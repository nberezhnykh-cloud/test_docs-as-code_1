#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

SRC_DIR="$ROOT_DIR/src"
BUILD_DIR="$ROOT_DIR/out"
STYLES_DIR="$ROOT_DIR/styles"

mkdir -p "$BUILD_DIR/html"
mkdir -p "$BUILD_DIR/docx"

echo "==> Генерация HTML через Asciidoctor"
asciidoctor \
  -b html5 \
  -D "$BUILD_DIR/html" \
  "$SRC_DIR/index.adoc"

echo "==> Конвертация в DOCX через Pandoc"
pandoc \
  "$BUILD_DIR/html/index.html" \
  --from html \
  --reference-doc="$STYLES_DIR/reference.docx" \
  --lua-filter="$STYLES_DIR/styles.lua" \
  -o "$BUILD_DIR/docx/output.docx"

echo "==> Готово: $BUILD_DIR/docx/output.docx"