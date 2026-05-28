import redis_config.redis_client as redis_client

redis_client = redis_client.Redis(
    host="localhost",
    port=6379,
    decode_responses=True  
)