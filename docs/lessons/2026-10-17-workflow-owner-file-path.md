# Workflow helper owner file은 정해진 경로에 둔다

## 관찰

`bluetape-flow.py init`에 owner file을 상태 루트의 최상위 경로로 지정하자 helper가 입력을 거부했다. repository의 tracked 파일과 원격 상태에는 영향이 없었다. helper가 요구하는 `.bluetape/handles/` 내부 경로로 수정한 후 초기화가 통과했다.

## 재발 방지

워크플로 receipt를 초기화하기 전에 `bluetape-flow.py`와 runtime의 owner-file containment 계약을 확인한다. owner file은 해당 상태 루트의 `handles/` 아래에 두고, fencing 값은 명령행·로그·대화에 출력하지 않는다. 경로 추정으로 실패하면 입력 오류를 좁혀 확인한 뒤 helper를 통해서만 복구한다.

## 근거

- Runtime contract: `skills/bluetape-workflow/scripts/bluetape_runtime.py`의 `initialize_run`.
- 이번 실행: 잘못된 최초 위치에서 helper 거부 후 `.bluetape/handles/` 아래 경로로 재시도 성공. 실패한 초기화는 repository tracked 파일이나 GitHub 상태를 바꾸지 않았다.
