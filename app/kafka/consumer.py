# app/kafka/consumer.py
import json
import ssl
import os
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from typing import Callable, Dict, List
import logging

logger = logging.getLogger(__name__)

class KafkaConfig:
    """Configuration for Kafka SSL connection"""
    def __init__(self):
        self.kafka_url = os.environ.get('KAFKA_URL', '').replace('kafka+ssl://', '')
        self.cert = os.environ.get('KAFKA_CLIENT_CERT')
        self.key = os.environ.get('KAFKA_CLIENT_CERT_KEY')
        self.ca = os.environ.get('KAFKA_TRUSTED_CERT')
        
        # Write certificates to files for SSL context
        self._write_certs()
        
    def _write_certs(self):
        """Write certificates to temporary files"""
        if self.cert:
            with open("/tmp/kafka_client_cert.pem", "w+") as f:
                f.write(self.cert)
        if self.key:
            with open("/tmp/kafka_client_key.pem", "w+") as f:
                f.write(self.key)
        if self.ca:
            with open("/tmp/kafka_ca.pem", "w+") as f:
                f.write(self.ca)

    def get_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for Kafka connection"""
        ssl_context = ssl.create_default_context()
        ssl_context.load_cert_chain(
            "/tmp/kafka_client_cert.pem",
            "/tmp/kafka_client_key.pem"
        )
        ssl_context.load_verify_locations("/tmp/kafka_ca.pem")
        return ssl_context

class KafkaHandler:
    def __init__(self):
        self.config = KafkaConfig()
        self.consumer = None
        self.producer = None
        self.topic_handlers: Dict[str, List[Callable]] = {}

    def create_consumer(self, topics: List[str]):
        """Create Kafka consumer with SSL authentication"""
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.config.kafka_url,
            security_protocol='SSL',
            ssl_context=self.config.get_ssl_context(),
            group_id=os.environ.get('CONSUMER_GROUP'),
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

    def create_producer(self):
        """Create Kafka producer with SSL authentication"""
        self.producer = KafkaProducer(
            bootstrap_servers=self.config.kafka_url,
            security_protocol='SSL',
            ssl_context=self.config.get_ssl_context(),
            value_serializer=lambda m: json.dumps(m).encode('utf-8')
        )

    def register_handler(self, topic: str, handler: Callable):
        """Register a handler function for a specific topic"""
        if topic not in self.topic_handlers:
            self.topic_handlers[topic] = []
        self.topic_handlers[topic].append(handler)

    async def start_consuming(self):
        """Start consuming messages from Kafka"""
        try:
            for message in self.consumer:
                topic = message.topic
                if topic in self.topic_handlers:
                    for handler in self.topic_handlers[topic]:
                        try:
                            await handler(message.value)
                            self.consumer.commit()
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            # Handle error (retry, dead letter queue, etc.)
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
            # Implement reconnection logic here

    async def produce_message(self, topic: str, message: dict):
        """Produce a message to a Kafka topic"""
        try:
            future = self.producer.send(topic, message)
            await future
            logger.info(f"Message sent to topic {topic}")
        except Exception as e:
            logger.error(f"Error producing message: {e}")
            raise

# Example handler implementation
async def handle_salesforce_update(message: dict):
    """Handle updates from Salesforce"""
    try:
        # Process the Salesforce update
        record_type = message.get('type')
        record_id = message.get('id')
        fields = message.get('fields', {})
        
        # Implement your business logic here
        logger.info(f"Processing Salesforce {record_type} update for {record_id}")
        
        # Example: Update local database with Salesforce changes
        # await update_local_record(record_type, record_id, fields)
        
    except Exception as e:
        logger.error(f"Error handling Salesforce update: {e}")
        raise