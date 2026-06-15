# Long-running — việc kéo dài quá một session (Mức 4)

Mức 4 giữ agent làm việc *đáng tin* trên thứ dài hơi: refactor nhiều ngày, migration lớn,
agent chạy nền hàng giờ. Việc dài chết vì 3 thứ — mỗi file ở đây chặn một thứ.

## 3 file, 3 vấn đề

| File | Chặn cái chết nào |
|------|-------------------|
| [`setup.sh`](../setup.sh) | Không về được trạng thái chạy-được (clone/agent mới không biết cài gì) |
| [`TASK.md`](./TASK.md) | Mất trạng thái qua session / sau `/clear` |
| [`new-worktree.sh`](../new-worktree.sh) | Nhiều task song song giẫm chân nhau |

## Cài đặt

```bash
cp setup.sh new-worktree.sh .          # vào root repo
chmod +x setup.sh new-worktree.sh
cp long-running/TASK.md .              # khi bắt đầu một việc dài cụ thể
```

Rồi **trỏ `CLAUDE.md`** vào chúng để agent biết dùng:

```md
## Build / Test / Run
- Dựng môi trường: ./setup.sh   (idempotent — chạy lại an toàn)

## Long-running
- Việc dài đang chạy ghi ở TASK.md — đọc trước khi bắt đầu, cập nhật khi tới mốc.
```

## Khi nào dùng cái nào (đây là phần discipline)

File chỉ là công cụ — biết *khi nào* rút ra mới là kỹ năng:

- **`setup.sh`** — chạy ngay khi vào checkout mới, và bất cứ khi nào nghi môi trường lệch.
  Giữ nó **idempotent + fail-fast**: agent nền phải dựng lại được mà không cần hỏi.
- **`TASK.md`** — mở ra khi việc *sẽ vắt qua nhiều session* hoặc bạn sắp `/clear`. Cập nhật ở
  **mốc** (xong một phần, chốt một quyết định), không phải mỗi dòng code. Nó là thứ agent kế
  tiếp đọc để tiếp tục — viết cho "người lạ" hiểu, không viết tốc ký cho riêng mình.
- **`new-worktree.sh`** — tách worktree khi chạy **≥2 hướng song song**, hoặc khi một task dài
  cần cô lập khỏi nhánh chính. Một task = một worktree. Xong: `git worktree remove <dir>`.

## Chạy nền & quay lại kiểm

Việc thật dài có thể chạy ở background rồi quay lại xem (không ngồi canh). Nguyên tắc:
khúc việc phải **resume được** — nếu đứt giữa chừng, `TASK.md` + `setup.sh` đủ để bắt lại từ
mốc gần nhất, không phải làm lại từ đầu. Đó là lý do hai file kia tồn tại.
