import datetime
from fastapi import HTTPException
from app.rate_limiter import r
from app.config import settings

def check_budget(user_id: str, estimated_cost: float = 0.0) -> bool:
    """
    Theo dõi ngân sách sử dụng OpenAI theo tháng cho từng user_id trong Redis.
    Nếu user gọi request sẽ ước lượng cost và cộng dồn.
    """
    month_key = datetime.datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    current_spent = float(r.get(key) or 0.0)
    
    if current_spent + estimated_cost > settings.monthly_budget_usd:
        raise HTTPException(
            status_code=402,
            detail=f"Payment Required: Monthly budget of ${settings.monthly_budget_usd} exceeded."
        )
    
    if estimated_cost > 0:
        r.incrbyfloat(key, estimated_cost)
        # Giữ key trong 32 ngày
        r.expire(key, 32 * 24 * 3600)
        
    return True
