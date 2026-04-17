# Deployment Information

## Public URL
https://language-tutor-service-production.up.railway.app

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://language-tutor-service-production.up.railway.app/health
# Expected: {"status": "ok", ...}
```

### API Test (with authentication)
```bash
# Lấy API Key từ cài đặt biến môi trường
curl -X POST https://language-tutor-service-production.up.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL
- OPENAI_API_KEY
- RATE_LIMIT_PER_MINUTE
- MONTHLY_BUDGET_USD

## Screenshots
- [Deployment dashboard / Service running](./railway_screenshot2.png)
