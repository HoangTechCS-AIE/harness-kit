# Harness Engineering cho Team — Tutorial thực chiến (Claude Code & Codex)

**Tiếng Việt** · [English](harness-engineering-tutorial.en.md)

> Dành cho dev đã quen dùng AI coding agent, muốn hiểu sâu *vì sao* agent lúc tốt lúc tệ và *làm gì* để nó đáng tin cậy hơn.
> Tài liệu này là bản tinh gọn + thực hành, dựa trên các nguồn trong [Awesome Harness Engineering](https://github.com/walkinglabs/awesome-harness-engineering/blob/main/README.md). Mỗi phần đều có link đọc sâu.

---

## Mục lục

1. [Harness Engineering là gì — và tại sao bạn cần nó](#1-harness-engineering-là-gì--và-tại-sao-bạn-cần-nó)
2. [Mô hình tư duy: 6 trụ cột của harness](#2-mô-hình-tư-duy-6-trụ-cột-của-harness)
3. [Trụ cột 1 — Context & Working State](#3-trụ-cột-1--context--working-state)
4. [Trụ cột 2 — Repo-local instructions & Specs (CLAUDE.md / AGENTS.md)](#4-trụ-cột-2--repo-local-instructions--specs-claudemd--agentsmd)
5. [Trụ cột 3 — Tools & Environment](#5-trụ-cột-3--tools--environment)
6. [Trụ cột 4 — Guardrails & Safe Autonomy](#6-trụ-cột-4--guardrails--safe-autonomy)
7. [Trụ cột 5 — Long-running, Orchestration & Resumability](#7-trụ-cột-5--long-running-orchestration--resumability)
8. [Trụ cột 6 — Evals & Observability](#8-trụ-cột-6--evals--observability)
9. [Hands-on: viết CLAUDE.md cho repo bằng `/init-harness`](#9-hands-on-viết-claudemd-cho-repo-bằng-init-harness)
10. [Checklist áp dụng cho team](#10-checklist-áp-dụng-cho-team)
11. [Lộ trình đọc thêm](#11-lộ-trình-đọc-thêm)

---

## 1. Harness Engineering là gì — và tại sao bạn cần nó

Ví von dễ nhớ nhất: một chiếc xe đua.

- **Model** (Claude, GPT…) = **động cơ**. Mạnh, nhưng tự nó chỉ sinh ra token.
- **Harness** = **toàn bộ phần còn lại của chiếc xe**: khung, vô-lăng, phanh, đồng hồ, hệ thống nhiên liệu, dây an toàn — tức là tất cả những gì *bao quanh* model để biến nó thành một agent làm được việc thật.

> **Harness Engineering** = nghề thiết kế và vận hành cái môi trường bao quanh agent (context, tools, ràng buộc, orchestration, đo lường) để agent làm việc **đáng tin cậy**, đặc biệt với task lập trình dài hơi.

Luận điểm cốt lõi của cả ngành: **khi agent code ra kết quả tệ, phần lớn là lỗi harness, không phải lỗi model.** Cùng một model, đổi harness có thể nhảy vọt điểm benchmark — LangChain đã chứng minh điều này bằng số liệu trong [Improving Deep Agents with harness engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/).

**Tại sao team code phải quan tâm?** Vì mọi triệu chứng khó chịu khi dùng Claude Code/Codex đều là vấn đề harness:

| Triệu chứng team hay gặp | Đây là vấn đề harness về… |
|---|---|
| Agent "quên" việc đang làm giữa task dài | Context & working state |
| Mỗi người dùng agent ra một kiểu, không nhất quán | Repo-local instructions / specs |
| Agent gọi sai tool, hoặc thiếu tool cần thiết | Tool design & environment |
| Agent sửa bừa, xoá nhầm, chạy lệnh nguy hiểm | Guardrails & safe autonomy |
| Task chạy 30 phút thì đứt, không resume được | Orchestration & resumability |
| Không ai biết agent làm tốt hay tệ | Evals & observability |

Đọc nền tảng:
- [Harness Engineering — Thoughtworks/Martin Fowler](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) — chia harness thành context engineering, architectural constraints, và "garbage collection" chống entropy.
- [The Anatomy of an Agent Harness — LangChain](https://blog.langchain.com/the-anatomy-of-an-agent-harness/) — agent = model + harness (prompts, tools, middleware, orchestration, runtime).
- [Skill Issue: Harness Engineering for Coding Agents — HumanLayer](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents) — bài "đập bàn" rằng kết quả yếu thường là lỗi harness.

---

## 2. Mô hình tư duy: 6 trụ cột của harness

Một cách phân rã hàn lâm hơn là **CAR — Control / Agency / Runtime** (từ [position paper về harness layer](https://www.preprints.org/manuscript/202603.1756)): harness vừa *kiểm soát* agent, vừa cấp *quyền hành động*, vừa là *runtime* chạy nó.

Nhưng để team áp dụng được, mình dùng 6 trụ cột thực dụng (bám đúng cấu trúc của [README repo này](https://github.com/walkinglabs/awesome-harness-engineering/blob/main/README.md)):

```
                    ┌─────────────────────────────┐
                    │          MODEL              │
                    └─────────────┬───────────────┘
                                  │
   ┌──────────────┬──────────────┼──────────────┬──────────────┐
   │              │              │              │              │
1. Context    2. Specs/      3. Tools &     4. Guardrails  5. Orchestration
   & State        AGENTS.md      Environment    & Safety       & Resumability
   │              │              │              │              │
   └──────────────┴──────────────┴──────┬───────┴──────────────┘
                                         │
                              6. Evals & Observability
                              (đo lường để cải tiến cả 5 cái trên)
```

Năm trụ cột đầu là *xây dựng* harness. Trụ cột 6 (evals) là *vòng phản hồi* — không đo thì không biết các thay đổi có thật sự tốt lên hay không.

---

## 3. Trụ cột 1 — Context & Working State

**Nguyên tắc số 1:** coi context window là **ngân sách bộ nhớ làm việc (working memory budget)**, không phải thùng rác để nhồi mọi thứ vào. Mỗi token đưa vào context đều "loãng" sự chú ý của model. Đây là thông điệp trung tâm của [Effective context engineering for AI agents — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

Các kỹ thuật thực chiến (tổng hợp từ [Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) và [OpenHands](https://openhands.dev/blog/openhands-context-condensensation-for-more-efficient-ai-agents)):

- **KV-cache locality:** giữ phần đầu prompt (system prompt, instructions) *ổn định, không đổi* giữa các bước → tận dụng cache, rẻ hơn và nhanh hơn. Đừng chèn timestamp/ID ngẫu nhiên vào đầu prompt.
- **Filesystem làm bộ nhớ ngoài:** thay vì nhồi cả file dài vào context, để agent ghi/đọc file (notes, scratchpad, kết quả trung gian). Context chỉ giữ *con trỏ* tới thông tin, không giữ toàn bộ thông tin.
- **Giữ lại failure trong context:** khi một lệnh fail, đừng giấu lỗi đi — để agent thấy stack trace để nó tự sửa. Che lỗi = agent lặp lại sai lầm.
- **Context condensation:** với session dài, nén lịch sử hội thoại nhưng *bảo toàn* mục tiêu, tiến độ, các file quan trọng, và test đang fail.
- **Backpressure:** đừng để agent đốt context vào việc nhiễu/giá trị thấp (xem [Context-Efficient Backpressure — HumanLayer](https://www.humanlayer.dev/blog/context-efficient-backpressure)).

**Trong Claude Code cụ thể:**
- Context tự được summarize khi dài (compaction) — nên các thông tin quan trọng *phải* nằm ở nơi bền vững (CLAUDE.md, file trong repo), đừng chỉ "nói miệng" trong chat.
- Dùng **subagents** để cô lập việc tốn context (vd: một agent đi đọc 50 file rồi chỉ trả về kết luận) → context chính không bị ngập.
- `/clear` khi đổi task để reset working state.

Đọc thêm: [Advanced Context Engineering for Coding Agents — HumanLayer](https://www.humanlayer.dev/blog/advanced-context-engineering), [Context Engineering for Coding Agents — Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html).

---

## 4. Trụ cột 2 — Repo-local instructions & Specs (CLAUDE.md / AGENTS.md)

Đây là **đòn bẩy rẻ nhất, hiệu quả nhất** cho một team — và là thứ nên làm đầu tiên.

Ý tưởng: thay vì mỗi dev tự "dạy" agent lại từ đầu mỗi lần, ta viết **một file hướng dẫn nằm trong repo** mà agent tự động đọc. Nó là "bộ nhớ chung, bền vững" của team.

- **Claude Code** đọc `CLAUDE.md` (ở root repo, và có thể phân tầng theo thư mục con).
- **Codex** đọc [`AGENTS.md`](https://github.com/agentsmd/agents.md) — một format mở, công cụ-trung lập (Codex, và nhiều agent khác cũng hỗ trợ).

> Mẹo cho team dùng *cả hai*: viết nội dung chính một lần, rồi để một file là nguồn thật và file kia symlink/đồng bộ sang. Tránh hai file lệch nhau.

**Một file hướng dẫn tốt nên có gì** (theo [Writing a good CLAUDE.md — HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md)):
- **Cách build / test / lint / run** — kèm lệnh chạy *một* test đơn lẻ.
- **Kiến trúc tổng quan** — những thứ cần đọc nhiều file mới hiểu (big picture), không liệt kê từng file.
- **Quy ước riêng** của codebase mà agent không tự đoán được (naming, format entry, ordering…).
- **Ràng buộc** ("không sửa file generated", "luôn chạy test trước khi báo xong").
- **Tránh:** lời khuyên chung chung ("viết code sạch"), liệt kê cây thư mục (agent tự khám phá được).

**Spec-driven development** là bước nâng cao: với feature lớn, viết spec rõ ràng *trước*, rồi cho agent thực thi theo spec. Spec mạnh → kết quả ổn định hơn nhiều.
- [GitHub Spec Kit](https://github.com/github/spec-kit) — toolkit cho spec-driven dev.
- [Understanding Spec-Driven Development — Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html).
- [12 Factor Agents — HumanLayer](https://www.humanlayer.dev/blog/12-factor-agents) — nguyên tắc vận hành agent production: prompt tường minh, agent *sở hữu* state, pause/resume sạch.

---

## 5. Trụ cột 3 — Tools & Environment

Agent hành động qua **tools** (đọc/ghi file, chạy lệnh, gọi API, MCP server). Chất lượng tool quyết định agent gọi đúng hay sai.

Nguyên tắc thiết kế tool tốt ([Writing effective tools for agents — Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)):
- Tool ít mà rõ ràng > nhiều tool chồng chéo. Quá nhiều tool làm model "rối tay".
- Tên + mô tả + schema phải nói rõ *khi nào dùng* và *trả về gì*.
- Trả về thông tin gọn, đã chắt lọc — đừng đổ raw dump làm ngập context (liên hệ lại trụ cột 1).
- Lỗi trả về phải *actionable* (gợi ý cách sửa), vì agent đọc lỗi để tự điều chỉnh.

**MCP (Model Context Protocol)** — cách chuẩn để cắm tool/nguồn dữ liệu ngoài vào agent (cả Claude Code và Codex đều hỗ trợ). Đọc:
- [Code execution with MCP — Anthropic](https://www.anthropic.com/engineering/code-execution-with-mcp) — cấp quyền thực thi qua ranh giới tool tường minh, soi được.
- Benchmark đo chất lượng tích hợp MCP: [MCP Bench](https://github.com/modelscope/MCPBench), [MCPMark](https://github.com/eval-sys/mcpmark).

**Environment** = cái "thế giới" agent chạy trong đó (shell, filesystem, container, browser). Harness tốt kiểm soát môi trường này: sandbox để an toàn, và cung cấp đúng công cụ verify (test runner, linter, browser để tự kiểm chứng kết quả).

---

## 6. Trụ cột 4 — Guardrails & Safe Autonomy

Mục tiêu: cho agent **tự chủ nhiều nhất có thể** mà vẫn **an toàn** — giảm số lần phải bấm "approve" thủ công nhưng không mất kiểm soát.

Các kỹ thuật:
- **Sandboxing & policy:** giới hạn agent chạy trong môi trường cô lập, định nghĩa rõ thao tác nào tự do / nào cần xác nhận. Xem [Beyond permission prompts — Anthropic](https://www.anthropic.com/engineering/claude-code-sandboxing).
- **Chống prompt injection:** khi agent đọc nội dung ngoài (web, file, issue), nội dung đó có thể chứa "lệnh ẩn" lừa agent. Phòng vệ bằng confirmation mode, analyzer, sandbox, hard policy — xem [Mitigating Prompt Injection — OpenHands](https://openhands.dev/blog/mitigating-prompt-injection-attacks-in-software-agents).
- **Quality-in-the-loop:** đưa kiểm tra chất lượng *vào trong vòng lặp* (lint/test/typecheck chạy tự động) thay vì review thủ công sau cùng. [Assessing internal quality — Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/ccmenu-quality.html).
- **Anchoring tới reference app:** ràng buộc agent bằng ví dụ mẫu cụ thể để output nhất quán. [Anchoring to a reference application — Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/anchoring-to-reference.html).
- **Quét rủi ro trước deploy:** [Lurkr](https://github.com/agentveil-protocol/lurkr) — static scanner chạy trong CI để phát hiện rủi ro năng lực agent (credentials lọt vào context LLM, `eval`/subprocess trong `@tool`, MCP endpoint chưa verify…).

**Trong Claude Code:** dùng permission modes, allowlist trong `settings.json`, và **hooks** (chạy lệnh tự động trước/sau tool call — vd auto-format, hoặc chặn lệnh nguy hiểm). Đây chính là cách "code hoá" guardrails cho cả team.

Mental model về vai trò con người: [Humans and Agents in Software Engineering Loops — Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/humans-and-agents.html) — con người nên *gia cố harness* thay vì soi từng dòng output.

---

## 7. Trụ cột 5 — Long-running, Orchestration & Resumability

Đây là phần "khó và đáng giá" nhất: làm sao agent chạy được task dài *qua nhiều context window* mà không lạc.

Bài gốc bắt buộc đọc: [Effective harnesses for long-running agents — Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). Các pattern chính:
- **Initializer agent:** một agent khởi tạo dựng sẵn môi trường/scaffolding trước khi agent chính bắt đầu.
- **Feature list / task state:** một danh sách việc bền vững (ghi ra file) làm "nguồn sự thật" về tiến độ — agent tick dần, context window mới đọc lại để biết đang ở đâu.
- **`init.sh`:** script chuẩn hoá việc setup môi trường để mọi run đều bắt đầu từ trạng thái sạch, lặp lại được.
- **Self-verification:** agent tự kiểm chứng kết quả (chạy test, build) trước khi tuyên bố xong.
- **Handoff artifacts:** khi context sắp đầy, ghi lại "biên bản bàn giao" để context window kế tiếp tiếp tục liền mạch.

Xem thêm bản follow-up: [Harness design for long-running application development — Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps).

**Orchestration patterns:**
- **Multi-agent:** chia vai (planner, coder, reviewer) và phối hợp có cấu trúc — [How we built our multi-agent research system — Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system).
- **Ralph pattern:** harness tối giản `while :; do cat PROMPT.md | claude-code; done` — vòng lặp một-task, prompt xếp chồng deterministic, subagent song song có giới hạn. Đọc cho vui mà sâu: [Ralph Wiggum as a Software Engineer](https://ghuntley.com/ralph/).
- **Framework vs Runtime vs Harness** — phân biệt rạch ròi để biết cái gì thuộc về đâu: [Agent Frameworks, Runtimes, and Harnesses, Oh My! — LangChain](https://blog.langchain.com/agent-frameworks-runtimes-and-harnesses-oh-my/).

**Reference implementations để học bằng cách đọc code:**
- [SWE-agent](https://github.com/SWE-agent/SWE-agent) — coding agent nghiên cứu, harness/prompt/tools/env đều soi được.
- [deepagents — LangChain](https://github.com/langchain-ai/deepagents) — patterns cho agent dài hơi.
- [Citadel](https://github.com/SethGammon/Citadel) — harness cho Claude Code & Codex với worktree cô lập, multi-agent, memory bền vững.

**Trong Claude Code:** subagents, plan mode, worktree isolation, và TodoWrite (task list bền vững trong session) chính là hiện thân của các pattern trên.

---

## 8. Trụ cột 6 — Evals & Observability

Không đo thì không cải tiến được. Với agent, "đo" khó hơn code thường vì có *nhiều đường* dẫn tới thành công/thất bại.

**Observability — soi cái agent thực sự làm:**
- **Traces:** ghi lại từng bước (tool call, kết quả, quyết định) để debug và chấm điểm. Chuẩn hoá bằng [OpenTelemetry Semantic Conventions for GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) để trace portable giữa các backend.
- Công cụ: [AgentOps](https://github.com/AgentOps-AI/agentops) (monitoring, session replay, cost tracking), [agenttrace](https://github.com/luoyuctl/agenttrace) (TUI/CLI local-first audit trace coding-agent: cost spike, tool failure, latency gap, diff giữa các lần thử).

**Evals — chấm điểm chất lượng:**
- Biến trace thật thành eval lặp lại được (JSONL log + deterministic check): [Testing Agent Skills with Evals — OpenAI](https://developers.openai.com/blog/eval-skills/), [How to Evaluate Agent Skills — OpenHands](https://openhands.dev/blog/evaluating-agent-skills).
- **Trace grading:** chấm trực tiếp trên trajectory cho task nhiều bước — [Trace grading — OpenAI](https://platform.openai.com/docs/guides/trace-grading).
- Tư duy "đo cái gì khi có nhiều trajectory": [Demystifying Evals for AI Agents — Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).
- Framework eval mở: [Inspect AI — UK AISI](https://inspect.aisi.org.uk/) (solver, scorer, sandbox, tool-use, log viewer).

**Cảnh báo quan trọng:** cấu hình runtime/hạ tầng có thể làm điểm benchmark dao động *lớn hơn* khoảng cách giữa các model trên leaderboard — tức là "noise hạ tầng" dễ làm bạn kết luận sai. Đọc [Quantifying infrastructure noise in agentic coding evals — Anthropic](https://www.anthropic.com/engineering/infrastructure-noise) trước khi tin một con số.

**Benchmarks** (khi muốn so sánh *harness*, không chỉ model): bắt đầu với [SWE-bench Verified](https://www.swebench.com/) (sửa GitHub issue thật) và [Terminal-Bench](https://www.tbench.ai/) (agent terminal-native). Xem cả mục [Benchmarks trong README](https://github.com/walkinglabs/awesome-harness-engineering/blob/main/README.md#benchmarks) để chọn theo loại task.

---

## 9. Hands-on: viết CLAUDE.md cho repo bằng `/init-harness`

Đây là bài thực hành đầu tiên nên làm với team — đòn bẩy lớn nhất, làm trong 1 buổi. Phần này tập trung `CLAUDE.md` (Claude Code); `AGENTS.md` cho Codex để đợt sau (xem cuối mục).

### Đừng auto-generate bằng `/init` mặc định

Nguồn chuẩn [Writing a good CLAUDE.md — HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md) nói thẳng: ***"don't auto-generate with `/init` — carefully craft its contents"***. Lý do: `/init` chỉ **mô tả hiện trạng** repo, còn thiếu hai thứ làm nên "harness" — **Guardrails** (ràng buộc hành vi agent) và **Definition of Done** (bằng chứng để agent tự verify).

Team mình đã đóng gói đúng kỷ luật này thành một skill: **`/init-harness`**.

### Cách làm (khuyến nghị): gõ `/init-harness`

Trong Claude Code, ở repo mục tiêu:

```
/init-harness            # hoặc: /init-harness <đường-dẫn-repo>
```

Skill sẽ: (1) quét repo điền **WHAT/WHY/HOW** (stack, build/test/run, **lệnh chạy một test**, kiến trúc); (2) hỏi **một lượt** để chốt **Guardrails + Definition of Done** — đúng phần nó không tự đoán được; (3) sinh file theo kỷ luật bên dưới và tự self-check.

### File nó sinh ra trông như thế nào

```md
# CLAUDE.md

## Repo này là gì
<WHY + WHAT: 1–3 câu. Cái mà đọc 1 file không ra.>

## Build / Test / Run
- Build / Test toàn bộ / Lint / typecheck: <lệnh>
- Chạy MỘT test: <lệnh cụ thể copy-paste chạy ngay>   ← tăng tốc feedback loop nhất
  (repo không có build/test — vd awesome-list — thì mục này thành cách verify thật,
   ví dụ: kiểm link bằng `curl -sI <url>` trước khi thêm.)

## Kiến trúc tổng quan
<Big picture cần đọc nhiều file mới hiểu. Dùng pointer path/file.ts:42, KHÔNG copy code.>

## Quy ước riêng (chỉ cái KHÔNG hiển nhiên)
<Pattern bắt buộc agent không tự đoán. KHÔNG ghi style/format — để linter lo.>

## Guardrails                      ← /init mặc định KHÔNG có
- KHÔNG sửa <file/thư mục generated>.
- LUÔN <chạy test/lint> trước khi báo hoàn thành.
- Cần xác nhận trước khi: <thao tác nguy hiểm>.

## Definition of Done              ← /init mặc định KHÔNG có
Một thay đổi coi là xong khi: <bằng chứng cụ thể — test xanh, build ok, lint sạch>.
```

> **Ví dụ thật (before/after):** [CLAUDE.md của chính repo này](https://github.com/walkinglabs/awesome-harness-engineering/blob/main/CLAUDE.md) được sinh bằng `/init-harness`. Repo là một awesome-list không có build/test, nên mục "HOW" được điều chỉnh thành *verify link + lychee CI* — và có đủ `Guardrails` + `Definition of Done` mà bản `/init` cũ thiếu.

### Nguyên tắc viết (trích nguồn chuẩn)

Từ [Writing a good CLAUDE.md — HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md):
- **"LLMs are stateless functions"** — `CLAUDE.md` là file *duy nhất* nạp vào *mọi* session. Mọi dòng phải xứng đáng.
- **"Less is more"** — model theo được ~150–200 instruction (system prompt đã chiếm ~50) → giữ file **<300 dòng, nhắm ~60–120**.
- **"Prefer pointers to copies"** — trỏ `path:line`, đừng copy snippet.
- **Không nhồi style/convention** — để linter/formatter lo.
- **Craft, đừng auto-dump** — phân tích để *đề xuất*, rồi chắt lọc.

### Dùng chung cho cả Claude Code + Codex (đợt sau)

Theo [agents.md](https://agents.md): agent đọc **file gần nhất trong cây thư mục — closest-file-wins** (repo chính của OpenAI có 88 file `AGENTS.md` lồng nhau), nên monorepo dùng root + override theo package (đúng ý "phân tầng" mà `/init-harness` hỏi khi repo lớn). Cách di trú chuẩn: ***"rename existing files to AGENTS.md and create symbolic links for backward compatibility"***.

→ Khi tới đợt thêm Codex: đổi nội dung sang `AGENTS.md` làm nguồn thật, rồi `ln -s AGENTS.md CLAUDE.md`. Một nguồn, hai công cụ, không bao giờ lệch.

> Chọn chiến lược theo loại codebase: [Greenfield AI, Brownfield AI, and the Vibecode You Just Inherited](https://sawinyh.com/blog/greenfield-vs-brownfield-ai-codebases) — greenfield agent-native, legacy brownfield, và code vừa vibecode xong; mỗi loại cần playbook khác (CLAUDE.md phân tầng, pre-commit hook siết dần, baseline lint).

---

## 10. Checklist áp dụng cho team

Dán cái này vào wiki nội bộ. Đi từ trên xuống — mỗi mục là một nấc trưởng thành harness.

**Mức 1 — Nền tảng (làm ngay tuần này)**
- [ ] Mỗi repo chính có `CLAUDE.md` sinh bằng `/init-harness` (xem [Phần 9](#9-hands-on-viết-claudemd-cho-repo-bằng-init-harness)), KHÔNG dùng `/init` thô.
- [ ] File có đủ mục `Guardrails` + `Definition of Done`, không chỉ build/test/kiến trúc.
- [ ] Có lệnh chạy *một* test đơn lẻ (hoặc cách verify thật) ghi rõ trong file.
- [ ] Quy ước: thông tin quan trọng đi vào file repo, không "nói miệng" trong chat.

**Mức 2 — Context & Tools**
- [ ] Dùng subagents/worktree cho việc tốn context (đọc nhiều file, refactor lớn).
- [ ] `/clear` khi đổi task; nén context cho session dài.
- [ ] Rà soát MCP server đang cắm: cái nào thật sự cần, cái nào gây nhiễu context.

**Mức 3 — Guardrails**
- [ ] Cấu hình permission/allowlist trong `settings.json` cho thao tác an toàn.
- [ ] Hooks tự động (format, chặn lệnh nguy hiểm) cho cả team.
- [ ] Test/lint/typecheck chạy *trong vòng lặp*, không để review thủ công cuối cùng.
- [ ] (Nếu agent đọc nội dung ngoài) có biện pháp chống prompt injection.

**Mức 4 — Long-running**
- [ ] Task dài có feature-list/task-state bền vững (file hoặc TodoWrite).
- [ ] Agent tự verify (chạy test/build) trước khi báo xong.
- [ ] Có `init.sh`/script setup môi trường lặp lại được.

**Mức 5 — Evals & Observability**
- [ ] Bật trace/observability để soi agent làm gì + chi phí.
- [ ] Có ít nhất vài eval lặp lại được cho task quan trọng (kèm baseline "không harness").
- [ ] Khi so sánh số liệu, kiểm soát noise hạ tầng trước khi kết luận.

---

## 11. Lộ trình đọc thêm

Đọc theo thứ tự này nếu bắt đầu từ con số 0:

1. **Khái niệm:** [Thoughtworks — Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) → [LangChain — Anatomy of an Agent Harness](https://blog.langchain.com/the-anatomy-of-an-agent-harness/)
2. **Hai bài gốc nặng ký:** [Anthropic — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) + [OpenAI — Harness engineering với Codex](https://openai.com/index/harness-engineering/)
3. **Context (ăn tiền nhất khi code):** [Anthropic — Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) + [Manus — Lessons](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
4. **Áp dụng:** [Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) + [AGENTS.md](https://github.com/agentsmd/agents.md) → rồi chạy `/init-harness` để sinh file cho repo team ([Phần 9](#9-hands-on-viết-claudemd-cho-repo-bằng-init-harness))
5. **Đo lường:** [Anthropic — Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

> Toàn bộ danh mục đầy đủ (foundations, context, guardrails, specs, evals, benchmarks, runtimes) nằm ở [README của repo này](https://github.com/walkinglabs/awesome-harness-engineering/blob/main/README.md) — coi đó là thư viện tra cứu chính.
