import time
import redis
from fastapi import HTTPException
from app.config import settings

# Khởi tạo kết nối Redis
r = redis.from_url(settings.redis_url)

def check_rate_limit(user_id: str):
    """
    Sử dụng Sliding Window Logs trong Redis để đếm request.
    Giới hạn theo user_id.
    """
    now = time.time()
    key = f"rate_limit:{user_id}"
    
    # Xoá các request cũ hơn 60s
    r.zremrangebyscore(key, 0, now - 60)
    
    # Đếm số lượng request trong 60s qua
    request_count = r.zcard(key)
    
    if request_count >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {settings.rate_limit_per_minute} requests per minute."
        )
        
    # Thêm request mới vào ZSET
    r.zadd(key, {str(now): now})
    # Set expire để không rác DB (60s)
    r.expire(key, 60)
