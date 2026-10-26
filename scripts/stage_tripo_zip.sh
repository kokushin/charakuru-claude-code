#!/usr/bin/env bash
# Usage: stage_tripo_zip.sh <downloaded.zip> <extract_dir> <flat_dir> [log_file]
# Waits until the Tripo textured export ZIP has finished downloading (size stable), extracts it into
# <extract_dir>, and copies the FBX and its texture images FLAT into <flat_dir>. Use short paths on Windows:
# the nested .fbm folder inside the ZIP easily exceeds the 260-character path limit. Records the SHA256.
# Both folders must be new or empty: nothing existing is deleted or overwritten. Stops when two files in the
# ZIP share a name (flattening would drop one). Runs on macOS's stock bash 3.2 and on Git Bash for Windows.
set -euo pipefail
[ $# -ge 3 ] || { echo "usage: stage_tripo_zip.sh <downloaded.zip> <extract_dir> <flat_dir> [log_file]" >&2; exit 2; }
abs() { (cd "$(dirname "$1")" && printf '%s/%s' "$(pwd)" "$(basename "$1")"); }
fresh() {
  if [ -e "$1" ] && [ -n "$(ls -A "$1")" ]; then echo "NOT EMPTY $1 (choose a new folder; nothing is deleted)" >&2; exit 1; fi
  mkdir -p "$1"
}
sha256() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -c1-64; }
Z="$1"; LOG="${4:-}"
for i in $(seq 1 60); do [ -f "$Z" ] && [ ! -f "$Z.crdownload" ] && break; sleep 2; done
[ -f "$Z" ] || { echo "MISSING $Z"; exit 1; }
s1=$(wc -c < "$Z"); sleep 2; s2=$(wc -c < "$Z"); [ "$s1" = "$s2" ] || { echo "UNSTABLE $Z"; exit 1; }
fresh "$2"; fresh "$3"
Z="$(abs "$Z")"; X="$(abs "$2")"; R="$(abs "$3")"
unzip -l "$Z" | sed -n '4,11p'
(cd "$X" && unzip -q "$Z")
FILES="$(cd "$X" && find . -type f \( -iname '*.fbx' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \))"
[ -n "$FILES" ] || { echo "NO FBX OR IMAGES in $Z" >&2; exit 1; }
# Windows and macOS file systems ignore case, so compare names case-insensitively.
DUP="$(printf '%s\n' "$FILES" | sed 's|.*/||' | tr '[:upper:]' '[:lower:]' | sort | uniq -d)"
[ -z "$DUP" ] || { echo "DUPLICATE NAMES (flattening would overwrite): $DUP" >&2; exit 1; }
printf '%s\n' "$FILES" | while IFS= read -r f; do cp "$X/$f" "$R/"; done
if [ -n "$LOG" ]; then echo "SHA256 $(sha256 "$Z") $Z" >> "$LOG"; fi
ls -la "$R" | sed -n '4,$p'
