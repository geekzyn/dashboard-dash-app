import logging
import time
from urllib.parse import quote_plus
from typing import Any, Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from tenacity import retry, stop_after_attempt, wait_exponential


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Database:
    """
    MySQL database client using SQLAlchemy.
    
    Features:
    - Connection pooling
    - Automatic reconnection
    - Error handling and logging
    - Session management
    - Query execution with retries
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 1800, 
        connect_timeout: int = 10
    ):
        """
        Initialize the database client with connection parameters.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            username: Database username
            password: Database password
            pool_size: The number of connections to keep open
            max_overflow: The maximum number of connections to allow above pool_size
            pool_timeout: Seconds to wait before giving up on getting a connection
            pool_recycle: Seconds before connections are recycled
            connect_timeout: Seconds to wait for connection attempt
        """
        self.connection_url = (
            f"mysql+pymysql://{username}:{quote_plus(password)}@{host}:{port}/{database}"
            f"?charset=utf8mb4&connect_timeout={connect_timeout}"
        )
        
        self.engine = create_engine(
            self.connection_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,  # Enable connection health checks
        )
        
        self.SessionFactory = sessionmaker(bind=self.engine)
        logger.info(f"Database client initialized for {host}:{port}/{database}")
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions.
        Handles session cleanup and rollback on errors.
        
        Yields:
            SQLAlchemy Session object
        """
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {str(e)}")
            raise
        finally:
            session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def execute_query(self, query: str, params: Optional[dict] = None) -> list:
        """
        Execute a SQL query with retry logic.
        
        Args:
            query: SQL query string
            params: Optional dictionary of query parameters
            
        Returns:
            List of query results
            
        Raises:
            SQLAlchemyError: If query execution fails after retries
        """
        with self.get_session() as session:
            try:
                result = session.execute(text(query), params or {})
                return [dict(row) for row in result]
            except SQLAlchemyError as e:
                logger.error(f"Query execution error: {str(e)}")
                raise
    
    def close(self) -> None:
        """
        Properly close all database connections.
        """
        try:
            self.engine.dispose()
            logger.info("Database connections closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
