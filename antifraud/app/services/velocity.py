import time
import redis
from antifraud.app.core.config import settings
from antifraud.app.schemas.schemas import TransactionCreate

class VelocityCheckService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def add_transaction(self, transaction: TransactionCreate):
        """Adds a transaction to multiple velocity windows."""
        now = time.time()
        user_key = f"velocity:user:{transaction.user_id}"
        device_key = f"velocity:device:{transaction.device_id}"
        
        pipeline = self.redis_client.pipeline()
        pipeline.zadd(user_key, {str(now): now})
        pipeline.zadd(device_key, {str(now): now})
        
        # Track multiple cards on same device
        pipeline.sadd(f"device_cards:{transaction.device_id}", transaction.sender_card)
        pipeline.expire(f"device_cards:{transaction.device_id}", 3600) # 1 hour
        
        # Track same card sending to multiple receivers
        pipeline.sadd(f"card_receivers:{transaction.sender_card}", transaction.receiver_card)
        pipeline.expire(f"card_receivers:{transaction.sender_card}", 3600)

        # Amount tracking
        amount_key = f"velocity_amount:user:{transaction.user_id}"
        member = f"{now}:{transaction.amount}"
        pipeline.zadd(amount_key, {member: now})
        pipeline.expire(amount_key, 2400)
        
        pipeline.expire(user_key, 2400)
        pipeline.expire(device_key, 2400)
        pipeline.execute()

    def get_count(self, key_prefix: str, identifier: str, window_seconds: int) -> int:
        """Returns the number of transactions in the given window."""
        key = f"velocity:{key_prefix}:{identifier}"
        now = time.time()
        start_time = now - window_seconds
        
        # Remove old entries
        self.redis_client.zremrangebyscore(key, 0, start_time)
        
        # Count current entries
        return self.redis_client.zcard(key)

    def get_total_amount(self, key_prefix: str, identifier: str, window_seconds: int) -> float:
        """Returns the total amount in the given window (simplified approach)."""
        # For a production-grade amount check, we'd store timestamps and amounts
        # In this implementation, we'll use a slightly different key structure or aggregate
        # For brevity, let's assume we store (timestamp, amount) in a list or specialized structure
        # A better way for amounts in Redis sliding window is using buckets or storing amount in score (if unique)
        # Here we'll use a simpler bucketed approach for the last 30 minutes
        
        # Simplified: sum of values in the window
        # In a real system, we'd use Redis Stack (RedisTimeSeries) or a more complex script
        # Let's use a simple ZRANGE and sum if we stored amount in the member string "timestamp:amount"
        key = f"velocity_amount:{key_prefix}:{identifier}"
        now = time.time()
        start_time = now - window_seconds
        
        self.redis_client.zremrangebyscore(key, 0, start_time)
        entries = self.redis_client.zrangebyscore(key, start_time, now)
        
        total = 0.0
        for entry in entries:
            try:
                total += float(entry.split(":")[1])
            except (IndexError, ValueError):
                continue
        return total

    def add_transaction_with_amount(self, key_prefix: str, identifier: str, amount: float):
        key = f"velocity_amount:{key_prefix}:{identifier}"
        now = time.time()
        member = f"{now}:{amount}"
    def get_unique_cards_on_device(self, device_id: str) -> int:
        return self.redis_client.scard(f"device_cards:{device_id}")

    def get_unique_receivers_for_card(self, sender_card: str) -> int:
        return self.redis_client.scard(f"card_receivers:{sender_card}")

    def track_failed_attempt(self, user_id: str):
        key = f"failed_attempts:user:{user_id}"
        self.redis_client.incr(key)
        self.redis_client.expire(key, 86400) # 24 hours

    def get_failed_attempts(self, user_id: str) -> int:
        val = self.redis_client.get(f"failed_attempts:user:{user_id}")
        return int(val) if val else 0
