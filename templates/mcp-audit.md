# MCP hygiene — checklist dọn tool thừa (Mức 2)

Mỗi MCP server bạn cắm sẽ **bơm toàn bộ định nghĩa tool của nó vào context ở MỌI lượt** —
dù lượt đó không dùng tới. 5 server ít dùng có thể ngốn hàng nghìn token mỗi lượt và làm
model "rối tay" khi chọn tool. Đây là **thuế context vĩnh viễn**, không phải vấn đề an toàn
(an toàn là Mức 3).

## Cách xem đang cắm những gì

```bash
claude mcp list        # liệt kê MCP server đang cấu hình
```

## Với MỖI server, hỏi 3 câu

- [ ] **Tháng qua có thực sự gọi tool của nó không?** Không → gỡ.
- [ ] **Nó thêm bao nhiêu tool vào mỗi lượt, mà bạn chỉ dùng 1–2?** Thừa nhiều → gỡ hoặc tìm bản gọn hơn.
- [ ] **Có thể thay bằng CLI sẵn có không?** (vd `gh` thay vì MCP GitHub cho việc đơn giản) → ưu tiên CLI, gỡ MCP.

## Nguyên tắc

> **Tool ít mà rõ > nhiều tool chồng chéo.** Giữ đúng cái bạn dùng hằng tuần.
> Cắm thêm khi *thật sự* cần một nguồn/khả năng mới, không cắm "để sẵn cho chắc".

Cắm MCP "để sẵn cho chắc" là cái bẫy phổ biến nhất ở Mức 2: nó âm thầm làm mọi session
đắt hơn và kém chính xác hơn, mà không ai để ý.
