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
  "$SRC_DIR/$1.adoc"

echo "==> Конвертация в DOCX через Pandoc"
pandoc \
  "$BUILD_DIR/html/$1.html" \
  --from html \
  --reference-doc="$STYLES_DIR/reference.docx" \
  --lua-filter="$STYLES_DIR/styles.lua" \
  --toc \
  -M toc-title="Содержание" \
  -o "$BUILD_DIR/docx/$2.docx"

echo "==> Готово: $BUILD_DIR/docx/$2.docx"