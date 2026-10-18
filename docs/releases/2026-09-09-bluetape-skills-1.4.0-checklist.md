# Bluetape Skills 1.4.0 릴리스 체크리스트

## 릴리스 식별

| 항목 | 값 |
|---|---|
| 저장소 | `bluetape4k/bluetape-skills` |
| 분류 | Type E 유지보수 + Type P stable-release |
| 대상 버전 / 태그 | `1.4.0` / `v1.4.0` |
| 최신 공개 릴리스 | `v1.4.0` (`2026-09-08`) |
| 통합 브랜치 | `develop` |
| 안정 브랜치 | `main` |
| 후보 브랜치 | `chore/skills-sync-1.4.0` |
| 후보 source commit | `cc817860a5e67387827b236fec0bd644613d6a6a` |
| develop PR | #38 — `https://github.com/bluetape4k/bluetape-skills/pull/38` |
| develop merge commit | `7be805283ed5ee8e4a964187b6292edcaaafc6ab` |
| 승격 브랜치 | `release/promote-bluetape-skills-1.4.0` |
| main promotion base | `fca08654a685927da0c6d87159315f65b6d6970b` |
| main promotion PR | #39 — `https://github.com/bluetape4k/bluetape-skills/pull/39` |
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

- [x] `PUB-01` — target version, candidate SHA, artifact matrix, authority 고정
- [x] `PUB-02` — live branch/PR/release 상태와 GNO historical evidence 확인
- [x] `PUB-03` — 14개 skill source와 current installed skill parity 확인
- [x] `PUB-04` — `scripts/validate.sh`, workflow tests, diagram tests, isolated install 통과
- [x] `PUB-05` — develop PR merge-ready 및 main promotion hold 갱신
- [x] `PUB-06` — PR #38/#39의 exact head와 develop/main merge commit read-back
- [x] `PUB-07` — 서명 검증된 `v1.4.0` tag와 GitHub Release 생성·read-back
- [x] `PUB-08` — downstream consumer synchronization: N/A (source-only skill bundle)
- [x] `PUB-09` — next development line: N/A unless separately authorized
- [ ] `PUB-10` — README locale parity, release note, archive/checksum 검증
- [x] `PUB-11` — 공개 asset URL, GitHub digest metadata와 잔여 검증 위험 기록

## 현재 증거와 중단 조건

- GNO `bluetape4k-docs`의 공개 bundle synchronization lesson과 기존 1.3.4
  release checklist를 읽었다. GNO는 historical discovery이며 live GitHub가
  현재 상태의 기준이다.
- live GitHub의 default branch는 `develop`, 최신 공개 release는 `v1.4.0`이다.
- GitHub Actions가 없는 source-only 저장소이므로 workflow dispatch는 N/A다.
- candidate SHA가 바뀌면 기존 review·check·approval 증거를 폐기하고 다시
  exact-head 검증한다.
- 후보 commit `cc817860a5e67387827b236fec0bd644613d6a6a`에서 14개 canonical
  skill의 live source parity를 확인했고, 공개 경계 fixture만 private runtime
  의존성을 제거하도록 조정했다.
- `./scripts/validate.sh`는 workflow `151 passed, 164 subtests`와 diagram
  `50 tests OK`를 보고했고, isolated install은 14/14 파일 parity를 통과했다.
- writer terminology unit test는 8개 의도된 finding을 검출했고, 이번 release
  문서·CHANGELOG·README 대상 audit은 4개 파일 0건이었다.
- PR #38/#39의 병합, 서명 tag, GitHub Release 후속 evidence는 아래 closeout
  read-back에 기록한다. 이 문서는 archive/checksum/isolated-install의
  독립 검증 증거를 대신하지 않는다.

## 결과 기록

최종 문서에는 각 게이트의 `PASS/PENDING/BLOCKED`, exact SHA, PR URL, tag와
release URL, archive 및 `SHA256SUMS` 검증, isolated installation 결과,
제외·waiver·잔여 위험을 기록한다.

## 2026-10-19 후속 closeout read-back

- PR #38 (`chore/skills-sync-1.4.0` -> `develop`)의 마지막 head
  `1af779494006ff7968b93642d3e683e439593ee7`은 2026-09-08 15:30:56 UTC에
  merge commit `7be805283ed5ee8e4a964187b6292edcaaafc6ab`으로 병합됐다.
- PR #39 (`release/promote-bluetape-skills-1.4.0` -> `main`)의 마지막 head
  `bcd7cf842d3472469b9d777047328eebb3a7e66e`은 2026-09-08 15:39:09 UTC에
  merge commit `e0e688bc23e2d5af2476ef245f6f7cc4d0b39309`으로 병합됐다.
- `v1.4.0`은 SSH 서명이 있는 annotated tag다. GitHub tag verification은
  `verified: true`, tag object `9a051d6e9c41fe23f847d960a98bbc07cce8379c`,
  target commit `e0e688bc23e2d5af2476ef245f6f7cc4d0b39309`로 read-back했다.
  GitHub Release는 2026-09-08 15:57:48 UTC에 공개됐다.
- 공개 assets와 GitHub가 반환한 SHA-256 digest metadata는 다음과 같다. 이
  digest는 GitHub asset metadata이며, 이번 read-back에서 파일을 다시 내려받아
  archive 내용이나 `SHA256SUMS` 내부 값을 독립 검증한 것은 아니다.

  | Asset | URL | GitHub digest metadata |
  |---|---|---|
  | `bluetape-skills-1.4.0.tar.gz` | [다운로드](https://github.com/bluetape4k/bluetape-skills/releases/download/v1.4.0/bluetape-skills-1.4.0.tar.gz) | `sha256:64362f1b9d7759068cadfee0fdbf9afaa4ad1724ad6c5f59f2ffa66361007f6d` |
  | `bluetape-skills-1.4.0.zip` | [다운로드](https://github.com/bluetape4k/bluetape-skills/releases/download/v1.4.0/bluetape-skills-1.4.0.zip) | `sha256:0d6597f4a27caa02dc7d9a0b95854febd41e60d05798eb865c4baee68be08630` |
  | `SHA256SUMS` | [다운로드](https://github.com/bluetape4k/bluetape-skills/releases/download/v1.4.0/SHA256SUMS) | `sha256:a7cac147820d504b134984639ea8b9a8443f99e598e47798395b104b899e5efb` |
- `PUB-10`은 release archive checksum, locale/추출본, tag 기반 fresh install을
  독립 검증하지 않아 계속 `PENDING`이다. [PR #38](https://github.com/bluetape4k/bluetape-skills/pull/38),
  [PR #39](https://github.com/bluetape4k/bluetape-skills/pull/39),
  [v1.4.0 GitHub Release](https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.4.0).
