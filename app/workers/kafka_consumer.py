# app/workers/kafka_consumer.py
import asyncio
import logging
from ..kafka.consumer import KafkaHandler
from ..salesforce.connect import HerokuConnect
from ..database import SessionLocal

logger = logging.getLogger(__name__)

class SalesforceKafkaWorker:
    def __init__(self):
        self.kafka = KafkaHandler()
        self.db = SessionLocal()
        self.sf_connect = HerokuConnect(self.db)
        
    async def handle_contact_update(self, message: dict):
        """Handle Contact updates from Kafka"""
        try:
            contact_id = message.get('id')
            contact_data = message.get('data', {})
            
            # Sync with Salesforce
            await self.sf_connect.sync_record(
                'Contact',
                contact_id,
                contact_data
            )
            
            logger.info(f"Successfully processed Contact update for {contact_id}")
            
        except Exception as e:
            logger.error(f"Error processing Contact update: {e}")
            # Implement error handling (retry queue, dead letter queue, etc.)
    
    async def handle_account_update(self, message: dict):
        """Handle Account updates from Kafka"""
        try:
            account_id = message.get('id')
            account_data = message.get('data', {})
            
            # Sync with Salesforce
            await self.sf_connect.sync_record(
                'Account',
                account_id,
                account_data
            )
            
            logger.info(f"Successfully processed Account update for {account_id}")
            
        except Exception as e:
            logger.error(f"Error processing Account update: {e}")

    async def start(self):
        """Start the Kafka consumer worker"""
        try:
            # Set up Kafka consumer for relevant topics
            self.kafka.create_consumer(['salesforce.contact', 'salesforce.account'])
            
            # Register handlers for each topic
            self.kafka.register_handler('salesforce.contact', self.handle_contact_update)
            self.kafka.register_handler('salesforce.account', self.handle_account_update)
            
            # Start consuming messages
            await self.kafka.start_consuming()
            
        except Exception as e:
            logger.error(f"Error in Kafka consumer worker: {e}")
            raise

# app/workers/cli.py
"""CLI entry point for worker processes"""
import asyncio
import click
from .kafka_consumer import SalesforceKafkaWorker

@click.command()
def run_worker():
    """Run the Kafka consumer worker"""
    worker = SalesforceKafkaWorker()
    asyncio.run(worker.start())

if __name__ == '__main__':
    run_worker()