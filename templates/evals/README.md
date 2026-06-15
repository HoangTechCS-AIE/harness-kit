# Evals & Observability — đo agent có làm đúng không (Mức 5)

Mức 1–4 *dựng* harness. Mức 5 là **vòng phản hồi**: làm sao biết khi bạn sửa CLAUDE.md /
settings / skill thì agent **tốt lên hay tệ đi**? Không có Mức 5, mọi thay đổi harness chỉ là đoán.

## Hai nửa

| Nửa | Trả lời | File |
|-----|---------|------|
| **Evals** | "Agent ra kết quả *đúng* không?" (pass/fail đo được) | [`cases/`](./cases/) |
| **Observability** | "Agent đã *làm gì*, vì sao hỏng?" | [`observability.md`](./observability.md) |

Evals nói **đúng/sai**. Observability nói **tại sao** — và thường lộ bệnh ở mức thấp hơn
(đọc lại file hoài = context bẩn → Mức 2; hỏi quyền liên tục → chỉnh `allow` ở Mức 3).

## Vòng lặp (đây mới là cốt lõi, không phải file)

```
define  →  run  →  read  →  fix  →  (chạy lại)
golden     cho       đọc      sửa
task       agent     trace    harness
           chạy      / kết    (CLAUDE.md,
                     quả      settings, skill)
```

Đòn bẩy thật: bộ golden task là **lưới chống regression cho chính harness**. Sửa CLAUDE.md xong,
chạy lại bộ case — case trước đậu mà giờ rớt → gần như chắc chắn do thay đổi của mình (xác nhận
bằng cách chạy lại vài lần để loại nhiễu), không phải đoán.

## Sự thật: Mức 5 ít "gói thành file" nhất

Eval *thật* thì **đặc thù domain** — không kit nào ship sẵn "agent của bạn làm đúng chưa".
Kit này chỉ cho **khung + kỷ luật**:

- ✅ File: cấu trúc thư mục + template golden-task + guide observability.
- 🧠 Discipline (phần lớn): *định nghĩa* "đúng" cho task của bạn, dựng bộ case, đọc trace,
  **đóng vòng lặp** (eval phát hiện regression → sửa harness → chạy lại).

Kit cố ý **không** ship runner code — runner là đặc thù repo, giả vờ generic sẽ thành rác.

## Bắt đầu

1. Copy `cases/example-task.md` thành một case thật, điền done-criteria *khách quan*.
2. Gom 3–5 task **đại diện** (việc agent làm thường xuyên nhất) — không cần nhiều, cần đúng.
3. **Lấy baseline "không harness" TRƯỚC.** Chạy bộ case một lần ở trạng thái chưa áp harness
   (CLAUDE.md trống / trước khi cài Mức 1–4) và ghi điểm. Đây là cái **định lượng ROI của harness**:
   chạy lại sau khi đã áp harness rồi so delta — chính là luận điểm mở đầu của ngành (đổi harness
   làm điểm nhảy; xem `docs/harness-engineering-tutorial.md`). *Khác* với regression ở bước sau.
4. Sau đó, trước/sau **mỗi lần sửa** harness, chạy lại bộ case và đối chiếu (chạy vài lần để loại
   nhiễu trước khi kết luận nhân-quả).
5. Khi một case rớt, mở [`observability.md`](./observability.md) để truy *vì sao*.
