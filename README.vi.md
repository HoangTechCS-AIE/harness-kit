<div align="center">

# harness-kit

**Thiết lập repo cho coding agent (Claude Code) theo 5 mức trưởng thành của harness engineering — bằng một lệnh.**

[![npm](https://img.shields.io/npm/v/@htechcs/harness-kit?logo=npm&color=cb3837)](https://www.npmjs.com/package/@htechcs/harness-kit)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
![node](https://img.shields.io/badge/node-%E2%89%A518-brightgreen)

**Vietnamese** · [English](README.md)

<br>

<img src="https://raw.githubusercontent.com/HoangTechCS-AIE/harness-kit/main/assets/demo.gif" width="700" alt="harness-kit demo">

</div>

---

**Harness** = mọi thứ *bao quanh* model (context, chỉ dẫn, tools, ràng buộc an toàn, orchestration,
đo lường) để agent làm việc đáng tin. Kit này đóng gói nó thành **artifact** cài được + một
**tutorial** dạy *khi nào* dùng từng thứ. Kit ship file; tutorial dạy kỷ luật.

## 1. Hoạt động thế nào

```mermaid
flowchart LR
    D([Bạn]) -->|"npx @htechcs/harness-kit"| I[["harness-kit<br/>installer"]]
    I --> R1[".claude/<br/>settings.json · agents/"]
    I --> R2["repo root<br/>setup.sh · TASK.md"]
    I --> R3["~/.claude/skills/<br/>init-harness"]
    I --> R4["docs/harness/<br/>tutorial + guides"]
    R1 --> A([Claude Code<br/>đọc mỗi session])
    R2 --> A
    R3 --> A
    R4 --> A
```

Một lệnh `npx` rải artifact vào đúng chỗ; từ đó Claude Code đọc chúng ở mọi phiên làm việc.

## 2. Cài nhanh

```bash
npx @htechcs/harness-kit              # hỏi chọn mức rồi cài
npx @htechcs/harness-kit --all        # cài cả 5 mức
npx @htechcs/harness-kit --levels=1,3 # chỉ mức cụ thể
```

Cần **Node ≥18**. Lệnh lưu toàn bộ tài liệu vào `docs/harness/` để team giữ lại. **Idempotent** —
chạy lại an toàn (`--force` để ghi đè).

## 3. 5 mức — mỗi mức chặn một kiểu thất bại

```mermaid
flowchart TD
    L1["Mức 1 · Nền tảng — CLAUDE.md"] --> L2["Mức 2 · Context sạch"]
    L2 --> L3["Mức 3 · Guardrails"]
    L3 --> L4["Mức 4 · Long-running"]
    L4 --> L5["Mức 5 · Evals & Observability"]
    L5 -.->|"phát hiện lỗi → gia cố harness"| L1
```

| Mức | Khi không có nó | Artifact |
|-----|-----------------|----------|
| **1 — Nền tảng** | agent không có chỉ dẫn repo bền vững | skill `/init-harness` → sinh `CLAUDE.md` |
| **2 — Context sạch** | context ngập, agent "loãng" sự chú ý | subagent mẫu + checklist rà MCP |
| **3 — Guardrails** | agent xoá/push nhầm, bị hỏi quyền liên tục | `settings.json` (deny/ask/allow) |
| **4 — Long-running** | việc dài đứt giữa chừng, không resume | `setup.sh`, `new-worktree.sh`, `TASK.md` |
| **5 — Evals & Obs** | không biết agent làm tốt hay tệ | golden-task template + guide observability |

## 4. Cài tay từng mức

> Installer chỉ tự động hoá đúng những lệnh `cp` dưới đây — mở ra nếu muốn hiểu/làm thủ công.

<details>
<summary><b>Mức 1 — Nền tảng · CLAUDE.md</b> &nbsp;<code>[làm trước tiên]</code></summary>

```bash
cp -r skills/init-harness ~/.claude/skills/   # rồi gõ /init-harness trong repo đích
```
</details>

<details>
<summary><b>Mức 2 — Context sạch</b></summary>

```bash
mkdir -p .claude/agents && cp templates/agents/repo-explorer.md .claude/agents/
```
Đọc `templates/agents/README.md` + `templates/mcp-audit.md`.
</details>

<details>
<summary><b>Mức 3 — Guardrails</b> &nbsp;<code>[trỏ vào CLAUDE.md]</code></summary>

```bash
mkdir -p .claude && cp templates/settings.json .claude/settings.json
```
**Việc đầu tiên:** thêm lệnh test/lint của repo vào `allow` (xem `templates/guardrails/README.md`).
</details>

<details>
<summary><b>Mức 4 — Long-running</b> &nbsp;<code>[trỏ vào CLAUDE.md]</code></summary>

```bash
cp templates/setup.sh templates/new-worktree.sh . && chmod +x setup.sh new-worktree.sh
cp templates/long-running/TASK.md .            # khi bắt đầu một việc dài
```
</details>

<details>
<summary><b>Mức 5 — Evals & Observability</b> &nbsp;<code>[cần ≥1 mức đã áp để có cái mà đo]</code></summary>

```bash
mkdir -p evals/cases && cp templates/evals/cases/example-task.md evals/cases/
```
Đọc `templates/evals/README.md` (có bước **baseline không-harness**) + `observability.md`.
</details>

<details>
<summary><b>+ Specs</b> — nửa còn lại của Trụ cột 2</summary>

```bash
mkdir -p docs/specs && cp templates/spec/FEATURE.md docs/specs/<feature>.md
```
</details>

## 5. Phụ thuộc giữa các mức

- **Mức 1 trước hết** — xương sống; các mức sau viện tới `CLAUDE.md`.
- **Mức 3 & 4** đều "trỏ `CLAUDE.md` tới" artifact của chúng → cần Mức 1 xong.
- **Mức 5** cần ít nhất một mức đã áp để có thay đổi mà đo (xem vòng feedback ở sơ đồ trên).

## 6. Benchmark guardrails

Guardrails ở Mức 3 được *đo*, không nói suông. Một benchmark tái lập được cho 25 thao tác rủi ro
(lệnh thảm hoạ, đọc file secret, lệnh dev an toàn) chạy qua các rule phân quyền và chấm xem cái gì
bị chặn / gác / cho phép.

<p align="center">
  <img src="https://raw.githubusercontent.com/HoangTechCS-AIE/harness-kit/main/assets/guardrails-slope.png" width="720" alt="Guardrails coverage: default vs hardened">
</p>

Bộ mặc định gác **68%** ngay khi cài; profile hardened nâng lên **92%** — chặn cứng **6/8 lệnh thảm
hoạ** và **7/7 lần đọc file secret**. Đây là **độ phủ chính sách** guardrail, không phải tỉ lệ hoàn
thành task.

```bash
node bench/guardrails-bench.js                                                       # default
node bench/guardrails-bench.js templates/settings.json bench/settings.hardened.json  # before / after
```

Xem [`bench/RESULTS.md`](bench/RESULTS.md) cho phương pháp đo và 2 gap còn lại.

## 7. Tài liệu

`docs/harness-engineering-tutorial.md` ([English](docs/harness-engineering-tutorial.en.md)) — vì sao +
*khi nào* dùng từng thứ (sau khi cài: `docs/harness/`). Danh mục nguồn đầy đủ của cả ngành:
[Awesome Harness Engineering](https://github.com/walkinglabs/awesome-harness-engineering).

## 8. License

[MIT](LICENSE).
