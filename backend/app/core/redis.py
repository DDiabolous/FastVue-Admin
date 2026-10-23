"""延迟初始化共享 Redis 连接池；由应用 lifespan 关闭。"""

from fastapi import HTTPException, Request
from redis.asyncio import Redis


async def get_redis(request: Request) -> Redis:
    config = request.app.state.config
    if not config.redis_url:
        raise HTTPException(503, '认证缓存未配置')
    client = getattr(request.app.state, 'redis', None)
    if client is None:
        client = Redis.from_url(
            config.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=3,
            health_check_interval=30,
            max_connections=50,
        )
        request.app.state.redis = client
    return client
