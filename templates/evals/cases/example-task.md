<!--
Một "golden task" = một việc đại diện + tiêu chí đậu KHÁCH QUAN, để chạy lại được sau mỗi
lần sửa harness. Copy file này cho mỗi case. Đặt tên theo việc: add-endpoint.md, fix-flaky-test.md...

Nguyên tắc: done-criteria phải đo được bằng MÁY nếu có thể (lệnh chạy ra pass/fail), chỉ rớt
xuống chấm bằng người khi bất khả kháng. "Trông có vẻ đúng" KHÔNG phải tiêu chí.
Xoá comment này khi dùng thật.
-->

# Case: <tên việc — vd "thêm endpoint GET /users/:id">

## Task (đưa nguyên văn cho agent)
<Lời nhắc y như bạn sẽ gõ cho agent. Càng giống thực tế càng tốt.>

## Setup (repo phải ở trạng thái nào trước khi chạy)
<Branch/commit nền, dữ liệu seed, biến môi trường. Để case lặp lại được giống nhau mỗi lần.>
- Base: <commit/branch>
- 

## Done-criteria (KHÁCH QUAN — đậu/rớt rõ ràng)
<Cái PHẢI đúng sau khi agent xong. Ưu tiên lệnh chạy ra pass/fail.>
- [ ] `<lệnh test>` xanh
- [ ] `<lệnh lint / typecheck>` sạch
- [ ] <thay đổi cụ thể tồn tại — vd "route mới trả 200 với id hợp lệ, 404 nếu không">
- [ ] KHÔNG đụng <file/đường ngoài phạm vi>

## Cách chấm
<Tự động được thì ghi đúng lệnh. Phải chấm tay thì ghi rubric ngắn, đừng để "tự hiểu".>
- Tự động: `<lệnh trả exit code>`
- Tay (nếu cần): <1–2 câu rubric>

## Tham chiếu (tùy chọn)
<Commit/PR "đúng" để so, nếu có. Giúp thấy agent lệch ở đâu.>
