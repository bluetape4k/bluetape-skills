# 안정 승격 전에 develop의 버전 참조를 먼저 검증한다

## 맥락

PR #40은 모델 설정 참고 문서와 README 연결을 `develop`에 병합했지만, 병합된
트리의 안정 설치 예제는 여전히 `v1.4.0`을 가리켰고 변경 내역은
`CHANGELOG.md`의 `[Unreleased]` 아래에 있었다. 이 상태에서 곧바로 `main` 승격을
다음 단계로 안내하면 목표 버전이 포함된 release candidate 없이 안정 브랜치를
준비하게 된다.

## 결정

- 안정 승격 전에 `develop`의 영어·한국어 README clone/update 예제, CHANGELOG
  heading, release-tag 링크가 목표 버전으로 함께 갱신됐는지 확인한다.
- 참조가 이전 버전이거나 변경이 `[Unreleased]`에 남아 있으면, 먼저 별도
  version-sync PR을 `develop`에 통합한다. 그 exact merge commit을 검증한 뒤에만
  `main` promotion PR을 준비한다.
- 후보 PR 생성, PR merge, `main` 승격, tag와 GitHub Release는 각각 저장소·대상
  ref·exact SHA를 고정하고 별도 승인 경계를 유지한다.

## 결과

2026-10-18 기준 `develop` merge commit은
`31e69c613e9f908bec27f3a7ebee6e34cabebe21`이었다. README와 CHANGELOG가
`v1.4.0` 상태인 것을 확인해 `v1.4.1` version-sync 후보를 준비했고, 후보는
PR #41(`develop` <- `release/bluetape-skills-1.4.1`)로 이미 공개되어 있었다.
2026-10-18 closeout read-back에서 PR #41은 OPEN, 당시 head는
`373a160e8b8e3a9b7103949a7d5d199897ea436a`, `main`은
`e0e688bc23e2d5af2476ef245f6f7cc4d0b39309`, 최신 공개 릴리스는 `v1.4.0`이었다.
사용자는 merge부터 `main` 승격, tag/Release, 작업 worktree 정리까지 요청했지만,
이 lesson을 갱신하는 시점에는 merge-ready exact-head 승인과 이후 main/tag/Release
승인 gate가 남아 있었다. 그러므로 “후보가 로컬에만 있다”는 이전 문구는 더 이상
현재 상태 설명으로 사용하지 않는다.

근거: [PR #41](https://github.com/bluetape4k/bluetape-skills/pull/41),
[PR #40](https://github.com/bluetape4k/bluetape-skills/pull/40), 이전 release
candidate와 promotion인 [PR #38](https://github.com/bluetape4k/bluetape-skills/pull/38),
[PR #39](https://github.com/bluetape4k/bluetape-skills/pull/39).

## 재발 방지

release checklist에서 최신 공개 tag와 현재 `develop` SHA를 먼저 기록하고,
두 README의 stable clone/update 명령과 CHANGELOG version heading/link를 그
tag 후보와 대조한다. 버전 참조가 준비되지 않았다면 promotion을 만들지 말고
version-sync 단계를 먼저 완료한다.

### 릴리스 closeout 기록도 승격 전에 대조한다

2026-10-19 후속 점검에서 과거 릴리스 checklist의 완료 증거가 `main`에는
남아 있지만 `develop` 사본에는 빠진 경우를 확인했다. PR #34/#35는 이미
병합됐지만 `1.3.4` tag/Release는 없었고, PR #38/#39와 `v1.4.0` Release는
완료됐다. 병합, tag, Release, archive 검증은 서로 다른 상태이므로 하나의
완료 표시로 뭉뚱그리지 않는다.

다음 stable promotion 전에 exact `develop`·`main` SHA를 고정하고,
`docs/releases/*checklist.md`와 연관 lesson을 서로 비교한다. 빠진 사실은
live GitHub에서 재확인하고 기존 checklist를 덮어쓰지 않는 날짜별 후속
read-back으로 `develop`에 보존한다. 그 후 promotion candidate tree가 이
증거를 삭제하거나 과거 `PENDING`을 근거 없이 `PASS`로 바꾸지 않는지
확인한다. 이 단계가 끝나기 전에는 promotion PR을 만들지 않는다.

## 검증

- 최초 version-sync candidate에서 `./scripts/validate.sh`: workflow 151 tests, 164 subtests, diagram 50 tests 통과.
- 현재 checklist/lesson 수정분도 `./scripts/validate.sh` 통과(151 tests, 164 subtests; diagram 50 tests), `git diff --check` 통과. 이는 archive/checksum/isolated install을 포함한 tag 기반 release 검증을 대신하지 않는다.
- README의 안정 버전 예제와 CHANGELOG의 `1.4.1` heading/link가 일치하고, README에 이전 `v1.4.0` 참조는 없다.
- 관련 Korean terminology rule set은 `clinic-appointment` 전용이라 미적용이다. 독립 reviewer lane은 최초 candidate에서 bounded timeout 후 중단했고, 당시 lesson은 최초 version-sync candidate의 inline fallback review에서 검토했다. 이 verdict는 이번 사실 갱신 diff를 포함하지 않으며 독립 attestation도 아니다.
- 2026-10-18 version-sync 후보 점검 시점에는 `v1.4.1` tag/Release가 없었다. archive/checksum과 isolated install은 게시 전 별도로 검증해야 한다.
- 2026-10-19 closeout read-back에서 [PR #34](https://github.com/bluetape4k/bluetape-skills/pull/34), [PR #35](https://github.com/bluetape4k/bluetape-skills/pull/35), [PR #38](https://github.com/bluetape4k/bluetape-skills/pull/38), [PR #39](https://github.com/bluetape4k/bluetape-skills/pull/39), `v1.4.0` SSH tag verification, GitHub Release를 확인했다. archive/checksum 파일 내용과 isolated install은 이번 문서 복구에서 재검증하지 않았다.
