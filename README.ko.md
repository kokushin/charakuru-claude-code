# charakuru-claude-code

[日本語](README.md) | [English](README.en.md) | [简体中文](README.zh-CN.md) | 한국어

[Charakuru(きゃらくる)](https://github.com/nanocle/Charakuru)를 **Claude Code**로 실행해, 원본 일러스트로부터 흔들리는 부위와 표정이 들어간 VRM 모델을 만들기 위한 Claude Code용 Skill입니다.

> **비공식**: 이 Skill은 Charakuru 본가와 별도로 만들어졌으며, Charakuru의 공식 Skill이나 배포물이 아닙니다.

Charakuru는 Codex로 작업하는 것을 전제로 한 키트입니다. 이 Skill은 Claude Code가 주 담당으로 작업할 때의 역할 분담(이미지 생성만 Codex CLI, Tripo Studio는 브라우저 조작), 크레딧을 쓰기 전의 확인 지점, 실제 제작에서 생긴 문제와 해결 방법을 모델 제작(원본 일러스트 → 표정이 들어간 VRM) 범위에서 정리한 것입니다. 키트 자체(앱, 공정별 Skills)는 포함하지 않습니다. 키트는 각자 받아 주세요.

## 구성

| 경로 | 내용 |
| --- | --- |
| `SKILL.md` | 전체 흐름, 역할 분담, 판단 원칙 |
| `references/setup.md` | 필요한 환경, Windows / macOS 주의점, Codex로 이미지를 만들 때의 약속 |
| `references/stages.md` | 공정별 메모(이미지 소재, Tripo, 소재화, 등신 비율, 리깅, T포즈 보정) |
| `references/expressions.md` | 백그라운드 Blender로 표정을 제작하는 방법(붙어 있는 입술 이음매 대처 포함)과 표정이 들어간 VRM 내보내기 |
| `references/pitfalls.md` | 증상 → 원인 → 해결 방법 목록 |
| `scripts/` | bash / Blender / Node 보조 스크립트(아래 표) |

| 스크립트 | 용도 |
| --- | --- |
| `codex_img.sh` | Codex CLI의 내장 image_gen을 한 번만 호출해 지정한 경로에 PNG를 저장 |
| `stage_tripo_zip.sh` | Tripo의 텍스처 포함 ZIP을 짧은 경로에 풀고 파일을 한 폴더에 평평하게 배치(Windows 경로 길이 제한 대책. 기존 폴더는 지우지 않음) |
| `rotate_fbx.py` | Tripo에서 돌려받은 FBX(리그 없음)의 방향을 Z축 회전으로 보정 |
| `inspect_rig.py` | 본의 계층·위치와 메시의 웨이트·셰이프 키·재질을 목록으로 출력 |
| `vrma_arm_angles.mjs` | 동작 확인용 모션(VRMA)의 팔 각도를 확인해 기본 자세의 어긋남을 찾음 |
| `fix_tpose.py` | 기본 자세를 정확한 T포즈로 보정하고 아래팔·손 콜라이더를 추가 |
| `ea_run.py` | 키트의 표정 헬퍼를 백그라운드 Blender에 attach하고 스니펫을 실행 |
| `ea_zoom.py` | 표정 클로즈업 촬영(카메라 클리핑·상태 저장 관련 주의점 반영) |
| `ea_mouth_arcs.py` | 구멍이 없는 입술 이음매에서 위아래 입술 가장자리의 호를 구함 |
| `ea_mouth_parts.py` | 입안의 별도 파츠가 입술을 따라 움직이게 하고, 입을 벌리는 표정을 확대 |
| `grid_crop.py` / `contact.py` / `label_grid.py` | 기준점을 읽기 위한 확대 격자, 비교용 콘택트 시트 |
| `make_vrm_expressions.py` | 표정 키를 VRM 1.0 표정에 할당해 다른 이름의 VRM으로 내보내기(`--no-mouth`는 눈과 눈썹만) |
| `patch_vrm.mjs` | 앱이 내보낸 VRM의 메타데이터(이름·작성자·이용 조건)를 파생 VRM에 복사 |

## 사용 방법

1. 이 저장소를 Claude Code의 Skill 위치에 둡니다.
   - 모든 프로젝트에서 사용: `~/.claude/skills/charakuru-claude-code/`(Windows는 `%USERPROFILE%\.claude\skills\charakuru-claude-code\`)
   - 해당 프로젝트에서만 사용: `<프로젝트>/.claude/skills/charakuru-claude-code/`

   ```bash
   git clone https://github.com/kokushin/charakuru-claude-code.git ~/.claude/skills/charakuru-claude-code
   ```

   ZIP으로 다운로드한 경우 압축을 푼 폴더 이름을 `charakuru-claude-code`로 바꾼 뒤 둡니다.
2. `BLENDER` 환경 변수에 Blender 실행 파일을 설정합니다([설정](references/setup.md#必要なもの), 일본어).
3. Charakuru 키트를 풀고 `npm start`로 앱을 실행합니다.
4. Claude Code에 "Charakuru로 이 일러스트를 VRM으로 만들어 줘"처럼 요청하면 이 Skill이 로드됩니다. 각 공정은 앱에서 요청문을 만들어 Claude Code에 전달합니다.

## 필요한 것

- Charakuru 배포 키트(Releases의 ZIP), Node.js 22 이상
- Blender 5.2 이상, VRM Add-on for Blender
- Codex CLI(이미지 생성용)
- Chrome과 Claude in Chrome(Tripo Studio 조작), Tripo 계정과 크레딧
- bash: Windows는 [Git for Windows](https://gitforwindows.org/)(Git Bash. `unzip`·`cygpath`도 포함), macOS는 기본 bash로 동작합니다
- 선택: Pillow(비교 이미지 생성)

작성 시 동작 환경: Charakuru 1.1.0, Blender 5.2, Windows(제작)와 macOS(검증). 스크립트는 키트 내부의 함수와 파일 배치에 의존하므로, 키트 업데이트로 동작하지 않게 될 수 있습니다.

## 주의

- Tripo 조작은 크레딧을 소비합니다. 이 Skill은 먼저 크레딧 상한을 합의하고, 사용자가 참조 이미지를 승인한 뒤에 생성하도록 지시합니다.
- Charakuru 본체의 이용은 Charakuru의 [LICENSE](https://github.com/nanocle/Charakuru/blob/main/LICENSE)(Charakuru Source-Available License)를 따르세요. 업무상 이용에는 매출·자금 조달액에 따른 조건이 있습니다.
- 참조 이미지 등의 소재는 각각의 이용 약관을 따르세요. VRM 메타데이터(작성자·이용 조건)는 사용자가 정합니다.
- 기재된 Tripo 설정값은 2026년 10월 시점의 제작 예입니다.
- Charakuru, Tripo, Codex, Blender 등의 명칭은 각 권리자에게 귀속됩니다.

## 크레딧

이 Skill은 Nano 님이 제작·공개한 Charakuru를 Claude Code에서 사용하기 위한 것입니다.

- Charakuru(きゃらくる): https://github.com/nanocle/Charakuru
- 제작: Nano(X: [@Dstudio_ai](https://x.com/Dstudio_ai))

## 라이선스

이 Skill(`SKILL.md`, `references/`, `scripts/`)은 [MIT License](LICENSE)입니다. Charakuru 키트 본체는 포함하지 않으며, 키트의 이용 조건은 키트의 라이선스를 따릅니다.
