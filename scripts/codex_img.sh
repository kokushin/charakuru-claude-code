#!/usr/bin/env bash
# Usage: codex_img.sh <out.png> <prompt.txt> [image1 image2 ...]
# Asks Codex CLI to run its built-in image_gen once and copy the result to <out.png>.
# Runs on macOS's stock bash 3.2 and on Git Bash for Windows. CANVAS overrides the canvas request and
# CODEX_HOME the Codex home (default ~/.codex). An existing <out.png> is removed first, so a stale image can
# never pass as this run's result.
set -euo pipefail
[ $# -ge 2 ] || { echo "usage: codex_img.sh <out.png> <prompt.txt> [image ...]" >&2; exit 2; }
# Paths handed to Codex: C:/... form on Git Bash (cygpath -m), unchanged elsewhere.
native() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }
abs() { (cd "$(dirname "$1")" && printf '%s/%s' "$(pwd)" "$(basename "$1")"); }
OUT="$1"; PROMPT_FILE="$2"; shift 2
[ -f "$PROMPT_FILE" ] || { echo "MISSING $PROMPT_FILE" >&2; exit 1; }
mkdir -p "$(dirname "$OUT")/logs"
OUT="$(abs "$OUT")"; OUTDIR="$(dirname "$OUT")"; NAME="$(basename "$OUT")"
LOG="$OUTDIR/logs/${NAME%.*}.log"; LAST="${LOG%.log}.last.txt"; MARK="${LOG%.log}.start"
GENDIR="${CODEX_HOME:-$HOME/.codex}/generated_images"
IMGARGS=(); DESC=""; i=1
for img in "$@"; do
  [ -f "$img" ] || { echo "MISSING $img" >&2; exit 1; }
  IMGARGS+=(-i "$(native "$(abs "$img")")"); DESC+="Attached image $i: $(basename "$img")"$'\n'; i=$((i+1))
done
CANVAS="${CANVAS:-a square 1:1 canvas at the largest square size available}"
INSTR="You are only an image-generation operator. Use your built-in image_gen tool exactly ONCE to generate ONE image from the prompt between the markers. Pass the attached images to image_gen as input reference images in the given order (Image 1 = first attached image, and so on). Request a genuinely transparent background (real alpha channel) and ${CANVAS}.
${DESC}
After generation, copy the generated PNG (it is saved under $(native "$GENDIR")) to exactly this path (overwrite if it exists): $(native "$OUT")
Do not edit, crop, recolor, resize or post-process the image with code. Do not create any other files. Finally reply with one line: SOURCE=<generated file path> OUT=<copied path>.
<<<PROMPT
$(cat "$PROMPT_FILE")
PROMPT>>>"
rm -f "$OUT" "$LAST"; touch "$MARK"
# ${arr[@]+...}: an empty array is an unbound variable under set -u in bash < 4.4
codex exec --skip-git-repo-check -s workspace-write -C "$(native "$OUTDIR")" ${IMGARGS[@]+"${IMGARGS[@]}"} -o "$(native "$LAST")" "$INSTR" < /dev/null > "$LOG" 2>&1 || { echo "codex failed, see $LOG"; tail -20 "$LOG"; exit 1; }
if [ ! -s "$OUT" ] && [ -d "$GENDIR" ]; then
  # Codex generated but did not copy: take the image only when exactly one PNG appeared during this run.
  NEW=(); while IFS= read -r f; do NEW+=("$f"); done < <(find "$GENDIR" -type f -name '*.png' -newer "$MARK")
  if [ ${#NEW[@]} -eq 1 ]; then cp "${NEW[0]}" "$OUT"; echo "copied by script: ${NEW[0]}"; fi
fi
[ -s "$OUT" ] || { echo "no image at $OUT, see $LOG"; exit 1; }
[ "$(head -c 4 "$OUT" | tail -c 3)" = "PNG" ] || { echo "$OUT is not a PNG, see $LOG"; exit 1; }
[ -f "$LAST" ] && cat "$LAST"; ls -la "$OUT"
