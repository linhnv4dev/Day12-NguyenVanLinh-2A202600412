# Delivery Checklist — Day 12 Lab Submission

> **Student Name:** NGUYỄN VĂN LĨNH
> **Student ID:** 2A202600412
> **Date:** 17/04/2026

---

## Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. **API key hardcode:** Mật khẩu, key lưu trực tiếp trong code.
2. **Không có Config Management:** Các thông số `DEBUG`, `DATABASE_URL` bị gán cứng.
3. **Sử dụng lệnh `print()` để log:** Không có định dạng chuẩn.
4. **Thiếu Health Check Endpoint:** Platform không biết ứng dụng còn sống hay đã treo.
5. **Port và Host cố định:** Gắn cứng `localhost:8000`.

### Exercise 1.3: Comparison table

| Feature | Develop | Production | Why Important? |
| ------- | ------- | ---------- | -------------- |
| Config  | Hardcode trong file | Env vars (Dùng Pydantic) | Bảo mật cao, linh hoạt deploy ở các môi trường khác nhau. |
| Health check | Không có | Có `/health` và `/ready` | Orchestrator/Load Balancer cần biết app có đang hoạt động tốt hay không. |
| Logging | `print()` thường | Structured JSON logging | Dễ dàng parse, tìm kiếm và phân tích lỗi. |
| Shutdown | Đột ngột | Graceful Shutdown | Không mất data khi đóng kết nối. |
| Host/Port| `localhost:8000` | `0.0.0.0`, port theo `PORT` | Nhận traffic từ bên ngoài container / proxy của Cloud. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. Base image: `python:3.11`
2. Working directory: `/app`
3. Tại sao COPY requirements.txt trước: Để tận dụng cơ chế Layer Cache của Docker.
4. CMD vs ENTRYPOINT: `CMD` chỉ định tham số mặc định dễ bị ghi đè, `ENTRYPOINT` định nghĩa lệnh cố định.

### Exercise 2.3: Image size comparison

- Develop: ~1.15 GB
- Production: ~150 MB
- Difference: ~87% nhỏ hơn

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

- URL: https://language-tutor-service-production.up.railway.app
- Screenshot: [railway_screenshot.png](./railway_screenshot.png)

## Part 4: API Security

### Exercise 4.1-4.3: Test results

```json
{"question":"Test 1","answer":"Tôi là AI agent được deploy lên cloud...","usage":{"requests_remaining":98,"budget_remaining_usd":4e-05}}
```

### Exercise 4.4: Cost guard implementation

Sử dụng Redis để theo dõi chi phí theo `user_id`. Key trong Redis được lưu dạng `budget:{user_id}:{YYYY-MM}`. Mỗi lần nhận request, ta ước tính chi phí và dùng lệnh `INCRBYFLOAT` để cộng dồn vào key đó. Nếu tổng vượt quá ngân sách (ví dụ $10), trả về lỗi HTTP 402. Key có thiết lập expire 32 ngày để tự reset.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

- **Health Checks:** Cài đặt endpoint `/health` và `/ready`.
- **Graceful Shutdown:** Bắt tín hiệu `SIGTERM`. Báo cho Load Balancer ngừng gửi request mới.
- **Stateless Design:** Chuyển lịch sử chat từ biến dictionary trong memory (RAM) lên Redis.
- **Load Balancing:** Dùng Nginx phân phối traffic theo round-robin qua các instances Agent.
```

---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent with all files:

```
your-repo/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── auth.py              # Authentication
│   ├── rate_limiter.py      # Rate limiting
│   └── cost_guard.py        # Cost protection
├── utils/
│   └── mock_llm.py          # Mock LLM (provided)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore
├── railway.toml             # Railway config (or render.yaml)
└── README.md                # Setup instructions
```

**Requirements:**

- All code runs without errors
- Multi-stage Dockerfile (image < 500 MB)
- API key authentication
- Rate limiting (10 req/min)
- Cost guard ($10/month)
- Health + readiness checks
- Graceful shutdown
- Stateless design (Redis)
- No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

````markdown
# Deployment Information

## Public URL

https://language-tutor-service-production.up.railway.app

## Platform

Railway / Render / Cloud Run

## Test Commands

### Health Check

```bash
curl https://language-tutor-service-production.up.railway.app/health
# Expected: {"status": "ok"}
```
````

### API Test (with authentication)

```bash
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

## Screenshots

- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)

````

##  Pre-Submission Checklist

- [x] Repository is public (or instructor has access)
- [x] `MISSION_ANSWERS.md` completed with all exercises
- [x] `DEPLOYMENT.md` has working public URL
- [x] All source code in `app/` directory
- [x] `README.md` has clear setup instructions
- [x] No `.env` file committed (only `.env.example`)
- [x] No hardcoded secrets in code
- [x] Public URL is accessible and working
- [x] Screenshots included in `screenshots/` folder
- [x] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://language-tutor-service-production.up.railway.app/health

# 2. Authentication required
curl https://language-tutor-service-production.up.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://language-tutor-service-production.up.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do
  curl -H "X-API-Key: YOUR_KEY" https://language-tutor-service-production.up.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}';
done
# Should eventually return 429
````

---

## Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day12-agent-deployment
```

**Deadline:** 17/4/2026

---

## Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

## Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **
