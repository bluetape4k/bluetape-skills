# Bluetape Skills 1.1.0 공개 bundle 교훈

## 맥락

chezmoi에 병합된 14개 canonical skill을 공개 저장소로 export하면서 Phase 2 workflow runtime과 교차 skill 계약을 1.1.0 후보에 반영했다.

## 결정

- canonical skill 디렉터리는 전체를 복사하고 chezmoi의 `executable_` 접두사는 공개 target 이름으로 변환했다.
- `.pytest_cache`, `.ruff_cache`, `__pycache__`, 개인 설정, hook, memory, runtime state는 배포 경계 밖에 뒀다.
- Workflow가 참조하지만 canonical Bluetape 목록에 속하지 않는 `code-review`, `self-audit`는 `skills/manifest.json`의 외부 companion으로 선언했다.
- Contract validator는 외부 companion 부재 진단만 허용하고 다른 진단은 계속 실패하도록 공개 validator에서 감쌌다.

## 결과와 검증

- 기존 validator는 Phase 2 필수 파일이 없어도 통과했지만, 보완 후 manifest, rendered filename, contract, 전체 workflow 테스트를 함께 검증한다.
- Canonical source와 공개 14-skill export의 파일 목록과 SHA-256을 rendered filename 기준으로 비교한다.
- `README.md`와 `README.ko.md`는 같은 설치 버전, runtime 경계, 외부 companion, 검증 요구사항을 설명한다.

## 다음 작업 원칙

공개 bundle 동기화에서는 개별 파일을 골라 복사하지 말고 canonical skill 단위를 전체 export한다. Canonical validator가 설치 환경 전체를 가정하면 공개 bundle 경계를 넓히지 말고 외부 의존성을 명시적으로 선언한 뒤 예상 진단만 좁게 허용한다.
