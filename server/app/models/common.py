from datetime import datetime

from beanie import Document

class IdempotencyKey(Document):
    key: str
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "idempotency_keys"
        # Beanie creates indexes automatically during startup initialization
        indexes = [
            {"fields": ["key"], "unique": True},
            {"fields": ["created_at"], "expireAfterSeconds": 86400} # 24-hour TTL
        ]
