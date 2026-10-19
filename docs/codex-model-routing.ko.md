# Codex와 OMX 모델 설정 (수동 적용 참고)

[English](codex-model-routing.md) | 한국어

이 문서는 Codex 사용자 기본값과 현재 OMX agent role에 `gpt-6-luna` 및 `max`를 직접 설정하는 방법을 안내합니다. 선택 가능한 참고 예시일 뿐 Bluetape의 필수 설정이나 성능 권고가 아닙니다. Bluetape Skills 설치 스크립트는 이 설정을 적용하지 않습니다.

파일을 수정하기 전에 로그인한 계정, workspace, Codex client에서 해당 모델과 추론 강도를 사용할 수 있는지 확인하세요. 제공 여부는 실행 환경에 따라 다르고 바뀔 수 있습니다. 먼저 백업하고, 기존 파일의 다른 설정은 보존하면서 필요한 key만 합치세요.

## Codex 사용자 기본값 설정

기본 Codex 설정 파일은 `~/.codex/config.toml`입니다. `CODEX_HOME`을 지정했다면 `$CODEX_HOME/config.toml`을 수정하세요. 다음 root-level 값을 추가하거나 갱신합니다.

```toml
model = "gpt-6-luna"
model_reasoning_effort = "max"
```

선택한 모델과 client가 지정한 추론 강도를 지원해야 합니다. 최신 지원 여부는 [Codex 설정 reference](https://developers.openai.com/codex/config-reference)와 [GPT-6 Luna 모델 페이지](https://developers.openai.com/api/docs/models/gpt-6-luna)에서 확인하세요.

## OMX agent role별 override 설정

사용자 범위 OMX 설정 파일은 `${CODEX_HOME:-$HOME/.codex}/.omx-config.json`입니다. 프로젝트 범위 설정은 해당 프로젝트의 Codex home을 사용하며, 흔히 `./.codex/.omx-config.json`에 둡니다. `omx doctor`로 현재 설정 범위와 실제 경로를 확인하세요. 의도한 경우가 아니라면 개인 설정을 공유 저장소에 복사하지 마세요.

아래 두 객체를 기존 JSON 파일에 key 단위로 합치세요. 관계없는 최상위 key와 아래 예시에 없는 기존 role 항목도 보존합니다. 이 예시는 나열된 role만 갱신합니다. 아래 22개 role 이름은 2026-10-17 기준 이 참고 문서가 사용하는 Bluetape runtime registry를 반영합니다. 설치된 OMX 버전에서 인식되는 role만 사용하고, 같은 설정을 적용하려는 신규 role이 생기면 직접 추가하세요.

```json
{
  "agentModels": {
    "analyst": "gpt-6-luna",
    "architect": "gpt-6-luna",
    "code-reviewer": "gpt-6-luna",
    "code-simplifier": "gpt-6-luna",
    "critic": "gpt-6-luna",
    "debugger": "gpt-6-luna",
    "dependency-expert": "gpt-6-luna",
    "designer": "gpt-6-luna",
    "executor": "gpt-6-luna",
    "explore": "gpt-6-luna",
    "git-master": "gpt-6-luna",
    "planner": "gpt-6-luna",
    "prometheus-strict-metis": "gpt-6-luna",
    "prometheus-strict-momus": "gpt-6-luna",
    "prometheus-strict-oracle": "gpt-6-luna",
    "researcher": "gpt-6-luna",
    "scholastic": "gpt-6-luna",
    "team-executor": "gpt-6-luna",
    "test-engineer": "gpt-6-luna",
    "verifier": "gpt-6-luna",
    "vision": "gpt-6-luna",
    "writer": "gpt-6-luna"
  },
  "agentReasoning": {
    "analyst": "max",
    "architect": "max",
    "code-reviewer": "max",
    "code-simplifier": "max",
    "critic": "max",
    "debugger": "max",
    "dependency-expert": "max",
    "designer": "max",
    "executor": "max",
    "explore": "max",
    "git-master": "max",
    "planner": "max",
    "prometheus-strict-metis": "max",
    "prometheus-strict-momus": "max",
    "prometheus-strict-oracle": "max",
    "researcher": "max",
    "scholastic": "max",
    "team-executor": "max",
    "test-engineer": "max",
    "verifier": "max",
    "vision": "max",
    "writer": "max"
  }
}
```

`agentModels`와 `agentReasoning`은 Codex 기본값과 별개의 role별 override입니다. OMX가 설정을 읽더라도 선택한 모델과 실제 Codex 실행 환경이 `max`를 지원해야 합니다. 지원되지 않는 role 추론 강도를 OMX가 자동으로 낮춰 주지는 않습니다. 현재 schema와 우선순위는 [OMX model/config routing reference](https://github.com/Yeachan-Heo/oh-my-codex/blob/main/docs/reference/omx-config-schema-routing.md)에서 확인하세요.

OMX setup은 role override 외에도 전달 방식과 설정 범위에 따라 prompts, skills, native agents, `config.toml`, hooks, `AGENTS.md`, `.omx` runtime/HUD 파일을 생성하거나 갱신할 수 있습니다. scope와 전달 방식 선택을 저장하고, plugin mode에서는 기존 OMX 관리 prompts/skills를 보관하거나 제거하며, `developer_instructions`와 setup 소유 Team/notification 연동을 변경할 수도 있습니다. 먼저 [OMX setup 안내](https://github.com/Yeachan-Heo/oh-my-codex/blob/main/skills/omx-setup/SKILL.md)를 읽고, 의도한 scope의 변경 미리보기를 확인하세요.

```bash
omx setup --dry-run --scope user
# 프로젝트 범위 설정이라면:
omx setup --dry-run --scope project
```

미리보기에서 생성·갱신·보관·제거 대상과 저장될 선택을 모두 확인하고, 모든 변경이 의도한 경우에만 적용합니다. 전달 방식을 명시적으로 선택한다면 미리보기와 적용 명령 양쪽에 같은 `--plugin` 또는 `--legacy`를 넣으세요. `--force`는 관리 대상 파일을 덮어쓰거나 재설치합니다.

```bash
omx setup --scope user --force
# 프로젝트 범위 설정이라면:
omx setup --scope project --force
omx doctor
```

OMX를 실행하는 것과 같은 shell 및 프로젝트 context에서 setup을 실행하세요. `omx doctor`로 적용된 설치 상태와 실제 설정 범위를 확인합니다.

## 적용 확인 및 유지관리

1. 실제 Codex home과 OMX 설정 범위를 확인합니다.
2. 사용 중인 계정, workspace, client에서 `gpt-6-luna`와 `max`가 허용되는지 확인합니다.
3. 설치된 OMX role registry와 설정한 key가 일치하는지 확인합니다.
4. Codex 또는 OMX를 업그레이드한 뒤에는 공식 reference를 다시 확인합니다. 모델 제공 여부와 role 목록은 바뀔 수 있습니다.

위 예시는 수동 적용용입니다. `./scripts/install.sh`는 Bluetape skill 폴더를 `${CODEX_HOME:-$HOME/.codex}/skills`에 설치할 뿐, `config.toml`이나 `.omx-config.json`을 쓰지 않습니다.
