# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **API key hardcode:** Mật khẩu, key lưu trực tiếp trong code, dễ lộ trên Github.
2. **Không có Config Management:** Các thông số `DEBUG`, `DATABASE_URL` bị gán cứng.
3. **Sử dụng lệnh `print()` để log:** Ghi ra cả thông tin bảo mật và không có định dạng chuẩn.
4. **Thiếu Health Check Endpoint:** Platform (Cloud/Docker) không biết ứng dụng còn sống hay đã treo.
5. **Port và Host cố định:** Gắn cứng `localhost:8000`, sẽ không nhận được kết nối khi deploy lên Docker hay Cloud.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcode trong file | Env vars (Dùng Pydantic) | Bảo mật cao, linh hoạt deploy ở các môi trường khác nhau. |
| Health check | Không có | Có `/health` và `/ready` | Orchestrator/Load Balancer cần biết app có đang hoạt động tốt hay không để route traffic. |
| Logging | `print()` thường | Structured JSON logging | Dễ dàng parse, tìm kiếm và phân tích lỗi trên các hệ thống Log Aggregator (Datadog, Loki). |
| Shutdown | Đột ngột (Kill process) | Graceful Shutdown | Cho phép hoàn thành các requests đang xử lý dở trước khi đóng kết nối, giúp không mất data. |
| Host/Port| `localhost:8000` | `0.0.0.0`, port theo `PORT` env var | Bắt buộc để nhận traffic từ bên ngoài container / proxy của Cloud. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image:** `python:3.11` (Image đầy đủ, kích thước lớn).
2. **Working directory:** `/app`
3. **Tại sao COPY requirements.txt trước:** Để tận dụng cơ chế Layer Cache của Docker. Nếu requirements không đổi, Docker sẽ lấy cache cho lệnh `pip install`, tiết kiệm rất nhiều thời gian build.
4. **CMD vs ENTRYPOINT:** `CMD` dùng để chỉ định tham số/lệnh mặc định và rất dễ bị ghi đè (khi gọi `docker run`). `ENTRYPOINT` định nghĩa lệnh chính luôn luôn được chạy, thường được ưu tiên cho các container chạy như một file thực thi (executable).

### Exercise 2.3: Image size comparison
- Develop: ~1.15 GB (Dùng base image đầy đủ)
- Production: ~150 MB (Dùng multi-stage build với python slim)
- Difference: ~87% nhỏ hơn.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://aithucchienday12agentservice-production.up.railway.app
- Screenshot: `screenshots/railway_screenshot.png`

## Part 4: API Security

### Exercise 4.1-4.3: Test results
```bash
# Token generation
curl http://localhost:8000/auth/token -X POST   -H "Content-Type: application/json"   -d '{"username": "teacher", "password": "teach456"}' 
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZWFjaGVyIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzc2NDE4Njg3LCJleHAiOjE3NzY0MjIyODd9.SEtbOFTR_q3HRT3g_cfNVmcMeF16CTFWrUvvQXf_ouw","token_type":"bearer","expires_in_minutes":60,"hint":"Include in header: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."}

# API Call with JWT Token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZWFjaGVyIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzc2NDE4Njg3LCJleHAiOjE3NzY0MjIyODd9.SEtbOFTR_q3HRT3g_cfNVmcMeF16CTFWrUvvQXf_ouw"
curl http://localhost:8000/ask -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain JWT"}' 
{"question":"Explain JWT","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":99,"budget_remaining_usd":2.1e-05}}

# Rate Limit test
for i in {1..20}; do
  curl http://localhost:8000/ask -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"question": "Test '$i'"}'
  echo ""
done 
# (Log cho thấy request trừ dần `requests_remaining` và tăng `budget_remaining_usd`)
```

### Exercise 4.4: Cost guard implementation
Sử dụng Redis để theo dõi chi phí theo `user_id`. Key trong Redis được lưu dạng `budget:{user_id}:{YYYY-MM}`. Mỗi lần nhận request, ta ước tính chi phí và dùng lệnh `INCRBYFLOAT` để cộng dồn vào key đó. Nếu tổng vượt quá ngân sách (ví dụ $10), ứng dụng sẽ trả về lỗi HTTP 402 (Payment Required). Key có thiết lập tự động xoá sau hơn một tháng (khoảng 32 ngày) để tự động reset cho chu kì tháng mới.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **Health Checks:** Cài đặt endpoint `/health` trả về liveness (container chạy bình thường) và `/ready` trả về readiness (container đã kết nối thành công tới Redis). Load balancer sử dụng các endpoint này để định tuyến an toàn.
- **Graceful Shutdown:** Bắt tín hiệu `SIGTERM`. Báo cho Load Balancer ngừng gửi request mới và đợi các request đang chạy xử lý nốt trước khi đóng kết nối.
- **Stateless Design:** Chuyển `conversation_history` từ biến dictionary trong memory (RAM) lên Redis. Việc này đảm bảo khi scale lên 3-5 instances thì user vẫn giữ được lịch sử chat.
- **Load Balancing:** Khi dùng lệnh scale của Docker Compose, Nginx sẽ phân phối đều traffic (round-robin) qua các instances Agent. Nếu một container chết, traffic tự động chạy sang container khác và người dùng không bị rớt mạng.
