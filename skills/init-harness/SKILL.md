---
name: init-harness
description: Sinh file CLAUDE.md "đạt chuẩn harness engineering" cho một repo, thay cho /init mặc định. Phân tích codebase để điền WHAT/WHY/HOW (stack, build/test/run, kiến trúc, quy ước), rồi hỏi xác nhận đúng 2 phần không tự đoán được — Guardrails (ràng buộc hành vi agent) và Definition of Done (khi nào coi là xong) — những thứ /init bỏ sót. Tuân thủ kỷ luật của HumanLayer "Writing a good CLAUDE.md": ngắn (<300 dòng, lý tưởng ~60), pointer thay vì copy, không nhồi style/convention (để cho linter), craft thủ công chứ không auto-generate. Dùng skill này khi người dùng muốn tạo/chuẩn hóa CLAUDE.md, "init harness", thiết lập repo cho coding agent. Hiện chỉ làm CLAUDE.md (Claude Code); AGENTS.md/Codex sẽ bổ sung sau.
argument-hint: [đường dẫn repo, mặc định là thư mục hiện tại]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# init-harness — CLAUDE.md đạt chuẩn harness engineering

Sinh ra một `CLAUDE.md` là **repo-local instruction bền vững** mà Claude Code đọc trong *mọi*
session. Khác `/init` mặc định ở chỗ: `/init` chỉ **mô tả hiện trạng** repo (đây là gì, build ra sao);
skill này còn **quy định hành vi agent** (Guardrails + Definition of Done) và tuân thủ kỷ luật
quản lý context của nguồn chuẩn.

## Nguyên tắc nền (không được vi phạm)

Trích từ [Writing a good CLAUDE.md — HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md):

- **"LLMs are stateless functions"** — `CLAUDE.md` là file *duy nhất* nạp vào *mọi* session. Mọi dòng phải xứng đáng.
- **"Less is more"** — model theo được ~150–200 instruction; system prompt đã chiếm ~50. Giữ file **dưới 300 dòng, nhắm ~60–120**.
- **"Prefer pointers to copies"** — trỏ tới `path/file.ts:42`, KHÔNG copy snippet code vào file.
- **Không nhồi style/convention** — để linter/formatter lo. Đừng viết "dùng 2 space", "đặt tên camelCase".
- **Chỉ chứa cái universally relevant** — thông tin theo task cụ thể để riêng, link tới khi cần (progressive disclosure).
- **Right altitude — đừng hardcode luật cứng** — nguồn chuẩn cảnh báo HAI cực NGANG NHAU: quá mơ hồ *và* quá cứng ("overly complex hardcoded logic"). Viết heuristic/ranh giới ổn định, KHÔNG nhồi chuỗi if-this-then-that cho từng edge-case (làm `CLAUDE.md` giòn, mâu thuẫn, khó bảo trì). Quy tắc chỉ đúng trong một task cụ thể → đẩy ra file theo-task, đừng nhét vào `CLAUDE.md`.
- **Craft, đừng auto-dump** — nguồn chuẩn nói thẳng *don't auto-generate*. Skill này phân tích để *đề xuất*, nhưng phải chắt lọc, không đổ raw.
- **Viết cái KHÔNG hiển nhiên** — bỏ cây thư mục (agent tự khám phá), bỏ lời khuyên chung ("viết code sạch").

Hai phần làm nên "harness" (mà `/init` thiếu):
- **Guardrails** — agent *không được* làm gì, *phải* làm gì trước khi báo xong, thao tác nào cần xác nhận.
- **Definition of Done** — bằng chứng cụ thể (test pass, build xanh, lint sạch) để agent tự verify trước khi tuyên bố hoàn thành.

## Quy trình

### B1 — Xác định repo & quét hiện trạng

- Repo đích = `$ARGUMENTS` nếu có, ngược lại là thư mục hiện tại. Xác nhận là git repo (`git rev-parse --show-toplevel`).
- Nếu đã có `CLAUDE.md` → đọc, đề xuất *cải thiện* thay vì ghi đè mù. Hỏi trước khi overwrite.
- Gom nguồn sẵn có để hợp nhất (đừng để rải rác): `README.md`, `.cursorrules` / `.cursor/rules/`, `.github/copilot-instructions.md`, `AGENTS.md` nếu có.

### B2 — Suy ra WHAT / WHY / HOW (tự động, đậm đặc)

Phân tích codebase, KHÔNG hỏi những gì đoán được:

- **HOW (ưu tiên cao nhất — agent cần để chạy vòng lặp):**
  - Build / run / test / lint / typecheck — đọc từ `package.json` scripts, `Makefile`, `justfile`, `pyproject.toml`, `Cargo.toml`, `go.mod`, CI workflow…
  - **Lệnh chạy MỘT test đơn lẻ** — bắt buộc tìm cho ra (vd `pytest path::test_x`, `vitest run -t "name"`, `go test -run`). Đây là thứ tăng tốc feedback loop nhất.
  - Tool đặc thù: `bun` vs `node`, `uv` vs `pip`, package manager nào.
- **WHAT:** tech stack, ranh giới module, "map" codebase (đặc biệt quan trọng với monorepo). Mô tả *big picture cần đọc nhiều file mới hiểu*, KHÔNG liệt kê từng file.
- **WHY:** mục đích dự án, vai trò từng phần chính — 1–3 câu.

### B3 — Hỏi xác nhận ĐÚNG 2 phần không đoán được (gom 1 lượt duy nhất)

Dùng AskUserQuestion, gộp tất cả vào một lượt (tôn trọng context budget):

1. **Guardrails** — gợi ý ứng viên từ repo rồi nhờ xác nhận:
   - File/thư mục KHÔNG được sửa (generated, migrations đã chạy, lockfile, `dist/`, `vendor/`).
   - Thao tác cần xác nhận trước (chạy migration, xoá data, push, sửa CI/secrets).
   - Quy tắc bắt buộc ("luôn chạy test trước khi báo xong", "không thêm dependency mới nếu không hỏi").
2. **Definition of Done** — một thay đổi coi là xong khi nào? (vd: `<lệnh test>` xanh + `<lint>` sạch + `<typecheck>` pass). Đây là cái agent dùng để self-verify.

Nếu repo quá lớn / đa module → hỏi có muốn **phân tầng**: `CLAUDE.md` gọn ở root + file con cho module phức tạp (closest-file-wins). Mặc định: chỉ root.

### B4 — Viết CLAUDE.md theo khung

Bắt buộc mở đầu bằng:

```md
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
```

Khung nội dung (bỏ mục nào không có thực — đừng bịa):

```md
## Repo này là gì
<WHY + WHAT: 1–3 câu. Cái mà đọc 1 file không ra.>

## Build / Test / Run
- Build: <lệnh>
- Test toàn bộ: <lệnh>
- Chạy MỘT test: <lệnh cụ thể copy-paste chạy ngay>
- Lint / typecheck: <lệnh>
- Tool đặc thù: <bun/uv/...>

## Kiến trúc tổng quan
<Big picture cần đọc nhiều file mới hiểu: luồng chính, ranh giới module,
"trái tim" hệ thống nằm ở đâu. Dùng pointer path/file.ts:line, không copy code.>

## Quy ước riêng (chỉ cái KHÔNG hiển nhiên)
<Pattern bắt buộc mà agent không tự đoán. KHÔNG ghi style/format — để linter lo.>

## Guardrails
- KHÔNG sửa: <file/thư mục>.
- LUÔN <chạy test/lint> trước khi báo hoàn thành.
- Cần xác nhận trước khi: <thao tác nguy hiểm>.

## Definition of Done
Một thay đổi coi là xong khi: <bằng chứng cụ thể — test xanh, build ok, lint sạch>.
```

### B5 — Tự kiểm trước khi giao (self-check)

Đối chiếu file vừa viết với checklist, sửa nếu vi phạm:

- [ ] Dưới 300 dòng (lý tưởng <120). Nếu dài → cắt, đẩy chi tiết theo-task ra file riêng + link.
- [ ] Không có cây thư mục, không lời khuyên chung chung, không style/convention thừa.
- [ ] Dùng pointer (`path:line`) thay vì copy snippet.
- [ ] Có lệnh chạy MỘT test, copy-paste chạy được.
- [ ] Có mục Guardrails và Definition of Done (đây là phần làm nên "harness").
- [ ] Guardrails/Quy ước là heuristic ở mức ranh giới, KHÔNG phải chuỗi luật cứng/edge-case; luật chỉ đúng 1 task đã đẩy ra file theo-task.
- [ ] Mọi lệnh đã kiểm là tồn tại thật trong repo (đừng bịa script không có).

### B6 — Báo cáo

Tóm tắt cho người dùng: đã tạo/cập nhật file gì, đã hợp nhất nguồn nào (Cursor/Copilot/README), số dòng, và các Guardrails/DoD đã chốt. Nhắc: **AGENTS.md cho Codex sẽ làm ở đợt sau** (khi đó chỉ cần `ln -s AGENTS.md CLAUDE.md` để dùng chung một nguồn).

## Ngoài phạm vi (hiện tại)

- Không sinh `AGENTS.md` / không symlink — để dành đợt sau theo yêu cầu (focus Claude Code trước).
- Không thiết lập hooks/settings.json/MCP — đó là các trụ cột harness khác, làm riêng.
