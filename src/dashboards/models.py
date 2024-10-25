from sqlalchemy import Column, BigInteger, Float, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AzureCosts(Base):
    __tablename__ = 'azure_costs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cost = Column(Float)
    date = Column(Date)
    service = Column(String(512))
    resource_group = Column(String(90))
    currency = Column(String(3))
    subscription_id = Column(String(36))
    subscription = Column(String(64))
    application = Column(String(64))
    environment = Column(String(64))
    cluster = Column(String(64))

