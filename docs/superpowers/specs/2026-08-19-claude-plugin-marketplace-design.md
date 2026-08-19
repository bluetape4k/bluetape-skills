# Claude Code Plugin Marketplace 지원 설계

- Status: Approved
- Date: 2026-08-19
- Author: jeff.dean (with Claude)

## 배경

`bluetape-skills`는 현재 [Codex skills](https://developers.openai.com/codex/skills/) 전용
공개 배포 저장소다(`skills/`, `skills/manifest.json`, `scripts/install.sh`,
`scripts/validate.sh`). 이 저장소를 Claude Code plugin marketplace로도 사용할 수 있도록
확장한다.

## 목표

- 기존 Codex 배포 경로(설치, 검증, manifest)는 변경 없이 그대로 유지한다.
- 동일한 저장소에서 Claude Code 사용자가 `/plugin marketplace add` /
  `/plugin install`로 동일한 스킬 세트를 설치할 수 있게 한다.
- 스킬 콘텐츠(`skills/*/SKILL.md` 등)는 복제·심볼릭 링크 없이 원본 그대로
  재사용한다.

## 목표가 아닌 것

- `skills/*/SKILL.md` 본문 안의 Codex 전용 표현(`$bluetape-workflow` 트리거
  문법, `CODEX_HOME` 경로 참조 등)을 Claude 전용 문구로 다시 쓰는 일. Claude
  Code도 동일한 SKILL.md frontmatter(`name`, `description`)를 읽으므로 동작에는
  영향이 없다.
- 스킬을 개별 플러그인으로 쪼개는 일 (하나의 통합 플러그인으로 배포한다).
- `scripts/install.sh`, `skills/manifest.json` 변경.

## 결정 사항

| 항목 | 결정 |
| --- | --- |
| 배포 범위 | Codex 배포 유지 + Claude marketplace 신규 추가 (이중 배포) |
| 플러그인 단위 | 스킬 14개를 하나의 플러그인 `bluetape-skills`로 통합 |
| 콘텐츠 재사용 | `skills/*/SKILL.md` 원본 그대로, 복사/치환 없음 |
| 플러그인 루트 | 저장소 루트 자체 (`.claude-plugin/`를 루트에 추가, `skills/`는 자동 탐색) |
| owner 정보 | `bluetape4k` + README의 GitHub URL 포함 |
| 버전 | 기존 CHANGELOG/태그(`1.3.4`)와 동일 문자열 사용, 이후 함께 범프 |

## 구조 변경

### 신규 파일

```
.claude-plugin/
├── plugin.json
└── marketplace.json
```

`.claude-plugin/plugin.json`:

```json
{
  "name": "bluetape-skills",
  "displayName": "Bluetape Skills",
  "version": "1.3.4",
  "description": "Installable, canonical Codex/Claude skills for Bluetape development workflows.",
  "author": { "name": "bluetape4k" },
  "homepage": "https://github.com/bluetape4k/bluetape-skills",
  "repository": "https://github.com/bluetape4k/bluetape-skills",
  "license": "MIT",
  "keywords": ["bluetape", "workflow", "kotlin", "codex"]
}
```

`skills` 필드는 명시하지 않는다 — 필드가 없으면 Claude Code가 최상위 `skills/`
디렉토리를 자동 탐색하므로, `skills/manifest.json`이 관리하는 14개 스킬이
그대로 노출된다.

`.claude-plugin/marketplace.json`:

```json
{
  "name": "bluetape-skills",
  "owner": { "name": "bluetape4k", "url": "https://github.com/bluetape4k/bluetape-skills" },
  "description": "Bluetape Skills marketplace",
  "version": "1.3.4",
  "plugins": [
    {
      "name": "bluetape-skills",
      "source": "./",
      "description": "Canonical Bluetape workflow, language, and publishing skills",
      "version": "1.3.4"
    }
  ]
}
```

`bluetape-skills`는 Claude Code의 예약 마켓플레이스 이름 목록
(`claude-code-marketplace`, `claude-plugins-official`, `anthropic-plugins`,
`first-party-plugins`, `healthcare` 등)과 충돌하지 않는다.

### 변경 파일

- `README.md`, `README.ko.md`: "Install" 섹션 뒤에 "Claude Code plugin
  marketplace로 설치" 하위 섹션 추가.
  ```
  /plugin marketplace add bluetape4k/bluetape-skills
  /plugin install bluetape-skills@bluetape-skills
  ```
  기존 SKILL.md 본문의 `$skill-name` 트리거 문법은 Codex 표기이며 Claude
  Code에서는 스킬 이름으로 자동 인식된다는 안내를 덧붙인다.
- `scripts/validate.sh`: 기존 Codex 번들 검증에 더해, `.claude-plugin/*.json`
  두 파일이 유효한 JSON이고 필수 필드(plugin.json의 `name`, marketplace.json의
  `name`/`owner`/`plugins`)를 갖췄는지 확인하는 단계를 추가한다. `claude` CLI가
  PATH에 있으면 `claude plugin validate .`를 우선 시도하고, 없으면 Python
  `json.load` 기반 최소 검증으로 폴백한다.
- `CHANGELOG.md`: `[Unreleased]`에 "Claude Code plugin marketplace 지원 추가"
  항목 기록.

### 변경하지 않는 파일

- `skills/*/SKILL.md` 및 하위 리소스 전체
- `skills/manifest.json`
- `scripts/install.sh`
- `AGENTS.md`

## 에러 처리 / 엣지 케이스

- `validate.sh`에 `claude` CLI가 없는 실행 환경(CI 등)에서도 실패하지 않도록
  JSON 유효성 폴백 경로를 반드시 둔다.
- marketplace.json의 `strict` 기본값(true)에 따라 `plugin.json`이 권위 소스가
  되므로, 두 파일의 `name`/`version`이 어긋나지 않도록 값을 동일하게 유지한다.
- 향후 버전을 올릴 때 `plugin.json`, `marketplace.json`, `CHANGELOG.md`,
  `README.md` 예시의 버전 문자열을 함께 갱신해야 한다는 점을 README에 명시한다.

## 테스트 계획

- `./scripts/validate.sh` 실행 — 기존 Codex 검증 스위트 + 신규 plugin/marketplace
  JSON 검증 단계가 모두 통과하는지 확인.
- `claude plugin validate .` (CLI 존재 시) 실행 결과가
  `✔ Validation passed`인지 확인.
- 로컬 스모크 테스트: `/plugin marketplace add ./` 후 `/plugin install
  bluetape-skills@bluetape-skills`로 설치 흐름이 에러 없이 완료되는지 수동 확인
  (가능한 환경에서).

## 롤아웃

- `develop` 브랜치에서 작업 후 기존 릴리스 프로세스(리뷰 → `main` 승격 →
  태그)를 그대로 따른다. 이번 변경만으로 새 버전을 태깅할 필요는 없으며, 다음
  정기 릴리스에 포함한다.
