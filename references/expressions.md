# 表情制作を Claude Code で進める

キットの `skills/avatar-expression-authoring/SKILL.md` と `references/commands.md`・`transfer.md` を先に読みます。ここでは、Blender の GUI 操作（Computer Use）なしに、背景の Blender でキット同梱のヘルパー（`<kit>/scripts/expression-studio.py`）を動かして仕上げたやり方を書きます。

## 準備

1. 依頼文の `agent-session.mjs begin` を実行し、`saved: true` を確認。
2. 顔の連結部品を一覧する（`helper.list_blink_parts`、または部品ごとの頂点数・範囲を出す）。制作例の構成は、皮膚（最大の部品）、まつ毛（左右）、虹彩・瞳・ハイライト、二重線、眉（左右）、上唇・下唇の内側パーツ、口内、耳でした。
3. `<kit>/scripts/expression-lab.mjs init` に `objects`（顔メッシュ）と `camera`（顔の中心、正面方向、ortho_scale、size）を渡して作業コピーを作ります。
4. 以降は `<skill>/scripts/ea_run.py` で、作業コピーを開いてヘルパーを attach し、短いスニペット（Python ファイル）を実行する形で進めます。スニペットは `helper`、`bpy`、`show()`（結果を JSON で表示）を使えます。形を変えたら `helper.save()` を呼びます。

```bash
"$BLENDER" -b --factory-startup --python-exit-code 1 --python <skill>/scripts/ea_run.py -- <kit_root> <work_dir> <snippet.py>
```

`ea_mouth_arcs.py` などの引数は環境変数 `EA_ARGS`（JSON）で渡します。上の書き方は Git Bash / macOS 用で、PowerShell では `$env:EA_ARGS='{...}'; & $env:BLENDER -b ...` とします。

## 撮影

- 通常の撮影は `helper.capture(expression, strength, display=..., angles=[...])`。寄りの撮影は `<skill>/scripts/ea_zoom.py` の `zoomed()` で一時的にカメラと表示対象を変えます（髪で顔が隠れるので、構造を見るときは顔メッシュだけを表示する）。
- **カメラの注意**: 撮影カメラは中心から 3×ortho_scale 手前にあり、ニアクリップは 0.1 m です。ortho_scale を 0.06 未満にすると顔がクリップされます。寄りたいときは 0.06 以上で撮り、画像を切り抜きます。中心は顔の位置のままにします（斜めはその中心のまわりを回る）。
- `capture()` は撮影中に `session.json` を保存します。一時的に変えたカメラを戻したら、`helper.record()` で保存し直します（`zoomed()` がそうしている）。
- 見比べは、ラベル付きのグリッド（`<skill>/scripts/label_grid.py`）にまとめると速いです。最後は髪付き・MToon で全表情と組み合わせ（目を閉じた笑顔、喜び、怒り、悲しみ、驚き、話しながらのまばたき）を顔サイズで確認します。

## 目

- 8点（目頭・目尻・上縁・下縁 × 左右）は、正面の撮影画像の画素から `helper.set_blink_pixels()` で指定できます。皮膚だけを同じカメラで高解像度に撮り、`<skill>/scripts/grid_crop.py` に作業フォルダの `session.json` を渡して、セッションのカメラ（`camera.size`）の画素座標を書き込んだ拡大図を作ると、座標を正確に読めます。L はカメラから見て右（モデルの左目）です。
- 目の白目が皮膚に描かれ、くぼんだ面になっている構造でも、開口縁（まつ毛の帯の下端と白目の下端）に点を置けばフィットします。
- 追従部品にはまつ毛と二重線を入れます。虹彩・瞳は入れません（閉じた瞼の裏に隠れる）。
- `helper.transfer_eyes(reviewed=True)` で8表情を転送したら、まばたき 1.0・0.5 を正面・斜め・横で確認します。

## 口（縫い目が融合している場合）

Tripo 由来の顔では、上下唇の縫い目に穴がなく、口の奥に閉じた袋（口内）がある構造が多いです。境界辺がないので `helper.mouth_paths()` は使えません。

> **先に確認すること**: 実際の制作では、下の手順で口を開けられるようにしても、ふくらんだ唇の中央に小さな穴が開いたように見え、ユーザーが違和感を持ちました。口の動きの調整、頭の再生成（同じ構造が出た）、描いた口パーツへの置き換えも試しましたが採用されず、最終的に **口の表情は見送り、目と眉だけで表情を作りました**。口の表情を作る前に、開いた口の試作を1〜2個（あ・笑顔）だけ作ってユーザーに見せ、方針を決めてから全表情へ進めてください。目と眉だけでも表情は成立します。口を見送る場合は、下の表情付き VRM の書き出しで `--no-mouth` を付けます（試作した口のキーが残っていても VRM に入りません）。

1. `<skill>/scripts/ea_mouth_arcs.py` で、口の縫い目の頂点を「上の袋（天井）につながる行」と「下の袋（床）につながる行」に分け、**上下の行が辺でつながっていない中央部分**の端を口角として、上下の弧を作ります。口角側で上下の行が辺でつながっている部分を口縁に含めると、開いたときにその面が縦に伸びて、白い三角（牙のような形）になります。
2. `helper.prepare_mouth()` → `helper.capture_mouth_fit()` で、赤（上唇）と青（下唇）の弧を確認してから `transfer_mouth(reviewed=True)`。
3. 唇の内側や口内が別パーツなら、`<skill>/scripts/ea_mouth_parts.py` で、上の部品は上唇の弧、下の部品は下唇の弧の動きに追従させます。弧の動きを x の2次式で近似してから当てると、部品が山形に折れません。開く量に応じて、部品の縁を唇の裏へ少し引っ込めます。
4. 開口が唇線の中央だけなので、鑑賞サイズで小さく見えます。開口系（あ・い・う・え・お・驚き）だけ、皮膚の変位を 1.3〜1.5 倍にし、内側部品を追従させ直します（`ea_mouth_parts.py` の `gain`。倍率は転送したキーに対する値なので、同じ値で再実行しても重なりません）。
5. 口を開けた状態は、正面・斜め・横と中間値（0.5）で確認します。

## 眉

- 左右の眉が独立部品なら `helper.prepare_brows({'L': ..., 'R': ...})` → `transfer_brows(reviewed=True)`。L/R はモデルの左右です。
- 前髪で眉が隠れるモデルでは、眉の表情は鑑賞サイズではほとんど見えません。見える範囲で破綻がなければ十分です。

## 保存と登録

```python
helper.note('差', '変更', '観察', '次の一手', 'ready_for_review')
helper.save(export=True)
```

```bash
node <kit>/scripts/expression-lab.mjs register <work_dir> <project.charakit>
node <kit>/scripts/agent-session.mjs complete <url> <request_id> "目8・眉5を制作して登録しました（口は見送り）"
```

完了メッセージには実際に作った表情の内訳を書きます（上は口を見送った場合の例）。

アプリの表情制作タブで表情一覧が出ることを確認します。プレビューで強度を変えたら、「この表情を戻す」で 0 に戻しておきます（調整値は正本に保存されるため）。

表情はキットの方針どおり既存 VRM には自動で入りません。VRM で使いたい場合は、次の手順で表情付きの VRM を別名で作ります。

## 表情付き VRM を別名で書き出す

キットの正式出力 `exports/avatar.vrm` は変更しません。派生ファイルとして書き出します。

```bash
"$BLENDER" -b --factory-startup --python-exit-code 1 --python <skill>/scripts/make_vrm_expressions.py -- \
  <kit_root> <project>/exports/avatar.blend \
  <project>/work/expression-authoring/exports/expressions.blend out/model_expressions.vrm [--no-mouth]
node <skill>/scripts/patch_vrm.mjs out/model_expressions.vrm out/model_expressions.vrm --meta-from <project>/exports/avatar.vrm
```

- `make_vrm_expressions.py` は、表情作業 Blend の顔メッシュから `EA_*` キーを `avatar.blend` の同じ顔メッシュへ写し（基本形が一致することを検査）、VRM 1.0 の表情に割り当てて書き出します。
  - blink / blinkLeft / blinkRight、aa / ih / ou / ee / oh はそれぞれ1キー。動いていないキー（転送していない `EA_aa` など）と、`--no-mouth` のときの口のキーは割り当てません。
  - happy / angry / sad / relaxed / surprised は「目＋口＋眉」の組み合わせ（眉は 0.6〜1.0）。目の形を含むので、まばたきの上書きは `blend`（驚きは `block`）。
  - カスタム表情 `smile` = まばたき＋笑顔の口＋眉（目を閉じた笑顔）。
- アプリはモデル名・作者・利用条件を VRM の書き出し時に直接書き込むので、`avatar.blend` から書き出すとメタが `undefined` になります。`patch_vrm.mjs --meta-from` で、アプリが書き出した VRM のメタをコピーします。
- 書き出すのは、アプリが書き出した `exports/avatar.vrm` に入っているメッシュだけです（`--reference-vrm` で別の VRM も指定可）。`avatar.blend` にはウェイト転送用の素体（`…_FittedDonor`）がリグに結び付いたまま入っていますが、これは書き出されません。先にアプリで「VRMを書き出す」を済ませておきます。
- 出力先のフォルダはなければ作り、同名の古いファイルは書き出し前に消します。書き出しに失敗するとエラーで止まります。
- 書き出した VRM は、キットのアプリ（動作確認）や VRM 対応ビューアで読み込み、各表情が動くことを確かめます。
