# Observability — thấy agent đã làm gì (Mức 5)

Khi một eval rớt — hoặc agent "làm gì đó lạ" — bạn cần *nhìn* được nó đã làm gì, không đoán.
Đây là các chỗ mà nhìn, từ rẻ tới sâu.

## Chỗ nào mà nhìn

1. **Transcript phiên** — bản ghi *mọi* tool call agent đã gọi (đọc file nào, chạy lệnh gì,
   sửa gì). Đây là nguồn sự thật số một khi truy "vì sao nó làm vậy". Claude Code lưu transcript
   mỗi session dưới thư mục project trong `~/.claude/`.
2. **`/cost`** — token & chi phí của phiên. Tăng vọt bất thường = dấu hiệu context phình
   (đọc lại file thừa, MCP nhồi tool) → kéo về Mức 2.
3. **Telemetry (cho cả team / chạy nền)** — Claude Code xuất được metrics/logs qua OpenTelemetry:
   bật bằng biến môi trường `CLAUDE_CODE_ENABLE_TELEMETRY` rồi trỏ OTLP exporter sang backend
   của bạn (Grafana, Honeycomb, Datadog…). Dùng khi cần theo dõi nhiều phiên/agent, không chỉ một.
   → Tra cấu hình chính xác trong docs Claude Code mục *monitoring / telemetry*.
4. **Log hook (audit chủ động)** — gắn `PostToolUse` hook ghi mỗi tool call ra file (xem
   [guardrails/README.md](../guardrails/README.md) mục Hooks). Hữu ích khi chạy nền và muốn xem lại sau.

## Dấu hiệu bệnh & nó chỉ về mức nào

Observability không chỉ để debug một phiên — nó **lộ ra lỗ hổng harness**:

| Thấy gì trong trace | Bệnh | Sửa ở mức |
|---------------------|------|-----------|
| Đọc đi đọc lại cùng file; token leo thang | context bẩn | **Mức 2** (subagent / `/clear` / cắt MCP) |
| Bị hỏi quyền liên tục cho lệnh an toàn | allowlist thiếu | **Mức 3** (thêm vào `allow`) |
| Suýt chạy lệnh phá hoại | thiếu chốt | **Mức 3** (thêm vào `deny`/`ask`) |
| Mất ngữ cảnh giữa phiên dài, làm lại từ đầu | không checkpoint | **Mức 4** (`TASK.md`) |
| Làm sai mà không ai biết tới lúc muộn | thiếu eval | **Mức 5** (thêm golden task) |
| Mơ hồ "build/test chạy sao" | chỉ dẫn thiếu | **Mức 1** (CLAUDE.md) |
| Lặp đi lặp lại cùng một lỗi qua nhiều phiên | luật chưa được ghi | **Mức 1** (thêm 1 dòng vào CLAUDE.md) |

**Đóng vòng về Mức 1 — `CLAUDE.md` là tài liệu sống.** Khi trace cho thấy agent **lặp lại** một
lỗi Z (vd quên chạy migration, sửa nhầm file generated), đừng chỉ sửa tay lần này: thêm **một dòng**
guardrail/quy ước vào `CLAUDE.md` để chặn lần sau, rồi **chạy lại golden task** xác nhận hết
regression. Đó là cách `CLAUDE.md` lớn lên *từ lỗi thật*, thay vì phình theo phỏng đoán.

## Nguyên tắc

> Đừng cải thiện harness bằng cảm giác. **Đọc trace, để nó chỉ đúng mức cần sửa**, sửa, rồi
> chạy lại golden task để xác nhận tốt lên thật. Đó là toàn bộ vòng lặp Mức 5.
