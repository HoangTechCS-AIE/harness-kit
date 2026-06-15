#!/usr/bin/env bash
# new-worktree.sh — tạo một git worktree + branch riêng cho một task song song/dài.
#
# Mức 4 (long-running): mỗi task nặng nên có cây làm việc RIÊNG, để chạy song song
# mà không giẫm chân (không stash/switch liên tục, không sửa đè lên nhau).
#
# Dùng:   ./new-worktree.sh <tên-task>
# Vd:     ./new-worktree.sh refactor-auth
#   -> tạo branch 'refactor-auth' + thư mục ../<repo>-refactor-auth (cạnh repo, KHÔNG lồng trong).

set -euo pipefail

name="${1:-}"
[ -n "$name" ] || { echo "dùng: $0 <tên-task>   (vd: refactor-auth)"; exit 1; }

# Phải đứng trong một git repo.
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "✗ không phải git repo"; exit 1; }

root="$(git rev-parse --show-toplevel)"
repo="$(basename "$root")"
dir="$root/../${repo}-${name}"          # đặt CẠNH repo, không lồng -> git status không nhiễu

[ -e "$dir" ] && { echo "✗ đã tồn tại: $dir"; exit 1; }   # fail-fast, không ghi đè

# Tách từ base mới nhất. Đổi 'main' nếu repo bạn dùng tên khác.
base="$(git symbolic-ref --quiet --short HEAD || echo main)"

if git show-ref --verify --quiet "refs/heads/${name}"; then
  git worktree add "$dir" "$name"            # branch đã có -> checkout vào worktree mới
else
  git worktree add -b "$name" "$dir" "$base" # branch mới tách từ base hiện tại
fi

echo "✓ worktree: $dir   (branch: $name)"
echo "  cd \"$dir\" để bắt đầu. Xong việc: git worktree remove \"$dir\""
