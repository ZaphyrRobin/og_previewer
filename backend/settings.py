from dotenv import load_dotenv
load_dotenv()

import os
import redis.asyncio as redis

# Redis client
REDIS_CLIENT = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Database url
DATABASE_URL = os.getenv("DATABASE_URL")
