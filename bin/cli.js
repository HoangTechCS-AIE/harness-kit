#!/usr/bin/env node
'use strict'

// harness-kit — installer cho Harness Engineering starter kit.
// Chạy: npx harness-kit            (hỏi chọn mức)
//        npx harness-kit --all      (cài hết, không hỏi)
//        npx harness-kit --levels=1,3,4
// Cờ phụ: --target=<dir> (mặc định thư mục hiện tại), --force (ghi đè), --help.
//
// Nguyên tắc: IDEMPOTENT (chạy lại an toàn — file đã có thì bỏ qua trừ khi --force)
// và FAIL-SOFT (thiếu một artifact thì cảnh báo, không sập cả lần cài).

const fs = require('fs')
const path = require('path')
const os = require('os')
const readline = require('readline')

const KIT = path.resolve(__dirname, '..') // gốc package (nơi có templates/, skills/, docs/)
const HOME = os.homedir()
let TARGET = process.cwd() // đặt lại trong main(); dùng để hiển thị đường dẫn cho gọn

// ---- Bản đồ artifact theo mức: [nguồn-trong-kit, đích]. Đích tuyệt đối = cài cấp user. ----
const LEVELS = {
  '1': {
    title: 'Mức 1 — Nền tảng (CLAUDE.md)',
    copy: [['skills/init-harness', path.join(HOME, '.claude', 'skills', 'init-harness')]],
    next: 'Gõ  /init-harness  trong repo đích để sinh CLAUDE.md.',
  },
  '2': {
    title: 'Mức 2 — Context sạch',
    copy: [['templates/agents/repo-explorer.md', '.claude/agents/repo-explorer.md']],
    next: 'Đọc docs/harness/agents-README.md (quy tắc subagent) + mcp-audit.md (rà MCP thừa).',
  },
  '3': {
    title: 'Mức 3 — Guardrails',
    copy: [['templates/settings.json', '.claude/settings.json']],
    next: 'MỞ .claude/settings.json → thêm lệnh test/lint của repo vào "allow" (xem docs/harness/guardrails-README.md). Đây là việc ĐẦU TIÊN.',
  },
  '4': {
    title: 'Mức 4 — Long-running',
    copy: [
      ['templates/setup.sh', 'setup.sh'],
      ['templates/new-worktree.sh', 'new-worktree.sh'],
    ],
    chmod: ['setup.sh', 'new-worktree.sh'],
    next: 'Điền setup.sh cho repo bạn; copy docs/harness/TASK.md ra khi bắt đầu một việc dài.',
  },
  '5': {
    title: 'Mức 5 — Evals & Observability',
    copy: [['templates/evals/cases/example-task.md', 'evals/cases/example-task.md']],
    next: 'Đọc docs/harness/evals-README.md (có bước baseline "không harness") + observability.md.',
  },
}

// ---- Tài liệu hướng dẫn: luôn copy vào <target>/docs/harness/ để team GIỮ LẠI ----
// (npx cache biến mất sau khi chạy, nên phải đổ guidance vào repo.)
const GUIDE_DIR = path.join('docs', 'harness')
const GUIDE = [
  ['docs/harness-engineering-tutorial.md', 'tutorial.md'],
  ['docs/harness-engineering-tutorial.en.md', 'tutorial.en.md'],
  ['README.md', 'kit-README.md'],
  ['templates/agents/README.md', 'agents-README.md'],
  ['templates/mcp-audit.md', 'mcp-audit.md'],
  ['templates/guardrails/README.md', 'guardrails-README.md'],
  ['templates/long-running/README.md', 'long-running-README.md'],
  ['templates/long-running/TASK.md', 'TASK.md'],
  ['templates/evals/README.md', 'evals-README.md'],
  ['templates/evals/observability.md', 'observability.md'],
  ['templates/spec/README.md', 'spec-README.md'],
  ['templates/spec/FEATURE.md', 'FEATURE.md'],
]

function parseArgs(argv) {
  const o = { levels: null, all: false, force: false, target: process.cwd(), help: false }
  for (const a of argv) {
    if (a === '--all') o.all = true
    else if (a === '--force') o.force = true
    else if (a === '--help' || a === '-h') o.help = true
    else if (a.startsWith('--levels=')) o.levels = a.slice(9).split(',').map((s) => s.trim()).filter(Boolean)
    else if (a.startsWith('--target=')) o.target = path.resolve(a.slice(9))
  }
  return o
}

function showHelp() {
  console.log(`
harness-kit — thiết lập repo cho coding agent theo 5 mức.

  npx harness-kit                 hỏi chọn mức rồi cài
  npx harness-kit --all           cài cả 5 mức
  npx harness-kit --levels=1,3    cài mức cụ thể

Cờ:
  --target=<dir>   thư mục đích (mặc định: thư mục hiện tại)
  --force          ghi đè file đã tồn tại (mặc định: bỏ qua)
  --help

Mức: 1 Nền tảng · 2 Context · 3 Guardrails · 4 Long-running · 5 Evals.
Tài liệu luôn được đổ vào <target>/docs/harness/.
`)
}

function rel(p) {
  if (p.startsWith(HOME)) return '~' + p.slice(HOME.length)
  if (p.startsWith(TARGET)) return path.relative(TARGET, p) || '.'
  return p
}

// Đặt một artifact. destAbs: đường dẫn tuyệt đối đã resolve.
function place(srcRel, destAbs, force) {
  const src = path.join(KIT, srcRel)
  if (!fs.existsSync(src)) {
    console.log(`  ⚠ thiếu trong kit, bỏ qua: ${srcRel}`)
    return false
  }
  if (fs.existsSync(destAbs) && !force) {
    console.log(`  • đã có, giữ nguyên: ${rel(destAbs)}  (dùng --force để ghi đè)`)
    return false
  }
  fs.mkdirSync(path.dirname(destAbs), { recursive: true })
  fs.cpSync(src, destAbs, { recursive: true })
  console.log(`  ✓ ${rel(destAbs)}`)
  return true
}

function installLevel(key, target, force) {
  const lv = LEVELS[key]
  if (!lv) {
    console.log(`\n(bỏ qua mức không hợp lệ: ${key})`)
    return
  }
  console.log(`\n${lv.title}`)
  for (const [srcRel, dest] of lv.copy) {
    const destAbs = path.isAbsolute(dest) ? dest : path.join(target, dest)
    place(srcRel, destAbs, force)
  }
  for (const f of lv.chmod || []) {
    const p = path.join(target, f)
    try { if (fs.existsSync(p)) fs.chmodSync(p, 0o755) } catch (_) {}
  }
}

function installGuide(target, force) {
  console.log(`\nTài liệu hướng dẫn → ${path.join(rel(path.join(target, GUIDE_DIR)))}/`)
  for (const [srcRel, name] of GUIDE) {
    place(srcRel, path.join(target, GUIDE_DIR, name), force)
  }
}

function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
  return new Promise((resolve) => rl.question(question, (a) => { rl.close(); resolve(a) }))
}

async function main() {
  const opt = parseArgs(process.argv.slice(2))
  if (opt.help) { showHelp(); return }

  TARGET = opt.target
  console.log(`harness-kit → cài vào: ${opt.target}`)

  let levels
  if (opt.all) levels = Object.keys(LEVELS)
  else if (opt.levels) levels = opt.levels
  else if (process.stdin.isTTY) {
    const a = (await ask('\nCài mức nào? [all] hoặc danh sách vd 1,3,4: ')).trim()
    levels = !a || a.toLowerCase() === 'all' ? Object.keys(LEVELS) : a.split(',').map((s) => s.trim()).filter(Boolean)
  } else {
    levels = Object.keys(LEVELS) // không có TTY (CI/pipe) → cài hết
  }

  for (const k of levels) installLevel(k, opt.target, opt.force)
  installGuide(opt.target, opt.force)

  console.log('\n— Xong. Bước tiếp theo —')
  for (const k of levels) {
    if (LEVELS[k]) console.log(`  [${k}] ${LEVELS[k].next}`)
  }
  console.log('\nĐọc trước hết: docs/harness/tutorial.md (vì sao + KHI NÀO dùng từng thứ).')
}

main().catch((e) => { console.error('harness-kit lỗi:', e.message); process.exit(1) })
