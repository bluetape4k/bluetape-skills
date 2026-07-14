# Bluetape Skills

[English](README.md) | 한국어

Bluetape 개발 워크플로를 위한 설치 가능한 canonical [Codex skill](https://developers.openai.com/codex/skills/) 묶음입니다. 각 skill에는 실행에 필요한 reference, template, script, agent prompt를 함께 넣습니다. 반면 retired alias와 개인 런타임 상태는 의도적으로 배포하지 않습니다.

## 무엇을 공유하나

이 저장소는 관리자의 Codex 홈을 그대로 복제한 것이 아니라, 다른 개발자가 설치할 수 있도록 구성한 공개 배포본입니다. 재사용 가능한 skill 단위는 필요한 자료와 함께 온전히 제공하고, 사용자별 설정과 런타임 데이터는 배포 경계 밖에 둡니다.

[![공개 배포 경계: canonical Bluetape skill과 재사용 가능한 자료는 포함하고 개인 런타임 상태는 제외합니다](docs/images/bluetape-skills-public-bundle-boundary-01.png)](docs/images/bluetape-skills-public-bundle-boundary-01.svg)

## 설치

안정 버전을 복제하고 배포본을 검증한 뒤 설치 스크립트를 실행합니다.

```bash
git clone --branch v1.1.0 --depth 1 https://github.com/bluetape4k/bluetape-skills.git
cd bluetape-skills
./scripts/validate.sh
./scripts/install.sh
```

검증에는 Bash, `rg`, Python 3, `uv`가 필요합니다. 검증 스크립트는 공개 배포 경계와 workflow contract를 확인한 뒤, 임시 `uv` 환경에서 함께 배포한 workflow 회귀 테스트를 실행합니다.

설치 대상은 `${CODEX_HOME:-~/.codex}/skills`입니다. 동일한 canonical skill이 이미 있으면 설치 스크립트는 덮어쓰지 않고 멈춥니다. 교체가 필요할 때만 `--force`를 사용하세요. 기존 skill은 타임스탬프가 붙은 백업 디렉터리로 먼저 옮깁니다.

```bash
./scripts/install.sh --dry-run
./scripts/install.sh --codex-home "$HOME/.codex"
./scripts/install.sh --force
```

설치 뒤에는 Codex를 다시 시작해야 새 skill을 인식합니다.

아직 릴리스되지 않은 변경까지 따라가려면 `--branch v1.1.0 --depth 1` 옵션을 빼고 `main`을 복제하세요. 공개 버전과 다운로드 가능한 묶음은 [GitHub Releases](https://github.com/bluetape4k/bluetape-skills/releases)에서 확인할 수 있습니다.

## 업데이트

릴리스 태그는 변경되지 않습니다. 안정 설치본을 갱신하려면 원하는 새 태그를 별도 디렉터리에 복제하고 검증한 뒤, 기존 skill을 백업하면서 교체하세요.

```bash
git clone --branch v1.1.0 --depth 1 https://github.com/bluetape4k/bluetape-skills.git bluetape-skills-v1.1.0
cd bluetape-skills-v1.1.0
./scripts/validate.sh
./scripts/install.sh --force
```

의도적으로 `main`을 추적하는 checkout만 현재 브랜치에서 갱신합니다.

```bash
git pull --ff-only
./scripts/validate.sh
./scripts/install.sh --force
```

설치본을 강제로 교체하기 전, 로컬에서 수정한 내용이 있다면 `git log`와 `git diff`를 먼저 확인하세요.

## 사용

Bluetape 생태계 작업은 `$bluetape-workflow`부터 시작하세요. 작업을 분류한 뒤 가장 가벼운 안전한 경로로 연결합니다.

[![Workflow router: Bluetape 작업을 분류하고 알맞은 skill 경로로 연결합니다](docs/images/bluetape-workflow-type-router-01.png)](docs/images/bluetape-workflow-type-router-01.svg)

| 필요한 작업 | 사용할 skill |
| --- | --- |
| 재현 가능한 결함 수정 | `$bluetape-bugfix` |
| 범위가 작은 변경 | `$bluetape-fast-track` |
| 새 모듈, 의존성, 넓은 API 변경 | `$bluetape-full-feature` |
| Kotlin/JVM 구현 | `$bluetape-kotlin-patterns` |
| Go, Python, Rust 작업 | `$bluetape-go-patterns`, `$bluetape-py-patterns`, `$bluetape-rs-patterns` |
| 문서·현지화 | `$bluetape-writer` |
| 다이어그램·차트 | `$bluetape-diagram` |
| JVM·Go 배포 | `$bluetape-publish-jvm`, `$bluetape-publish-go` |

`skills/manifest.json`은 기계가 읽을 수 있는 inventory입니다. skill 디렉터리에는 `SKILL.md`뿐 아니라 연결된 자료도 있으므로, `SKILL.md`만 따로 복사하지 말고 디렉터리 전체를 설치해야 합니다.

## Native workflow runtime

1.1.0부터 `$bluetape-workflow`에 Phase 2 native runtime이 포함됩니다. Manifest 1.1은 run과 lane 수명주기, liveness 판정, topology 기반 완료 조건, receipt 기반 복구, 크기가 제한된 evidence를 정의합니다. `.bluetape` workflow state는 guarded CLI인 `bluetape-flow.py`만 기록합니다.

이 CLI는 native coordination을 기록하고 검증하지만 Codex agent tool을 대신하지는 않습니다. Agent 생성, 메시지 전송, 대기, 중단은 main session이 직접 수행한 뒤 관찰한 결과를 기록합니다. `.bluetape` state를 파일로 직접 수정하는 방식은 지원하지 않습니다.

Workflow가 참조하는 `code-review`와 `self-audit`는 외부 companion skill이며 이 canonical Bluetape 묶음에는 포함하지 않습니다. Code Review 경로나 harness self-audit gate를 사용할 때 별도로 설치하세요.

## 7-Tier review gate

Full Feature 작업의 `2-R` Spec Review, `3-R` Plan Review, `6-R` Pre-PR Review는 같은 7-Tier review engine을 사용합니다. Performance, Stability, Security, Operator/Ops, Developer/API, User/Caller라는 여섯 독립 관점이 서로 다른 실패를 찾고, main session의 통합이 일곱 번째 tier를 맡습니다.

[![2-R Spec, 3-R Plan, 6-R Pre-PR gate가 여섯 독립 review 관점과 main-session 통합을 거친 뒤 P0와 P1이 0이 될 때까지 blocker 수정과 검증을 반복합니다](docs/images/bluetape-workflow-7-tier-review-01.png)](docs/images/bluetape-workflow-7-tier-review-01.svg)

`P0`나 `P1`이 하나라도 남아 있으면 다음 gate를 열지 않습니다. Blocker를 수정하고 검증을 다시 실행한 뒤, 영향받은 review lane을 모두 재검토하고 다시 통합합니다. 최신 결과가 `P0=0`, `P1=0`일 때만 다음 단계로 진행합니다.

## 자세한 안내

- [Bluetape skill 공유와 설치](https://bluetape4k.github.io/ko/blog/bluetape-skills-sharing/)에서는 공개 배포본의 경계, canonical source 관리 원칙, 설치·업데이트 방법과 협업 모델을 설명합니다.
- [Bluetape workflow 사용법](https://bluetape4k.github.io/ko/blog/bluetape-skills-workflow-guide/)에서는 작업 분류, checklist gate, 단계별 다관점 review와 P0/P1이 0이 될 때까지 반복하는 절차를 다룹니다.

두 글에는 이 README의 빠른 시작 안내를 보완하는 source 동기화와 실행 경로 다이어그램도 담겨 있습니다.

## 의도적으로 제외한 항목

이 공개 묶음에는 재사용 가능한 canonical guidance만 포함합니다. 사용자 선호, memory, local rule, hook, config, plugin cache, secret, `bluetape4k-*` 같은 compatibility alias는 넣지 않습니다. 이 경계 덕분에 다른 개발자가 안심하고 설치할 수 있고, 개인 머신의 상태가 배포본에 섞이지 않습니다.

## 기여와 릴리스 정책

이 저장소는 관리 중인 canonical skill source를 배포하기 위한 mirror입니다. 수정이나 제안은 issue로 남겨 주세요. 관리자가 source와 함께 검토한 뒤 이후 bundle update에 반영합니다. 새 문서나 자동화에서는 retired skill 이름에 의존하지 마세요.

## 검증

복제하거나 갱신한 뒤 `./scripts/validate.sh`를 실행하세요. canonical inventory, 필수 front matter, rendered executable 이름, 외부 companion 선언, workflow contract, workflow 회귀 테스트, private/runtime payload 부재를 검사합니다.

## 라이선스

MIT. [LICENSE](LICENSE)를 참고하세요.
