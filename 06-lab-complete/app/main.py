import time
import signal
import json
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import openai

from app.config import settings
from app.auth import verify_api_key
from app.rate_limiter import check_rate_limit, r as redis_client
from app.cost_guard import check_budget

# Cấu hình JSON Logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
)
logger = logging.getLogger(__name__)

# Trạng thái ứng dụng
START_TIME = time.time()
is_ready = False

# Khởi tạo OpenAI Client
openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

# Graceful shutdown handling
def handle_sigterm(*args):
    logger.info("Received SIGTERM - graceful shutdown in progress")

signal.signal(signal.SIGTERM, handle_sigterm)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global is_ready
    logger.info(json.dumps({"event": "startup", "app": settings.app_name}))
    # Simulate DB/Redis connection delay
    time.sleep(0.1)
    is_ready = True
    yield
    is_ready = False
    logger.info(json.dumps({"event": "shutdown"}))
    time.sleep(0.5) # Để các request hoàn thành

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Request Models
class AskRequest(BaseModel):
    user_id: str
    question: str

# Endpoints
@app.get("/health")
def health():
    """Liveness probe"""
    return {"status": "ok", "uptime_seconds": round(time.time() - START_TIME, 1)}

@app.get("/ready")
def ready():
    """Readiness probe"""
    if not is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    try:
        redis_client.ping()
    except Exception:
        raise HTTPException(status_code=503, detail="Redis connection failed")
    return {"status": "ready"}

@app.post("/ask")
async def ask_agent(
    body: AskRequest,
    _api_key: str = Depends(verify_api_key)
):
    """
    Endpoint chính để chat với Language Tutor Agent.
    Yêu cầu Header: X-API-Key
    """
    # 1. Rate Limiting
    check_rate_limit(body.user_id)
    
    # 2. Cost Guard (Ước lượng cơ bản)
    # Giả sử mỗi request trung bình tốn $0.001 (gpt-3.5-turbo input/output tokens)
    estimated_cost = 0.001
    check_budget(body.user_id, estimated_cost)
    
    # 3. Lấy lịch sử hội thoại từ Redis (Stateless design)
    history_key = f"chat_history:{body.user_id}"
    raw_history = redis_client.lrange(history_key, 0, -1)
    
    messages = [
        {"role": "system", "content": "You are a helpful Language & Translation Tutor. Please help the user translate text, understand grammar, or learn languages effectively."}
    ]
    
    for item in raw_history:
        messages.append(json.loads(item.decode("utf-8")))
        
    messages.append({"role": "user", "content": body.question})
    
    # 4. Gọi OpenAI
    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API Key is not configured")
        
    try:
        logger.info(json.dumps({"event": "calling_openai", "user_id": body.user_id}))
        response = await openai_client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            max_tokens=500
        )
        answer = response.choices[0].message.content
        
        # 5. Lưu lại lịch sử (chỉ giữ 10 tin nhắn gần nhất)
        redis_client.rpush(history_key, json.dumps({"role": "user", "content": body.question}))
        redis_client.rpush(history_key, json.dumps({"role": "assistant", "content": answer}))
        redis_client.ltrim(history_key, -10, -1)
        redis_client.expire(history_key, 3600) # Expire sau 1 tiếng
        
        return {
            "question": body.question,
            "answer": answer,
            "model": settings.llm_model
        }
    except Exception as e:
        logger.error(json.dumps({"event": "openai_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="Error communicating with LLM")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
