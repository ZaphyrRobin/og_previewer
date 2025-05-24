import os
import redis.asyncio as redis

# Redis client
REDIS_CLIENT = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Database url
# Please feel free to declare
# export DATABASE_URL="postgresql+asyncpg://<username>:<passpord>@localhost:5432/og_preview"
DATABASE_URL = os.getenv("DATABASE_URL")
