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
`v1.4.0` 상태인 것을 확인해 `v1.4.1` version-sync 후보를 따로 준비했다.
후보 branch는 현재 로컬 worktree에만 있으며 push, PR 생성, merge, tag, Release는
실행하지 않았다.

근거: [PR #40](https://github.com/bluetape4k/bluetape-skills/pull/40), 이전 release
candidate와 promotion인 [PR #38](https://github.com/bluetape4k/bluetape-skills/pull/38),
[PR #39](https://github.com/bluetape4k/bluetape-skills/pull/39).

## 재발 방지

release checklist에서 최신 공개 tag와 현재 `develop` SHA를 먼저 기록하고,
두 README의 stable clone/update 명령과 CHANGELOG version heading/link를 그
tag 후보와 대조한다. 버전 참조가 준비되지 않았다면 promotion을 만들지 말고
version-sync 단계를 먼저 완료한다.

## 검증

- `./scripts/validate.sh`: workflow 151 tests, 164 subtests, diagram 50 tests 통과.
- tracked 변경 `git diff --check`: 통과; 새 lesson 후행 공백 검사 통과.
- README의 안정 버전 예제와 CHANGELOG의 `1.4.1` heading/link가 일치하고, README에 이전 `v1.4.0` 참조는 없다.
- 관련 Korean terminology rule set은 `clinic-appointment` 전용이라 미적용이다. 독립 reviewer lane은 bounded timeout 후 중단했고, 이 lesson은 체크리스트에 기록한 inline fallback review에서 검토했다. 이 verdict는 독립 attestation이 아니다.
- tag/archive/checksum과 isolated install: 아직 tag가 없는 후보 단계로, release
  직전에 별도로 검증해야 한다.
