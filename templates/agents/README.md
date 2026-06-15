# Subagents — quy tắc viết đúng (Mức 2)

Subagent là **đòn bẩy chính của Mức 2**: đẩy việc nặng (đọc nhiều file, refactor lớn,
chạy thử lặp) sang một **context riêng**, để context chính chỉ nhận *kết luận* — không bị ngập.

## Cài đặt

Mỗi subagent là một file `.md` trong `.claude/agents/` (cấp repo) hoặc `~/.claude/agents/` (cấp user).
Copy file mẫu vào đó là Claude Code tự nhận:

```bash
mkdir -p .claude/agents
cp repo-explorer.md .claude/agents/
```

## Cấu trúc file

```md
---
name: <kebab-case>
description: <KHI NÀO dùng — Claude đọc dòng này để tự quyết có gọi agent này không>
tools: Read, Grep, Glob        # (tuỳ chọn) chỉ trang bị tool agent CẦN, để nó gọn
---
<system prompt: vai trò + cách làm + ĐẶC BIỆT là cách TRẢ VỀ>
```

## 4 quy tắc không được quên

1. **`description` viết theo "khi nào dùng", không phải "là gì".** Đây là thứ agent chính
   đọc để quyết định có ủy thác hay không. Mơ hồ → không bao giờ được gọi.
2. **Subagent phải trả về *kết luận chắt lọc*, không phải nhật ký.** Cả lý do tồn tại của
   subagent là để context chính KHÔNG phải nuốt thứ nó đọc. Trả raw dump = phá mục tiêu.
3. **`tools` chỉ liệt kê cái thật cần.** Đây KHÔNG phải guardrail an toàn (đó là Mức 3) —
   mà để agent gọn, tập trung. Agent đọc-hiểu chỉ cần `Read, Grep, Glob`.
4. **Một subagent = một việc rõ.** Đừng gộp "đọc + sửa + test" vào một agent. Việc nặng
   khác nhau → context riêng khác nhau.

## Khi nào KHÔNG cần viết subagent mới

Claude Code đã có sẵn `Explore` (quét read-only), `Plan` (thiết kế), `general-purpose`.
Chúng lo phần lớn nhu cầu cô lập context rồi. **Chỉ viết subagent riêng khi** bạn có một
việc lặp lại, đặc thù domain mà built-in không nắm được — đừng đẻ bản generic trùng lặp,
vì chính tool thừa là cái nhiễu context mà Mức 2 dạy phải tránh.
