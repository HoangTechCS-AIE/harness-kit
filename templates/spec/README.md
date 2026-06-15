# Specs — spec-driven development (nửa còn lại của Trụ cột 2)

Trụ cột 2 là **"Repo-local instructions & Specs"**. Mức 1 (`/init-harness` → `CLAUDE.md`) lo nửa
**instructions**: luật bền, đúng xuyên *mọi* task. `FEATURE.md` lo nửa **specs**: định nghĩa **một
feature cụ thể TRƯỚC khi code**. Spec rõ → agent ít lạc hướng; acceptance criteria rõ → có sẵn cái
cho eval Mức 5 chấm đậu/rớt.

## Khi nào dùng

- Feature **đủ lớn để dễ lạc** / nhiều bước / nhiều người → viết spec trước.
- Việc nhỏ, một-phát-xong → **bỏ qua**. Đừng biến spec thành nghi thức.

## `FEATURE.md` vs `TASK.md` (đừng nhầm — chúng bổ sung nhau)

| | `FEATURE.md` (ở đây) | `TASK.md` (Mức 4) |
|---|---|---|
| Mục đích | **plan TRƯỚC khi code**: cái gì + tiêu chí đậu | **trạng thái sống còn QUA session** |
| Vòng đời | viết 1 lần đầu feature, ít đổi | cập nhật liên tục ở mỗi mốc |
| Trả lời | "feature này *là gì*, xong khi nào" | "*đang* làm tới đâu, bước kế" |

Feature lớn thường dùng **cả hai**: `FEATURE.md` chốt đích, `TASK.md` theo dõi đường đi.

## Cài

```bash
mkdir -p docs/specs
cp FEATURE.md docs/specs/<tên-feature>.md
```

## Nâng cao

Feature lớn / cả team → dùng framework chuyên: **GitHub Spec Kit**, **12-Factor Agents** (link
trong `docs/harness-engineering-tutorial.md`). `FEATURE.md` chỉ là bản tối giản để bắt đầu — đủ
để có spec, không bắt bạn nuốt cả framework.
