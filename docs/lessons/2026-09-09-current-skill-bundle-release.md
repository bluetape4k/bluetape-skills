# 현재 skill bundle을 공개 배포본으로 승격한 교훈

## 맥락

관리자의 설치 skill과 `bluetape-skills` 공개 bundle 사이에 Kotlin, Go,
JVM publish, workflow, writer 변경이 누적되었다. 개인 dotfiles의 hook·config와
공개 재사용 skill은 서로 다른 배포 경계를 가진다.

## 결정

- 설치된 canonical 14개 skill만 공개 `skills/`에 동기화한다.
- `bluetape-publish-kotlin` 같은 compatibility alias와 private runtime payload는
  manifest와 공개 경계 정책에 따라 제외한다.
- public bundle에 포함된 cache 산출물은 제거하고, source-only bundle의 공개
  검증은 `validate.sh`, workflow/diagram test, 격리 설치로 증명한다.
- 설치본 workflow test가 개인 `$doctor`와 user-scope `AGENTS.md` 문구를 직접
  읽어 공개 validator를 깨뜨렸다. 공개 fixture는 배포된 repository overlay의
  경계만 검증하도록 분리하고, 개인 skill이나 user-scope 문서를 공개 manifest에
  추가하지 않았다.
- 공개 버전은 최신 tag `v1.3.3`과 현재 승인된 변경을 구분해 `v1.4.0` 후보로
  고정한다. develop 통합과 main 안정 승격, immutable tag/release를 각각
  분리한다.

## 검증 계획

- source/live inventory와 파일 parity를 비교한다.
- public-boundary validator가 private/runtime payload, rendered filename,
  manifest, external companion 선언을 통과하는지 확인한다.
- README 영어/한국어의 install/update 버전과 CHANGELOG/release checklist를
  함께 읽고, exact candidate SHA를 갱신한다.
- merge와 tag 전후에 GitHub live branch, PR, tag, release, archive checksum을
  다시 읽는다.

## 결과

후보 commit `cc817860a5e67387827b236fec0bd644613d6a6a`에 14개 canonical skill과
공개 경계 fixture를 고정했다. `./scripts/validate.sh`는 workflow 151건과
subtest 164건, diagram 50건을 통과했고, isolated install은 14/14 파일 parity를
확인했다. 승인되지 않은 merge·tag·release는 실행하지 않으며, candidate head가
바뀌면 이전 증거를 재사용하지 않는다.
