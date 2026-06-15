# harness-kit

> Thiết lập một repo cho coding agent (Claude Code) theo **5 mức trưởng thành** của harness
> engineering — bằng một lệnh.

**Harness** = mọi thứ *bao quanh* model (context, chỉ dẫn, tools, ràng buộc an toàn, orchestration,
đo lường) để agent làm việc đáng tin. Kit này đóng gói nó thành **artifact** cài được + một
**tutorial** dạy *khi nào* dùng từng thứ. Kit ship file; tutorial dạy kỷ luật.

## Cài nhanh

```bash
npx harness-kit              # hỏi chọn mức rồi cài
npx harness-kit --all        # cài cả 5 mức
npx harness-kit --levels=1,3 # chỉ mức cụ thể
```

Cần **Node ≥18**. Lệnh đổ artifact vào đúng chỗ (`.claude/`, root repo, `~/.claude/skills/`) và lưu
toàn bộ tài liệu vào `docs/harness/` để team giữ lại. **Idempotent** — chạy lại an toàn (`--force`
để ghi đè). Muốn cài tay để hiểu từng mức? Xem lệnh `cp` ở mỗi mức bên dưới — installer chỉ tự động
hoá đúng những lệnh đó.

## Trong kit có gì — mỗi mức chặn một kiểu thất bại

| Mức | Khi không có nó | Artifact |
|-----|-----------------|----------|
| **1 — Nền tảng** | agent không có chỉ dẫn repo bền vững | skill `/init-harness` → sinh `CLAUDE.md` |
| **2 — Context sạch** | context ngập, agent "loãng" sự chú ý | subagent mẫu + checklist rà MCP |
| **3 — Guardrails** | agent xoá/push nhầm, bị hỏi quyền liên tục | `settings.json` (deny/ask/allow) |
| **4 — Long-running** | việc dài đứt giữa chừng, không resume | `setup.sh`, `new-worktree.sh`, `TASK.md` |
| **5 — Evals & Obs** | không biết agent làm tốt hay tệ | golden-task template + guide observability |

## 5 mức (chi tiết + cài tay)

### Mức 1 — Nền tảng · `CLAUDE.md` &nbsp;`[làm trước tiên]`
```bash
cp -r skills/init-harness ~/.claude/skills/   # rồi gõ /init-harness trong repo đích
```

### Mức 2 — Context sạch
```bash
mkdir -p .claude/agents && cp templates/agents/repo-explorer.md .claude/agents/
```
Đọc `templates/agents/README.md` + `templates/mcp-audit.md`.

### Mức 3 — Guardrails &nbsp;`[trỏ vào CLAUDE.md]`
```bash
mkdir -p .claude && cp templates/settings.json .claude/settings.json
```
**Việc đầu tiên:** thêm lệnh test/lint của repo vào `allow` (xem `templates/guardrails/README.md`).

### Mức 4 — Long-running &nbsp;`[trỏ vào CLAUDE.md]`
```bash
cp templates/setup.sh templates/new-worktree.sh . && chmod +x setup.sh new-worktree.sh
cp templates/long-running/TASK.md .            # khi bắt đầu một việc dài
```

### Mức 5 — Evals & Observability &nbsp;`[cần ≥1 mức đã áp để có cái mà đo]`
```bash
mkdir -p evals/cases && cp templates/evals/cases/example-task.md evals/cases/
```
Đọc `templates/evals/README.md` (có bước **baseline không-harness**) + `observability.md`.

### + Specs (nửa còn lại của Trụ cột 2)
```bash
mkdir -p docs/specs && cp templates/spec/FEATURE.md docs/specs/<feature>.md
```

## Phụ thuộc giữa các mức

- **Mức 1 trước hết** — xương sống; các mức sau viện tới `CLAUDE.md`.
- **Mức 3 & 4** đều "trỏ `CLAUDE.md` tới" artifact của chúng → cần Mức 1 xong.
- **Mức 5** cần ít nhất một mức đã áp để có thay đổi mà đo.

## Tài liệu

`docs/harness-engineering-tutorial.md` (sau khi cài: `docs/harness/tutorial.md`) — vì sao + *khi nào*
dùng từng thứ. Danh mục nguồn đầy đủ của cả ngành:
[Awesome Harness Engineering](https://github.com/walkinglabs/awesome-harness-engineering).

## License

[MIT](LICENSE).
