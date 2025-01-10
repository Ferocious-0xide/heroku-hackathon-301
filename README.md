# Heroku Hackathon 301 🚀

An enterprise-grade FastAPI template with Kafka event streaming and Salesforce integration via Heroku Connect.

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Architecture Overview 🏗️
Heads up, there are real costs associated with this template. If you decidee to build with this template, please be aware of the costs.

This template implements an event-driven architecture with three main components:

1. **FastAPI Web Application**
   - Handles HTTP requests
   - Produces events to Kafka
   - Provides API endpoints for Salesforce data

2. **Kafka Event Streaming**
   - Manages event flow between components
   - Handles high-throughput message processing
   - Provides reliable message delivery

3. **Salesforce Integration**
   - Bi-directional sync with Salesforce via Heroku Connect
   - Real-time updates using Kafka
   - Maintains data consistency across systems

## Prerequisites 📋

- Salesforce Developer Account or Enterprise Edition
- Heroku Enterprise Account (for Heroku Connect)
- Understanding of Kafka concepts
- PostgreSQL knowledge

## Quick Deploy 🚀

### 1. Set Up Heroku Resources
```bash
# Create app with enterprise addons
heroku create my-app
heroku addons:create heroku-postgresql:standard-0
heroku addons:create heroku-kafka:basic-0
heroku addons:create heroku-connect:demo
```

### 2. Configure Heroku Connect
```bash
# Open Heroku Connect dashboard
heroku addons:open heroku-connect

# Import mapping configuration
heroku connect:import config/salesforce_mapping.json
```

### 3. Set Up Kafka
```bash
# Create topics
heroku kafka:topics:create salesforce.contact
heroku kafka:topics:create salesforce.account

# Configure consumer groups
heroku kafka:consumer-groups:create sf-sync-group
```

## Local Development 💻

1. Set up Python environment:
```bash
pyenv install 3.11.5
pyenv local 3.11.5
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up local Kafka (using Docker):
```bash
docker-compose up -d kafka
docker-compose up -d zookeeper
```

4. Configure environment:
```bash
# Copy example env file
cp .env.example .env

# Update with your credentials
nano .env
```

## Kafka Integration 🔄

### Producing Messages

```python
from app.kafka.consumer import KafkaHandler

kafka = KafkaHandler()
kafka.create_producer()

# Produce message
await kafka.produce_message('salesforce.contact', {
    'id': 'SF123',
    'data': {
        'Email': 'user@example.com',
        'FirstName': 'John',
        'LastName': 'Doe'
    }
})
```

### Consuming Messages

```python
from app.workers.kafka_consumer import SalesforceKafkaWorker

worker = SalesforceKafkaWorker()
await worker.start()
```

## Salesforce Integration 🔌

### Heroku Connect Configuration

1. Map Salesforce Objects:
```json
{
  "Contact": {
    "access": "read_write",
    "sf_notify_enabled": true,
    "fields": ["Email", "FirstName", "LastName"]
  }
}
```

2. Set Up Sync:
```bash
# Check sync status
heroku connect:status

# Force sync
heroku connect:restart
```

### Using the Integration

```python
from app.salesforce.connect import HerokuConnect

# Initialize connection
sf_connect = HerokuConnect(db_session)

# Sync record
await sf_connect.sync_record(
    'Contact',
    'SF123',
    {'Email': 'user@example.com'}
)
```

## Deployment 🌍

### Production Configuration

1. Scale dynos appropriately:
```bash
heroku ps:scale web=2:standard-2x
heroku ps:scale worker=2:standard-2x
heroku ps:scale kafka-consumer=2:standard-1x
```

2. Configure Kafka SSL:
```bash
# Get Kafka credentials
heroku config:get KAFKA_URL
heroku config:get KAFKA_CLIENT_CERT
heroku config:get KAFKA_CLIENT_CERT_KEY
heroku config:get KAFKA_TRUSTED_CERT
```

### Monitoring

1. View Kafka metrics:
```bash
heroku kafka:metrics
```

2. Check consumer lag:
```bash
heroku kafka:consumer-groups:lag
```

## Troubleshooting 🔍

### Common Issues

1. Kafka Connection Issues:
```bash
# Check Kafka status
heroku kafka:info

# View Kafka logs
heroku logs --tail --app your-app-name
```

2. Salesforce Sync Issues:
```bash
# Check sync status
heroku connect:status

# View sync errors
heroku connect:errors
```

## Performance Tuning 🔧

### Kafka Optimization

1. Configure consumer settings:
```python
KAFKA_SETTINGS = {
    'max_poll_records': 500,
    'max_poll_interval_ms': 300000,
    'session_timeout_ms': 10000
}
```

2. Adjust topic partitions:
```bash
heroku kafka:topics:partitions salesforce.contact 3
```

### Database Optimization

1. Configure connection pooling:
```python
ENGINE_SETTINGS = {
    'pool_size': 5,
    'max_overflow': 10,
    'pool_timeout': 30
}
```

## Security Considerations 🔒

1. Kafka Security:
   - Always use SSL connections
   - Rotate certificates regularly
   - Monitor consumer group access

2. Salesforce Security:
   - Use field-level security
   - Implement proper OAuth flow
   - Monitor sync permissions

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Run tests: `pytest`
4. Submit a pull request

## Resources 📚

- [Heroku Kafka Documentation](https://devcenter.heroku.com/articles/kafka-on-heroku)
- [Heroku Connect Documentation](https://devcenter.heroku.com/articles/heroku-connect)
- [Salesforce API Documentation](https://developer.salesforce.com/docs/api-explorer)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)