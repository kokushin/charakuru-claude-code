# セットアップと事前確認

## 必要なもの

| もの | 確認方法・メモ |
| --- | --- |
| きゃらくる配布キット | 専用配布 ZIP を展開したフォルダ（`AGENTS.md`、`package.json`、`server.mjs`、`public/`、`scripts/`、`skills/` が同じ階層）。GitHub の自動生成「Source code」ZIP とは別物 |
| Node.js 22 以上 | `node -v`。キットのルートで `npm start` → `http://127.0.0.1:8766`。ターミナルは開いたまま（Claude Code ならバックグラウンド実行） |
| Blender 5.2 以降 | `BLENDER` 環境変数に実行ファイルを入れ、すべて `"$BLENDER" -b --factory-startup --python-exit-code 1 --python ...` で呼ぶ（`blender` は通常 PATH にない）。例: Windows `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`、macOS `/Applications/Blender.app/Contents/MacOS/Blender` |
| VRM Add-on for Blender | Blender の拡張機能として導入。`--factory-startup` でも読み込まれる |
| bash | `<skill>/scripts/*.sh` 用。Windows は Git for Windows の Git Bash（`unzip`・`cygpath` 同梱）、macOS は標準の bash（3.2）で動く |
| Codex CLI | `codex exec` が動き、組み込みの image_gen が使えること。最初に1枚生成して確認する |
| Chrome ＋ Claude in Chrome | Tripo Studio にログイン済みのタブを使う。ログインはユーザーが行い、Claude は認証情報を入力しない |
| Pillow（任意） | `<skill>/scripts/contact.py` などの画像スクリプト用。システムの Python がなければ、Blender 同梱の Python で `-m pip install --target <dir> pillow` し、`PYTHONPATH=<dir>` を付けて実行する |

## Windows での注意

- **パス長 260 文字**: Tripo のテクスチャ付き書き出し ZIP は、中の `.fbm` フォルダのパスが長く、深いフォルダに展開すると失敗します。`D:\work\` のような短い作業フォルダに展開・中継し、キットへはフラットに置きます（`<skill>/scripts/stage_tripo_zip.sh`）。展開先と配置先には毎回新しい空のフォルダを指定します（中身があると、何も消さずに止まります）。キットの `export-rig` などの出力先も短いパスにします。
- **ダウンロード先の確認ダイアログ**: Chrome の「ダウンロード前に各ファイルの保存場所を確認する」がオンだと、Tripo の書き出しのたびに OS のダイアログが出ます。オフにするのはユーザーに頼みます（Claude はブラウザやOSの設定を変えない）。
- **シェル**: Git Bash と PowerShell が混在します。Blender への引数は `cygpath -w` で Windows パスに直して渡すと安全です。環境変数付きの実行例（`EA_ARGS='…' "$BLENDER" …`）は Git Bash の書き方で、PowerShell では `$env:EA_ARGS='…'; & $env:BLENDER …` にします。
- **改行コード**: `.sh` が CRLF になると Git Bash で動きません。この Skill は `.gitattributes` で LF に固定しています。ZIP で受け渡すときも LF のまま渡します。
- **容量**: Tripo の返却物（FBX・4K テクスチャ）や作業 Blend は積み重なると大きくなります。ユーザーが C: の容量を気にしている場合は、中間ファイルを別ドライブに置く方針を先に確認します。

## macOS での注意

- Python は `python3` で呼びます（`python` コマンドはない）。
- `.sh` に実行権限がなければ `bash <skill>/scripts/codex_img.sh …` のように bash で呼びます。

## Codex で画像を作るときの約束

- `<skill>/scripts/codex_img.sh <out.png> <prompt.txt> [参照画像...]` を使うと、Codex に「image_gen を1回だけ実行し、生成された PNG を指定パスにコピーする以外は何もしない」と指示して呼び出します。ログは出力先の `logs/` に残ります。実行前に `<out.png>` を消すので、前回の画像を今回の結果と取り違えることはありません。PNG ができなければエラーで止まります。
- 画像の判断（破綻の有無、どこを直すか）、合成、トリミング、透過の確認は Claude が行います。Codex に後処理をさせると、意図しない加工が入ることがあります。
- 透過背景が必要な画像は、生成後にアルファが本当に入っているかを確認します（市松模様の描き込みで「透過っぽく」なっていることがある）。
- 安全フィルタで拒否されることがあります（例: スカート＋脚の背面）。拒否されたら、同じ依頼の繰り返しや通すための言い換えはせず、その面は作らずに部位を1枚の画像で扱う方法へ切り替えて、ユーザーに伝えます（[落とし穴集](pitfalls.md)）。

## 作業ログに残すこと

作業フォルダ（キットの制作フォルダの `work/` など）に、短いログを残しておくと、文脈が切れても再開できます。

- Tripo: 開始時残高、上限、操作ごとの消費、残高
- 採用した候補とその理由（ユーザーの判断）
- 向き・スケールの補正値（例: セグメンテーション返却を Z 軸 +90° 回転）
- ユーザーの好み（例: 首は細め）と、確定した値（例: 全身 150 cm）
