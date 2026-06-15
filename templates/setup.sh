#!/usr/bin/env bash
# setup.sh — bootstrap môi trường: "một lệnh là repo chạy được".
#
# Mức 4 (long-running): agent chạy nền/lặp KHÔNG thể dừng hỏi "cài gì giờ".
# Script này phải đưa một checkout sạch về trạng thái chạy-được, không cần tương tác.
#
# 2 nguyên tắc bắt buộc:
#   - IDEMPOTENT: chạy lại nhiều lần vẫn an toàn (không nhân đôi, không hỏng state).
#   - FAIL-FAST:  thiếu thứ gì báo NGAY rồi dừng, đừng chạy tiếp trong trạng thái mù.
#
# ĐÂY LÀ SKELETON — mỗi repo cài thứ khác nhau. Điền phần TODO cho repo của bạn,
# rồi trỏ CLAUDE.md tới đây ("Build / Test / Run: chạy ./setup.sh trước").

set -euo pipefail   # lỗi -> dừng; biến chưa set -> dừng; lỗi giữa pipe -> dừng

cd "$(dirname "$0")"

# --- 1. Kiểm điều kiện cần (fail-fast) -------------------------------------
# Thiếu tool nền là báo ngay, đừng để lỗi mơ hồ ở bước sau.
require() {
  command -v "$1" >/dev/null 2>&1 || { echo "✗ thiếu '$1' — cài rồi chạy lại"; exit 1; }
}
# TODO: liệt kê tool repo bạn cần
require git
# require node
# require python3

# --- 2. Cài dependencies (idempotent) --------------------------------------
# Hầu hết package manager đã idempotent sẵn — chạy lại chỉ no-op.
# TODO: thay bằng lệnh của repo bạn
# npm ci
# uv sync
# go mod download

# --- 3. Cấu hình / secrets (fail-fast, KHÔNG tự tạo bừa) --------------------
# Có .env.example mà chưa có .env -> báo cho người chạy tự điền, đừng đoán giá trị.
# if [ -f .env.example ] && [ ! -f .env ]; then
#   echo "✗ chưa có .env — copy .env.example rồi điền secrets"; exit 1
# fi

# --- 4. Dịch vụ phụ trợ (idempotent) ---------------------------------------
# TODO: DB/queue... — dùng lệnh chỉ-tạo-nếu-chưa-có
# docker compose up -d

# --- 5. Verify: chứng minh môi trường thật sự chạy được --------------------
# Đừng kết thúc bằng "xong" mù — chạy một check rẻ để chắc chắn.
# TODO: lệnh smoke-test nhanh nhất của repo
# npm run build --silent
# python -c "import yourpkg"

echo "✓ môi trường sẵn sàng"
