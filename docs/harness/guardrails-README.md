# Guardrails — permission baseline (Mức 3)

Mức 3 kiểm soát agent **được phép làm gì** — ranh giới an toàn. Khác Mức 2 (context *sạch*),
Mức 3 lo hành động *an toàn*: chặn lệnh phá hoại, hỏi trước việc rủi ro, cho việc an toàn chạy thẳng.

## Cài đặt

Copy `settings.json` vào `.claude/` của repo:

```bash
mkdir -p .claude
cp settings.json .claude/settings.json
```

**Vì sao là `.claude/settings.json` (không phải `settings.local.json`):** file này **check vào repo**,
nên cả team clone về là **tự thừa hưởng cùng một bộ guardrail**. Còn `settings.local.json` là
ghi đè cá nhân (đã gitignore) — để dành cho tinh chỉnh riêng máy bạn, không ép lên team.

> ⚡ **Việc ĐẦU TIÊN sau khi copy — thêm lệnh test/lint/build vào `allow`.** Baseline cố ý chỉ
> allow git read-only. Nếu không thêm vòng feedback của repo, Claude sẽ hỏi quyền *mỗi lần* chạy
> test → bạn rơi đúng thói quen "bấm yes cho xong" mà mục *Insight* bên dưới gọi là nguy hiểm nhất.
> Mở `.claude/settings.json`, thêm vào `allow` đúng lệnh của stack bạn:
>
> - **Node:** `"Bash(npm run test:*)"`, `"Bash(npm run lint:*)"`, `"Bash(npm run build:*)"`
> - **Python:** `"Bash(pytest:*)"`, `"Bash(ruff:*)"`, `"Bash(mypy:*)"`
> - **Go:** `"Bash(go test:*)"`, `"Bash(go build:*)"`, `"Bash(go vet:*)"`
>
> Đây là **bắt buộc**, không phải tuỳ chọn — vòng feedback nhanh là tinh tuý xuyên suốt cả kit.

## Mô hình 3 rổ

Mọi hành động (chạy bash, đọc/sửa file) rơi vào 1 trong 3 rổ:

| Rổ | Nghĩa | Ví dụ trong baseline |
|----|-------|----------------------|
| **deny** | cấm tuyệt đối, agent không gọi được | `rm -rf`, đọc `.env`/`secrets/**`, đọc key `*.pem` |
| **ask** | dừng lại hỏi bạn trước | `git push`, `git reset --hard`, `git clean`, `rm` |
| **allow** | chạy thẳng, không hỏi | `git status`, `git diff`, `git log`, `git branch` |

Cú pháp rule: `Tool(specifier)`.
- Bash khớp theo **tiền tố**: `Bash(npm run test:*)` khớp mọi lệnh bắt đầu bằng `npm run test`.
- File theo kiểu **gitignore**: `Read(./secrets/**)`, `Edit(./dist/**)`.

## Cách mở rộng cho repo của bạn

Baseline cố ý **tối giản và universal**. Hãy thêm cái đặc thù repo:

- **Vào `allow`** — lệnh chạy hằng ngày, an toàn, để khỏi bị hỏi liên tục:
  `Bash(npm run test:*)`, `Bash(npm run lint:*)`, `Bash(pytest:*)`, `Bash(make:*)`.
- **Vào `ask`** — việc đặc thù repo mà *hệ quả lớn*:
  chạy migration (`Bash(npm run migrate:*)`), deploy, `Bash(docker compose down:*)`.
- **Vào `deny`** — path không bao giờ được sửa/đọc:
  `Edit(./dist/**)`, `Edit(./vendor/**)`, `Read(./**/*.key)`.

> Mẹo: đừng nhồi `allow` quá rộng. Mỗi lần Claude hỏi là một lần bạn *review* — nhồi allow
> nhiều quá là tự bỏ chốt review của chính mình.

## Insight: deny ≠ bảo mật kín kẽ

Deny-list **không** chống được kẻ địch (agent có thể lách: viết `rm` qua script, base64…).
Nó là **lưới an toàn + giảm ma sát**:
- `deny`/`ask` chặn **tai nạn** (xoá nhầm, push nhầm) — phòng *lỗi*, không phòng *tấn công*.
- `allow` cho lệnh an toàn chạy thẳng → bạn đỡ thói quen "bấm yes cho xong" (thói quen đó mới
  là cái nguy hiểm thật).

**An toàn thật sự** vẫn là **review diff + plan mode** trước khi cho agent hành động — đó là
kỷ luật runtime, không gói thành file được.

## Nội dung ngoài & prompt injection

`deny`/`ask` ở trên chặn *tai nạn*, **không** chặn được prompt injection. Nội dung agent đọc từ
web, issue, PR, log… là **dữ liệu — không phải lệnh**, nhưng kẻ xấu có thể giấu chỉ thị trong đó
để lái agent. Đây là **kỷ luật runtime** (nên kit không nhồi hook/CI-scan sẵn), vài chốt thực dụng:

- Đọc nội dung ngoài (web/issue/PR) trong **plan mode** — agent *đề xuất* trước khi *hành động*.
- KHÔNG cho agent tự chạy lệnh / `curl` lấy ra từ nội dung nó vừa fetch về.
- Input không tin cậy → tách **session riêng**, đừng trộn vào session đang có quyền cao.

Quét tự động ở CI và phần nền sâu hơn: xem `docs/harness-engineering-tutorial.md` (link **Lurkr**
cho CI-scan, **OpenHands — mitigating prompt injection** cho nền tảng).

## Nâng cao (tùy chọn): Hooks

Khi cần *logic* phức tạp hơn allow/deny tĩnh — vd "chặn mọi edit vào path bảo vệ", "tự chạy
lint sau mỗi lần sửa" — dùng **hook**: một script chạy *trước/sau* mỗi tool call. Khai báo trong
`settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": ".claude/hooks/guard.sh" }] }
    ]
  }
}
```

Script đọc JSON tool-call từ stdin; **exit code 2 = chặn**, kèm message ra stderr. Vì hook chặn
là script đặc thù từng repo, kit này **không nhồi sẵn** — chỉ chỉ đường. Viết khi bạn thật sự có
một quy tắc lặp lại mà allow/deny tĩnh không diễn đạt nổi.

**Audit-log (`PostToolUse`)** — ghi lại *mọi* tool call để xem lại sau. Đây là thứ
`evals/observability.md` (Mức 5) trỏ tới; hook này **generic, không đặc thù repo**:

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": ".claude/hooks/audit-log.sh" }] }
    ]
  }
}
```

`audit-log.sh` chỉ cần nối payload stdin vào một file — mỗi dòng là JSON một tool call:

```bash
#!/usr/bin/env bash
cat >> .claude/audit.log
```
