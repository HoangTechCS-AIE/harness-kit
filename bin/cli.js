#!/usr/bin/env node
'use strict'

// harness-kit — installer for the Harness Engineering starter kit.
// Run: npx @htechcs/harness-kit            (pick levels)
//      npx @htechcs/harness-kit --all      (install all, no prompt)
//      npx @htechcs/harness-kit --levels=1,3
// Extra flags: --target=<dir> (default: current directory), --force (overwrite), --help.
//
// Principles: IDEMPOTENT (safe to re-run — existing files are skipped unless --force)
// and FAIL-SOFT (a missing artifact is warned about, it doesn't abort the whole install).

const fs = require('fs')
const path = require('path')
const os = require('os')
const readline = require('readline')

const KIT = path.resolve(__dirname, '..') // package root (holds templates/, skills/, docs/)
const HOME = os.homedir()
let TARGET = process.cwd() // reset in main(); used to print tidy relative paths

// ---- Artifact map per level: [source-in-kit, destination]. Absolute dest = user-level install. ----
const LEVELS = {
  '1': {
    title: 'Level 1 — Foundation (CLAUDE.md)',
    copy: [['skills/init-harness', path.join(HOME, '.claude', 'skills', 'init-harness')]],
    next: 'Run  /init-harness  in the target repo to generate CLAUDE.md.',
  },
  '2': {
    title: 'Level 2 — Clean context',
    copy: [['templates/agents/repo-explorer.md', '.claude/agents/repo-explorer.md']],
    next: 'Read docs/harness/agents-README.md (subagent rules) + mcp-audit.md (prune unused MCP servers).',
  },
  '3': {
    title: 'Level 3 — Guardrails',
    copy: [['templates/settings.json', '.claude/settings.json']],
    next: 'OPEN .claude/settings.json → add your repo\'s test/lint commands to "allow" (see docs/harness/guardrails-README.md). Do this FIRST.',
  },
  '4': {
    title: 'Level 4 — Long-running',
    copy: [
      ['templates/setup.sh', 'setup.sh'],
      ['templates/new-worktree.sh', 'new-worktree.sh'],
    ],
    chmod: ['setup.sh', 'new-worktree.sh'],
    next: 'Fill in setup.sh for your repo; copy docs/harness/TASK.md out when you start a long task.',
  },
  '5': {
    title: 'Level 5 — Evals & Observability',
    copy: [['templates/evals/cases/example-task.md', 'evals/cases/example-task.md']],
    next: 'Read docs/harness/evals-README.md (includes a no-harness baseline step) + observability.md.',
  },
}

// ---- Guidance docs: always copied into <target>/docs/harness/ so the team keeps them ----
// (the npx cache disappears after the run, so the guidance must land in the repo.)
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
harness-kit — set up a repo for a coding agent across 5 maturity levels.

  npx @htechcs/harness-kit              pick levels interactively, then install
  npx @htechcs/harness-kit --all        install all 5 levels
  npx @htechcs/harness-kit --levels=1,3 install specific levels

Flags:
  --target=<dir>   target directory (default: current directory)
  --force          overwrite existing files (default: skip)
  --help

Levels: 1 Foundation · 2 Context · 3 Guardrails · 4 Long-running · 5 Evals.
Docs are always written to <target>/docs/harness/.
`)
}

function rel(p) {
  if (p.startsWith(HOME)) return '~' + p.slice(HOME.length)
  if (p.startsWith(TARGET)) return path.relative(TARGET, p) || '.'
  return p
}

// Place one artifact. destAbs: an already-resolved absolute path.
function place(srcRel, destAbs, force) {
  const src = path.join(KIT, srcRel)
  if (!fs.existsSync(src)) {
    console.log(`  ⚠ missing in kit, skipping: ${srcRel}`)
    return false
  }
  if (fs.existsSync(destAbs) && !force) {
    console.log(`  • exists, keeping: ${rel(destAbs)}  (use --force to overwrite)`)
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
    console.log(`\n(skipping invalid level: ${key})`)
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
  console.log(`\nGuidance docs → ${path.join(rel(path.join(target, GUIDE_DIR)))}/`)
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
  console.log(`harness-kit → installing into: ${opt.target}`)

  let levels
  if (opt.all) levels = Object.keys(LEVELS)
  else if (opt.levels) levels = opt.levels
  else if (process.stdin.isTTY) {
    const a = (await ask('\nWhich levels? [all] or a list e.g. 1,3,4: ')).trim()
    levels = !a || a.toLowerCase() === 'all' ? Object.keys(LEVELS) : a.split(',').map((s) => s.trim()).filter(Boolean)
  } else {
    levels = Object.keys(LEVELS) // no TTY (CI/pipe) → install everything
  }

  for (const k of levels) installLevel(k, opt.target, opt.force)
  installGuide(opt.target, opt.force)

  console.log('\n— Done. Next steps —')
  for (const k of levels) {
    if (LEVELS[k]) console.log(`  [${k}] ${LEVELS[k].next}`)
  }
  console.log('\nRead first: docs/harness/tutorial.md (the why + WHEN to use each piece).')
}

main().catch((e) => { console.error('harness-kit error:', e.message); process.exit(1) })
