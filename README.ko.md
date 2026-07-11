# Bluetape Skills

[English](README.md) | 한국어

Bluetape 개발 워크플로를 위한 설치 가능한 canonical [Codex skill](https://developers.openai.com/codex/skills/) 묶음입니다. 각 skill에는 실행에 필요한 reference, template, script, agent prompt를 함께 넣습니다. 반면 retired alias와 개인 런타임 상태는 의도적으로 배포하지 않습니다.

## 설치

```bash
git clone https://github.com/bluetape4k/bluetape-skills.git
cd bluetape-skills
./scripts/validate.sh
./scripts/install.sh
```

설치 대상은 `${CODEX_HOME:-~/.codex}/skills`입니다. 동일한 canonical skill이 이미 있으면 installer는 덮어쓰지 않고 멈춥니다. 교체가 필요할 때만 `--force`를 사용하세요. 기존 skill은 timestamp가 붙은 backup 디렉터리로 먼저 옮깁니다.

```bash
./scripts/install.sh --dry-run
./scripts/install.sh --codex-home "$HOME/.codex"
./scripts/install.sh --force
```

설치 뒤에는 Codex를 다시 시작해야 새 skill을 인식합니다.

## 업데이트

```bash
git pull --ff-only
./scripts/validate.sh
./scripts/install.sh --force
```

설치본을 강제로 교체하기 전, 로컬에서 수정한 내용이 있다면 `git log`와 `git diff`를 먼저 확인하세요.

## 사용

Bluetape 생태계 작업은 `$bluetape-workflow`부터 시작하세요. 작업을 분류한 뒤 가장 가벼운 안전한 경로로 연결합니다.

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

## 의도적으로 제외한 항목

이 공개 묶음에는 재사용 가능한 canonical guidance만 포함합니다. 사용자 선호, memory, local rule, hook, config, plugin cache, secret, `bluetape4k-*` 같은 compatibility alias는 넣지 않습니다. 이 경계 덕분에 다른 개발자가 안심하고 설치할 수 있고, 개인 머신의 상태가 배포본에 섞이지 않습니다.

## 기여와 릴리스 정책

이 저장소는 관리 중인 canonical skill source를 배포하기 위한 mirror입니다. 수정이나 제안은 issue로 남겨 주세요. 관리자가 source와 함께 검토한 뒤 이후 bundle update에 반영합니다. 새 문서나 자동화에서는 retired skill 이름에 의존하지 마세요.

## 검증

clone 또는 update 뒤 `./scripts/validate.sh`를 실행하세요. canonical inventory, 필수 front matter, private/runtime payload 부재를 검사합니다.

## 라이선스

MIT. [LICENSE](LICENSE)를 참고하세요.
