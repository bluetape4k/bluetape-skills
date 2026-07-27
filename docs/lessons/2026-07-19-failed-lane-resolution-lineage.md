# 실패 lane 해소 이력과 완료 판정 교훈

## 맥락

Phase 2 coordinator는 모든 lane의 상태가 `completed`여야 run을 완료했다.
검토 lane이 실제 결함을 발견해 `failed`가 된 뒤 수정과 exact-head 재검토가
성공해도, terminal 실패 이력을 성공으로 연결하는 계약이 없어 run이 영구히
완료되지 않았다.

## 결정

- 과거 `failed` 상태를 변경하거나 영수증에서 제거하지 않는다.
- 기존 Phase 2 snapshot도 허용하는 `candidate_validated` 이벤트에
  `candidate_kind=failed_lane_resolution`을 기록해 실패 lane과 나중에 성공한
  correction/rereview lane을 명시적으로 연결한다.
- 해소 대상은 `completed` lane과 독립적인 completion evidence를 요구한다.
- 실패, 차단, 취소, 미등록, 자기 참조, 중복, liveness-only 증거는 해소로
  인정하지 않는다.
- stalled-agent replacement lineage와 semantic failure resolution lineage를
  별도 계약으로 유지한다.
- 해소 증거는 실패 결과와 성공 결과의 receipt digest를 모두 결합하고,
  모든 과거 liveness evidence digest와 비교한다.
- 새 snapshot은 resolution lane의 `parent_lane_id`까지 검증하되, 이 필드를
  소급할 수 없는 기존 `1.1.0` snapshot은 후속 terminal receipt sequence와 두
  evidence digest 결합으로 호환한다.

## 결과와 검증

`completion-check`는 `unresolved_failed_lanes`와 `resolved_failed_lanes`를
분리해 보고한다. replay가 검증한 성공 lineage만 원래 실패 lane을
`missing_lanes`에서 제외하며, 원래 실패 상태와 원인 증거는 그대로 남는다.
성공, 미해소, 실패한 resolver, 잘못된 연결, 중복, replay, liveness-only
증거에 대한 회귀 테스트로 계약을 고정했다.

## 다음 작업 원칙

Append-only workflow에서 terminal 실패가 후속 작업으로 복구될 수 있다면,
과거 상태를 덮어쓰지 말고 별도의 성공 lineage를 기록한다. 완료 판정은
최신 성공 여부만 보지 말고 원래 실패, 해소 대상, 해소 증거를 함께 replay해
검증해야 한다.
