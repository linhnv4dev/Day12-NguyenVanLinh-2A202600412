from fastapi import Header, HTTPException
from app.config import settings

def verify_api_key(x_api_key: str = Header(...)):
    """Xác thực API key nội bộ để gọi Agent."""
    if x_api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key"
        )
    return x_api_key
