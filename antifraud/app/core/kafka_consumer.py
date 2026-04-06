import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from antifraud.app.core.config import settings
from antifraud.app.core.db import SessionLocal
from antifraud.app.services.orchestrator import AntifraudOrchestrator
from antifraud.app.schemas.schemas import TransactionCreate

logger = logging.getLogger("antifraud_kafka")

async def consume():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_TRANSACTIONS,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        auto_offset_reset='earliest'
    )
    
    await consumer.start()
    logger.info("Kafka consumer started...")
    
    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode('utf-8'))
                transaction = TransactionCreate(**data)
                
                # Use orchestrator to process
                async with SessionLocal() as db:
                    orchestrator = AntifraudOrchestrator(db)
                    await orchestrator.process_transaction(transaction)
                    
            except Exception as e:
                logger.error(f"Error processing Kafka message: {e}")
                continue
    finally:
        await consumer.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(consume())
