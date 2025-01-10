# app/salesforce/models.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from ..database import Base

class SalesforceSync(Base):
    """
    Model to track Salesforce synchronization status
    Maps to Heroku Connect sync table
    """
    __tablename__ = "salesforce_sync"

    id = Column(Integer, primary_key=True)
    sf_id = Column(String, unique=True, index=True)
    object_type = Column(String)
    sync_status = Column(String)
    last_sync = Column(DateTime)
    error_message = Column(String, nullable=True)
    raw_data = Column(JSON)

# app/salesforce/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class SalesforceSyncBase(BaseModel):
    sf_id: str
    object_type: str
    sync_status: str
    raw_data: Dict[str, Any]

class SalesforceSyncCreate(SalesforceSyncBase):
    pass

class SalesforceSync(SalesforceSyncBase):
    id: int
    last_sync: datetime
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

# app/salesforce/connect.py
import os
import json
import logging
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

logger = logging.getLogger(__name__)

class HerokuConnect:
    """
    Manages Heroku Connect synchronization with Salesforce
    """
    def __init__(self, db: Session):
        self.db = db
        self.schema = os.environ.get('HEROKU_CONNECT_SCHEMA', 'salesforce')
        
    async def sync_record(self, record_type: str, record_id: str, data: dict):
        """
        Synchronize a record with Salesforce through Heroku Connect
        """
        try:
            # Create sync record
            sync_record = models.SalesforceSync(
                sf_id=record_id,
                object_type=record_type,
                sync_status='pending',
                raw_data=data,
                last_sync=datetime.utcnow()
            )
            self.db.add(sync_record)
            
            # Execute sync through Heroku Connect mapped table
            table_name = f"{self.schema}.{record_type.lower()}"
            query = f"""
                INSERT INTO {table_name} 
                (_hc_lastop, _hc_err, {', '.join(data.keys())})
                VALUES 
                ('PENDING', NULL, {', '.join(['%s'] * len(data))})
            """
            await self.db.execute(query, list(data.values()))
            
            # Update sync status
            sync_record.sync_status = 'completed'
            self.db.commit()
            
            logger.info(f"Successfully synced {record_type} record {record_id}")
            
        except Exception as e:
            logger.error(f"Error syncing record: {e}")
            if sync_record:
                sync_record.sync_status = 'error'
                sync_record.error_message = str(e)
                self.db.commit()
            raise

    async def get_sync_status(self, record_id: str) -> schemas.SalesforceSync:
        """
        Get the synchronization status of a record
        """
        record = self.db.query(models.SalesforceSync).filter(
            models.SalesforceSync.sf_id == record_id
        ).first()
        
        if not record:
            return None
            
        return schemas.SalesforceSync.from_orm(record)

# app/salesforce/mapping.json
{
  "mappings": [
    {
      "object_name": "Contact",
      "config": {
        "access": "read_write",
        "sf_notify_enabled": true,
        "sf_polling_seconds": 600,
        "fields": {
          "Id": {},
          "Email": {},
          "FirstName": {},
          "LastName": {},
          "Phone": {},
          "MailingAddress": {}
        },
        "indexes": {
          "Id": {"unique": true},
          "Email": {"unique": true}
        }
      }
    },
    {
      "object_name": "Account",
      "config": {
        "access": "read_write",
        "sf_notify_enabled": true,
        "sf_polling_seconds": 600,
        "fields": {
          "Id": {},
          "Name": {},
          "Industry": {},
          "BillingAddress": {},
          "Phone": {}
        },
        "indexes": {
          "Id": {"unique": true}
        }
      }
    }
  ],
  "version": 1
}