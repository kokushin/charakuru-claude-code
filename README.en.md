# charakuru-claude-code

[日本語](README.md) | English | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

A Claude Code skill for running [Charakuru (きゃらくる)](https://github.com/nanocle/Charakuru) with **Claude Code** to turn a character illustration into a VRM model with spring bones and expressions.

> **Unofficial**: This skill was made independently of Charakuru. It is not an official skill or distribution of the Charakuru project.

Charakuru is a kit designed for working with Codex. This skill covers what changes when Claude Code is the main agent instead, within model production (source illustration → VRM with expressions): who does what (Codex CLI for image generation only, Tripo Studio through browser control), the checkpoints before spending credits, and the problems that came up in a real production and how they were fixed. It does not include the kit itself (the app and its per-stage Skills); get the kit separately.

## Contents

| Path | Description |
| --- | --- |
| `SKILL.md` | Overall flow, division of roles, guiding principles |
| `references/setup.md` | Requirements, Windows / macOS notes, rules for generating images with Codex |
| `references/stages.md` | Notes for each stage (image assets, Tripo, materials, proportions, rigging, T-pose fix) |
| `references/expressions.md` | Authoring expressions with Blender in the background (including fused lip seams) and exporting a VRM with expressions |
| `references/pitfalls.md` | Symptom → cause → fix |
| `scripts/` | bash / Blender / Node helper scripts (below) |

| Script | Purpose |
| --- | --- |
| `codex_img.sh` | Calls Codex CLI's built-in image_gen exactly once and saves the PNG to the given path |
| `stage_tripo_zip.sh` | Extracts a Tripo textured ZIP to a short path and lays the files out flat (works around the Windows path length limit; never deletes existing folders) |
| `rotate_fbx.py` | Fixes the orientation of an unrigged FBX returned by Tripo with a Z-axis rotation |
| `inspect_rig.py` | Lists the bone hierarchy and positions, and mesh weights, shape keys and materials |
| `vrma_arm_angles.mjs` | Checks the arm angles in the motion-check VRMA to find a rest-pose offset |
| `fix_tpose.py` | Corrects the rest pose to a true T-pose and adds forearm and hand colliders |
| `ea_run.py` | Attaches the kit's expression helper in background Blender and runs a snippet |
| `ea_zoom.py` | Close-up expression captures (handles the camera clipping and session-state pitfalls) |
| `ea_mouth_arcs.py` | Finds the upper and lower lip arcs on a lip seam that has no opening |
| `ea_mouth_parts.py` | Makes separate inner-mouth parts follow the lips and enlarges open-mouth expressions |
| `grid_crop.py` / `contact.py` / `label_grid.py` | Zoomed grids for reading landmarks, contact sheets for comparison |
| `make_vrm_expressions.py` | Binds expression keys to VRM 1.0 expressions and exports a separate VRM (`--no-mouth` for eyes and brows only) |
| `patch_vrm.mjs` | Copies the metadata (name, authors, usage terms) of the app-exported VRM into a derived VRM |

## Usage

1. Put this repository where Claude Code looks for skills.
   - For all projects: `~/.claude/skills/charakuru-claude-code/` (Windows: `%USERPROFILE%\.claude\skills\charakuru-claude-code\`)
   - For one project only: `<project>/.claude/skills/charakuru-claude-code/`

   ```bash
   git clone https://github.com/kokushin/charakuru-claude-code.git ~/.claude/skills/charakuru-claude-code
   ```

   If you downloaded a ZIP, rename the extracted folder to `charakuru-claude-code` before putting it there.
2. Set the `BLENDER` environment variable to the Blender executable ([setup](references/setup.md#必要なもの), in Japanese).
3. Extract the Charakuru kit and start the app with `npm start`.
4. Ask Claude Code something like "Make a VRM from this illustration with Charakuru" and the skill is loaded. For each stage, create the agent request in the app and pass it to Claude Code.

## Requirements

- The Charakuru kit (release ZIP), Node.js 22 or later
- Blender 5.2 or later, VRM Add-on for Blender
- Codex CLI (for image generation)
- Chrome and Claude in Chrome (to operate Tripo Studio), a Tripo account and credits
- bash: on Windows, [Git for Windows](https://gitforwindows.org/) (Git Bash, which also ships `unzip` and `cygpath`); on macOS, the stock bash works
- Optional: Pillow (for comparison images)

Tested with: Charakuru 1.1.0, Blender 5.2, Windows (production) and macOS (verification). The scripts depend on functions and the file layout inside the kit, so kit updates may break them.

## Notes

- Tripo operations consume credits. This skill tells Claude to agree on a credit limit first and to generate only after the user approves the reference images.
- Use of Charakuru itself is governed by its [LICENSE](https://github.com/nanocle/Charakuru/blob/main/LICENSE) (Charakuru Source-Available License). Business use is subject to conditions based on revenue and funding.
- Follow the terms of each asset, such as reference images. The user decides the VRM metadata (authors, usage terms).
- The Tripo settings mentioned are examples from a production in October 2026.
- Charakuru, Tripo, Codex, Blender and other names belong to their respective owners.

## Credits

This skill is for using Charakuru, created and published by Nano, with Claude Code.

- Charakuru (きゃらくる): https://github.com/nanocle/Charakuru
- Created by: Nano (X: [@Dstudio_ai](https://x.com/Dstudio_ai))

## License

This skill (`SKILL.md`, `references/`, `scripts/`) is licensed under the [MIT License](LICENSE). It does not include the Charakuru kit, whose use is governed by the kit's own license.
