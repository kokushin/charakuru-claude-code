# charakuru-claude-code

[日本語](README.md) | [English](README.en.md) | 简体中文 | [한국어](README.ko.md)

这是一个 Claude Code Skill，用于通过 **Claude Code** 运行 [Charakuru（きゃらくる）](https://github.com/nanocle/Charakuru)，从原图制作带物理（摇摆部件）和表情的 VRM 模型。

> **非官方**：本 Skill 独立于 Charakuru 项目制作，并非 Charakuru 官方的 Skill 或分发物。

Charakuru 是以使用 Codex 为前提设计的套件。本 Skill 面向由 Claude Code 担任主要 Agent 的情况，在模型制作（原图 → 带表情的 VRM）的范围内，整理了分工（图片生成只交给 Codex CLI，Tripo Studio 通过浏览器操作）、消耗积分前的确认点，以及实际制作中遇到的问题和解决方法。本仓库不包含套件本身（应用和各阶段的 Skills），请自行获取套件。

## 内容

| 路径 | 内容 |
| --- | --- |
| `SKILL.md` | 整体流程、分工、判断原则 |
| `references/setup.md` | 所需环境、Windows / macOS 注意事项、用 Codex 生成图片时的约定 |
| `references/stages.md` | 各阶段笔记（图片素材、Tripo、素材化、头身比例、绑定、T 姿势修正） |
| `references/expressions.md` | 在后台 Blender 中制作表情的方法（包括处理融合在一起的唇缝），以及导出带表情的 VRM |
| `references/pitfalls.md` | 症状 → 原因 → 解决方法一览 |
| `scripts/` | bash / Blender / Node 辅助脚本（见下表） |

| 脚本 | 用途 |
| --- | --- |
| `codex_img.sh` | 只调用一次 Codex CLI 内置的 image_gen，将 PNG 保存到指定路径 |
| `stage_tripo_zip.sh` | 将 Tripo 带纹理的 ZIP 解压到短路径，并把文件平铺放置（应对 Windows 路径长度限制，不会删除已有文件夹） |
| `rotate_fbx.py` | 通过绕 Z 轴旋转，修正 Tripo 返回的 FBX（无绑定）的朝向 |
| `inspect_rig.py` | 列出骨骼层级与位置，以及网格的权重、形态键和材质 |
| `vrma_arm_angles.mjs` | 检查动作确认用动作（VRMA）的手臂角度，找出基本姿势的偏差 |
| `fix_tpose.py` | 将基本姿势修正为真正的 T 姿势，并添加前臂和手部碰撞体 |
| `ea_run.py` | 在后台 Blender 中挂载套件的表情辅助工具并执行代码片段 |
| `ea_zoom.py` | 表情特写拍摄（已考虑相机裁剪和状态保存方面的注意事项） |
| `ea_mouth_arcs.py` | 从没有开口的唇缝中求出上下唇缘的弧线 |
| `ea_mouth_parts.py` | 让口腔内的独立部件跟随嘴唇，并放大张嘴类表情 |
| `grid_crop.py` / `contact.py` / `label_grid.py` | 用于读取标记点的放大网格，以及用于比较的拼图 |
| `make_vrm_expressions.py` | 将表情键分配给 VRM 1.0 表情，并另存为新的 VRM（`--no-mouth` 时仅含眼睛和眉毛） |
| `patch_vrm.mjs` | 将应用导出的 VRM 的元数据（名称、作者、使用条件）复制到派生的 VRM |

## 使用方法

1. 将本仓库放到 Claude Code 的 Skill 目录中。
   - 用于所有项目：`~/.claude/skills/charakuru-claude-code/`（Windows 为 `%USERPROFILE%\.claude\skills\charakuru-claude-code\`）
   - 仅用于某个项目：`<项目>/.claude/skills/charakuru-claude-code/`

   ```bash
   git clone https://github.com/kokushin/charakuru-claude-code.git ~/.claude/skills/charakuru-claude-code
   ```

   如果下载的是 ZIP，请先将解压后的文件夹重命名为 `charakuru-claude-code`，再放入上述目录。
2. 将 Blender 可执行文件的路径设置到环境变量 `BLENDER`（[设置](references/setup.md#必要なもの)，日文）。
3. 解压 Charakuru 套件，用 `npm start` 启动应用。
4. 向 Claude Code 提出类似“用 Charakuru 把这张原图做成 VRM”的请求，即会加载本 Skill。每个阶段都在应用中生成 Agent 请求，再交给 Claude Code。

## 所需环境

- Charakuru 分发套件（Releases 中的 ZIP）、Node.js 22 及以上
- Blender 5.2 及以上、VRM Add-on for Blender
- Codex CLI（用于图片生成）
- Chrome 与 Claude in Chrome（用于操作 Tripo Studio）、Tripo 账户与积分
- bash：Windows 使用 [Git for Windows](https://gitforwindows.org/)（Git Bash，附带 `unzip` 和 `cygpath`），macOS 使用系统自带的 bash 即可
- 可选：Pillow（用于制作对比图）

编写时的运行环境：Charakuru 1.1.0、Blender 5.2、Windows（制作）和 macOS（验证）。脚本依赖套件内部的函数和文件结构，套件更新后可能无法运行。

## 注意事项

- Tripo 的操作会消耗积分。本 Skill 要求先约定积分上限，并在用户批准参考图之后再生成。
- Charakuru 本身的使用请遵守其 [LICENSE](https://github.com/nanocle/Charakuru/blob/main/LICENSE)（Charakuru Source-Available License）。业务使用需满足基于收入和融资额的条件。
- 参考图等素材请遵守各自的使用条款。VRM 的元数据（作者、使用条件）由用户决定。
- 文中 Tripo 的设置值为 2026 年 10 月的制作示例。
- Charakuru、Tripo、Codex、Blender 等名称归各自的权利人所有。

## 致谢

本 Skill 用于通过 Claude Code 使用 Nano 制作并公开的 Charakuru。

- Charakuru（きゃらくる）：https://github.com/nanocle/Charakuru
- 制作：Nano（X：[@Dstudio_ai](https://x.com/Dstudio_ai)）

## 许可

本 Skill（`SKILL.md`、`references/`、`scripts/`）采用 [MIT License](LICENSE)。本仓库不包含 Charakuru 套件本身，套件的使用条件以套件的许可为准。
