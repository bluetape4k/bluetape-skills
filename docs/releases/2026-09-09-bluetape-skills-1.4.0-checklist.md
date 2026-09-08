# Bluetape Skills 1.4.0 릴리스 체크리스트

## 릴리스 식별

| 항목 | 값 |
|---|---|
| 저장소 | `bluetape4k/bluetape-skills` |
| 분류 | Type E 유지보수 + Type P stable-release |
| 대상 버전 / 태그 | `1.4.0` / `v1.4.0` |
| 최신 공개 릴리스 | `v1.3.3` (`2026-08-12`) |
| 통합 브랜치 | `develop` |
| 안정 브랜치 | `main` |
| 후보 브랜치 | `chore/skills-sync-1.4.0` |
| 배포 범위 | canonical skill 14개, 참조 자료, workflow/diagram 회귀 테스트 |
| 제외 범위 | private runtime, hooks, config, memory, plugin cache, retired alias, 외부 companion skill |
| 승인 | 사용자가 현재 skill 동기화와 배포 계획을 승인함. develop/main 병합·tag·release는 exact SHA별 fresh approval 대상 |

## 변경 범위

- 현재 설치된 canonical skill을 공개 `skills/`에 동기화한다.
- Kotlin lifecycle·JVM/serialization compatibility·retry/cache boundary
  reference를 포함한다.
- Go provider/crypto/HTTP hardening, JVM publish 문서, workflow model routing,
  writer terminology audit 변경을 포함한다.
- 설치 README와 한국어 README의 안정 버전을 `v1.4.0`으로 맞춘다.
- 공개 bundle에 남아 있던 diagram `.ruff_cache` 산출물을 제거한다.
- 공개 bundle의 workflow 회귀 테스트는 배포에서 제외한 개인 `$doctor`
  skill을 읽지 않고, 공개에 포함된 `AGENTS.md` 계약만 검증하도록 유지한다.

## 게이트

- [ ] `PUB-01` — target version, candidate SHA, artifact matrix, authority 고정
- [ ] `PUB-02` — live branch/PR/release 상태와 GNO historical evidence 확인
- [ ] `PUB-03` — 14개 skill source와 current installed skill parity 확인
- [ ] `PUB-04` — `scripts/validate.sh`, workflow tests, diagram tests, isolated install 통과
- [ ] `PUB-05` — develop PR merge-ready 및 main promotion hold 갱신
- [ ] `PUB-06` — develop/main exact SHA push·merge 상태 검증
- [ ] `PUB-07` — signed `v1.4.0` tag와 GitHub Release 생성·read-back
- [ ] `PUB-08` — downstream consumer synchronization: N/A (source-only skill bundle)
- [ ] `PUB-09` — next development line: N/A unless separately authorized
- [ ] `PUB-10` — README locale parity, release note, archive/checksum 검증
- [ ] `PUB-11` — artifact URLs, SHA, residual risk, side-effect state 보고

## 현재 증거와 중단 조건

- GNO `bluetape4k-docs`의 공개 bundle synchronization lesson과 기존 1.3.4
  release checklist를 읽었다. GNO는 historical discovery이며 live GitHub가
  현재 상태의 기준이다.
- live GitHub의 default branch는 `develop`, 최신 공개 release는 `v1.3.3`이다.
- GitHub Actions가 없는 source-only 저장소이므로 workflow dispatch는 N/A다.
- candidate SHA가 바뀌면 기존 review·check·approval 증거를 폐기하고 다시
  exact-head 검증한다.
- merge, immutable tag, GitHub Release는 해당 exact SHA의 merge-ready 보고와
  fresh approval 전에는 실행하지 않는다.

## 결과 기록

최종 문서에는 각 게이트의 `PASS/PENDING/BLOCKED`, exact SHA, PR URL, tag와
release URL, archive 및 `SHA256SUMS` 검증, isolated installation 결과,
제외·waiver·잔여 위험을 기록한다.
