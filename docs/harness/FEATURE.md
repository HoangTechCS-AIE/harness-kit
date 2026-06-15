<!--
FEATURE.md — spec một feature TRƯỚC khi viết code (spec-driven development).

Đây là nửa "Specs" của trụ cột "Repo-local instructions & Specs": CLAUDE.md (Mức 1) lo luật bền
xuyên MỌI task; FEATURE.md lo định nghĩa MỘT feature cụ thể trước khi bắt tay. Spec rõ → agent
chạy đúng hướng, ít lạc; acceptance criteria rõ → có cái để eval (Mức 5) chấm đậu/rớt.

Cách dùng: copy cho mỗi feature đáng-kể (vd docs/specs/<feature>.md). Việc nhỏ thì bỏ qua —
đừng nghi thức hoá. Điền đủ phần, xoá comment này khi dùng thật.
-->

# Feature: <tên ngắn gọn>

## Vấn đề / vì sao
<Giải quyết cái gì cho ai. 1–3 câu. Nếu không nói rõ được "vì sao", khoan code.>

## Phạm vi

### Trong phạm vi
- 

### NGOÀI phạm vi (quan trọng — chặn scope creep)
- 

## Ràng buộc
<Bắt buộc kỹ thuật/nghiệp vụ: API phải giữ nguyên, không thêm dependency, giới hạn hiệu năng…>
- 

## Acceptance criteria (đo được — đậu/rớt rõ ràng)
<Cái PHẢI đúng thì feature mới coi là xong. Đây cũng là nguồn cho golden task ở Mức 5.>
- [ ] 
- [ ] 

## Test hooks
<Sẽ kiểm bằng test nào / lệnh nào. Ưu tiên tự động hoá được.>
- 

## Ghi chú thiết kế & quyết định đã chốt
<Hướng tiếp cận + lý do ngắn. Để người sau (và agent) không bàn lại từ đầu.>
- 
