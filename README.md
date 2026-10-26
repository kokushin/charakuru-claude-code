# charakuru-claude-code

日本語 | [English](README.en.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

[きゃらくる（Charakuru）](https://github.com/nanocle/Charakuru) を **Claude Code** で動かして、元絵から揺れもの・表情付きの VRM モデルを作るための Claude Code 用 Skill です。

> **非公式**: この Skill はきゃらくる本家とは別に作られたもので、本家の公式な Skill や配布物ではありません。

きゃらくるは Codex での作業を前提にしたキットです。この Skill は、Claude Code が主担当で回すときの役割分担（画像生成だけ Codex CLI、Tripo Studio はブラウザ操作）、クレジットを使う前の確認地点、実際の制作で起きた問題と直し方を、モデル制作（元絵 → 表情付き VRM）の範囲でまとめています。キットの中身（アプリ、工程別 Skills）は含みません。キットは各自で入手してください。

## 中身

| パス | 内容 |
| --- | --- |
| `SKILL.md` | 全体の流れ、役割分担、判断の原則 |
| `references/setup.md` | 必要な環境、Windows / macOS の注意、Codex で画像を作るときの約束 |
| `references/stages.md` | 工程ごとのメモ（画像素材、Tripo、素材化、頭身、リグ、Tポーズ補正） |
| `references/expressions.md` | 表情制作を背景の Blender で進める方法（融合した唇の縫い目への対処を含む）と、表情付き VRM の書き出し |
| `references/pitfalls.md` | 症状 → 原因 → 直し方の一覧 |
| `scripts/` | bash / Blender / Node の補助スクリプト（下表） |

| スクリプト | 用途 |
| --- | --- |
| `codex_img.sh` | Codex CLI の組み込み image_gen を1回だけ呼び、指定パスに PNG を保存 |
| `stage_tripo_zip.sh` | Tripo のテクスチャ付き ZIP を短いパスに展開してフラットに置く（Windows のパス長対策。既存フォルダは消さない） |
| `rotate_fbx.py` | Tripo の返却 FBX（リグなし）の向きを Z 軸回転で補正 |
| `inspect_rig.py` | 骨の階層・位置、メッシュのウェイト・シェイプキー・材質を一覧 |
| `vrma_arm_angles.mjs` | 動作確認用モーション（VRMA）の腕の角度を確認し、基本姿勢のずれを見つける |
| `fix_tpose.py` | 基本姿勢を真の Tポーズに補正し、前腕・手のコライダーを追加 |
| `ea_run.py` | キットの表情ヘルパーを背景の Blender で attach してスニペットを実行 |
| `ea_zoom.py` | 表情の寄り撮影（カメラのクリップ・状態保存の注意を織り込み済み） |
| `ea_mouth_arcs.py` | 穴のない唇の縫い目から上下の口縁の弧を求める |
| `ea_mouth_parts.py` | 口内の別パーツを唇に追従させ、開口系の表情を拡大 |
| `grid_crop.py` / `contact.py` / `label_grid.py` | 目印を読むための拡大グリッド、比較用のコンタクトシート |
| `make_vrm_expressions.py` | 表情キーを VRM 1.0 の表情に割り当てて、別名の VRM を書き出し（`--no-mouth` で目と眉だけ） |
| `patch_vrm.mjs` | アプリが書き出した VRM のメタデータ（名前・作者・利用条件）を派生 VRM にコピー |

## 使い方

1. このリポジトリを Claude Code の Skill の置き場所に置きます。
   - 全プロジェクトで使う: `~/.claude/skills/charakuru-claude-code/`（Windows は `%USERPROFILE%\.claude\skills\charakuru-claude-code\`）
   - そのプロジェクトだけで使う: `<プロジェクト>/.claude/skills/charakuru-claude-code/`

   ```bash
   git clone https://github.com/kokushin/charakuru-claude-code.git ~/.claude/skills/charakuru-claude-code
   ```

   ZIP でダウンロードした場合は、展開したフォルダの名前を `charakuru-claude-code` にしてから置きます。
2. `BLENDER` 環境変数に Blender の実行ファイルを設定します（[セットアップ](references/setup.md#必要なもの)）。
3. きゃらくるのキットを展開し、`npm start` でアプリを起動します。
4. Claude Code に「きゃらくるでこの元絵からVRMを作って」のように頼むと、この Skill が読み込まれます。各工程はアプリで依頼文を出して Claude Code に渡します。

## 必要なもの

- きゃらくる配布キット、Node.js 22 以上
- Blender 5.2 以降、VRM Add-on for Blender
- Codex CLI（画像生成に使う）
- Chrome と Claude in Chrome（Tripo Studio の操作）、Tripo のアカウントとクレジット
- bash: Windows は [Git for Windows](https://gitforwindows.org/)（Git Bash。`unzip`・`cygpath` も同梱）、macOS は標準の bash で動きます
- 任意: Pillow（比較画像の作成）

作成時の動作環境: きゃらくる 1.1.0、Blender 5.2、Windows（制作）と macOS（検証）。スクリプトはキット内部の関数やファイル配置に依存しているので、キットの更新で動かなくなることがあります。

## 注意

- Tripo の操作はクレジットを消費します。この Skill は、最初にクレジットの上限を合意し、参照画像をユーザーが承認してから生成するよう指示しています。
- きゃらくる本体の利用は、きゃらくるの [LICENSE](https://github.com/nanocle/Charakuru/blob/main/LICENSE)（Charakuru Source-Available License）に従ってください。業務での利用には、売上・資金調達額による条件があります。
- 参照画像などの素材は、それぞれの利用規約に従ってください。VRM のメタデータ（作者・利用条件）はユーザーが決めます。
- 記載の Tripo の設定値は、2026年10月時点の制作例です。
- きゃらくる、Tripo、Codex、Blender などの名称は、それぞれの権利者のものです。

## クレジット

この Skill は、Nano さんが制作・公開している「きゃらくる」を Claude Code で使うためのものです。

- きゃらくる（Charakuru）: https://github.com/nanocle/Charakuru
- 制作: Nano（X: [@Dstudio_ai](https://x.com/Dstudio_ai)）

## ライセンス

この Skill（`SKILL.md`、`references/`、`scripts/`）は [MIT License](LICENSE) です。きゃらくるのキット本体は含まず、その利用条件はキットのライセンスに従います。
