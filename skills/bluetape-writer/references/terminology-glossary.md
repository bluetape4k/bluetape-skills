# Approved Terminology Glossary

Use this reference when a user supplies an approved terminology set or when a
domain term is corrected repeatedly across a document series. This file records
project-backed choices; it is not a universal Korean translation dictionary.
The machine-readable checks in `references/terminology-rules.json` enforce the
reusable collision and phrase rules below. Keep the two files aligned.

## Preservation Rules

- Preserve code identifiers, API names, configuration keys, HTTP reason codes,
  commands, URLs, and exact source excerpts.
- Apply a preferred term only when it names the same software state or
  operation. Do not mechanically replace a word when the technical meaning
  changes.
- Keep the same concept under the same name across body prose, frontmatter,
  tables, captions, alt text, diagram labels, and series navigation.
- When a term is ambiguous, expand it at first useful occurrence and retain the
  exact English token in parentheses when the token is part of the source
  contract, for example `보류(hold)` or `아웃박스(outbox)`.

## Clinic Appointment Series (2026-08)

The following choices were approved while proofreading the Korean clinic
appointment series. They are a local contract for this series and may not match
every product's terminology.

| English/source concept | Preferred Korean | Avoid or usage note |
|---|---|---|
| waitlist | `대기 목록` | Do not alternate with `대기열` or `대기 명단` in the same series. |
| waitlist entry | `대기 항목` | Use for one record in the waitlist, not for the collection. |
| offer | `제안` | Keep `OFFERED` as the exact state identifier. |
| active offer | `활성 제안` | In an invariant, prefer `빈시간에는 활성 제안만 남긴다` over a redundant `한 ... 하나`. |
| available appointment time / released time slot | `빈시간` | Use one word, not `빈 시간`; do not use the space-oriented `빈자리` in this series. |
| appointment service | `예약 서비스` | Keep spacing consistent; do not write `예약서비스`. |
| product management / product development / customer consultation | `상품 관리` / `상품 개발` / `고객 상담` | Keep each compound noun spaced in prose and headings. |
| appointment / reservation / visit commitment | `예약` | Use `예약` for reader-facing booking and visit language in this series. Preserve `commitment` only in exact source identifiers or when explaining a source contract. |
| confirmed appointment / confirmed visit commitment | `확정 예약` | Use this reader-facing phrase; preserve exact source identifiers and source excerpts. |
| snapshot (reader-facing) | Context-specific `기준 데이터`, `구매 기준 정보`, or `실행 기준 데이터` | Do not use `스냅샷` or `스냅숏` as a blanket translation. Preserve `PackageExecutionSnapshot`, `snapshotHash`, and other code tokens exactly. |
| source of truth | `기준 데이터 원본` | Do not use the literal `진실의 원천`. `SSOT` may remain when it is useful. |
| hold | `보류(hold)` | For capacity/resource context, qualify it as `수용량 보류(hold)` when needed. Preserve `hold` in identifiers. |
| outbox | `아웃박스(outbox)` | Preserve `outbox` in identifiers and source names. |
| terminal outcome decision | `최종 상태 결정` | Use an explicit decision node/label rather than an unexplained terminal connector. |
| no-show | `노쇼` | This is the approved reader-facing term for this series; preserve `NO_SHOW` in code. |
| scheduler / worker / provider | `스케줄러` / `워커` / `제공자(provider)` | Use the Korean technical loanword in prose and preserve source identifiers. |
| freshness / latestness | `최신 여부` or `최신인지 확인` | Prefer a concrete predicate over the abstract noun `최신성`. |
| durable / persisted command or work | `저장된 명령` / `저장된 작업` | Use `영속` only when it is part of an exact API, code, or established contract term. |
| notification backlog | `미처리 누적(backlog)` | Do not call notification backlog `대기열`; reserve `대기 목록` for the waitlist collection. |
| action queue item | `조치 메시지(작업 요청)` | A queue message is not automatically a database `행`. Use `행` only when the source really means a stored row. |
| member resolver circuit | `회원 조회(member) circuit` | Name the protected dependency; `회원 circuit` is too vague for reader-facing prose. |
| `DEGRADED_REVIEW` reader label | `운영 검토 대기` | Preserve the exact state identifier and explain the operator-facing label separately. |

## Approved Reader-Facing Phrases

- `운영 화면은 더 많은 정보보다 더 명확한 정보를 제공해야 한다` is the
  approved dashboard conclusion. It means that an operations screen should
  make the next decision and its boundary clear, not merely show more rows.
- For a terminal path in a workflow or sequence diagram, name the outcome and
  the decision explicitly. Do not leave a vertical connector attached to a
  horizontal dotted line without explaining what the line means.
- Keep the distinction between a state list and an action queue. A list shows
  current state; an action queue orders what an operator should inspect next.
- Resolve the semantic role before choosing a Korean term: collection versus
  item, database row versus queue message, state identifier versus reader label,
  and code token versus explanatory prose.

## Reusable Correction Patterns

These examples are taken from repeated corrections in the clinic appointment
series. They are sentence-level patterns, not blanket word substitutions.

| Translation-shaped or ambiguous wording | Reader-facing Korean |
|---|---|
| `계산 결과의 최신성 보장` | `계산 결과가 최신인지 확인하는 방법` |
| `영속 명령` | `저장된 명령` |
| `운영 화면의 한 행` | `조치 큐의 작업 요청` |
| `대기열(backlog)` | `미처리 누적(backlog)` |
| `회원 circuit` | `회원 조회(member) circuit` |
| `운영 보류` | `운영 검토 대기` |

Do not apply these replacements when the surrounding source proves that the
technical meaning is different. The audit script reports candidates; the
writer still reads the sentence and resolves the intended meaning.

## Review Checklist

- [ ] The collection term is `대기 목록`; an individual record is `대기 항목`.
- [ ] `빈시간`, `예약`, `확정 예약`, and `최종 상태 결정` are used for
      reader-facing prose.
- [ ] `예약 서비스`, `상품 관리`, `상품 개발`, and `고객 상담` use the approved spacing.
- [ ] `보류(hold)` and `아웃박스(outbox)` retain the English token where the
      source contract requires it.
- [ ] Code tokens, links, identifiers, numbers, and state names were not
      changed by terminology cleanup.
- [ ] Snapshot-like data is named by its domain role (`기준 데이터`,
      `구매 기준 정보`, or `실행 기준 데이터`), not by a blanket loanword.
- [ ] `node ~/.codex/skills/bluetape-writer/scripts/audit-korean-terms.mjs`
      was run for the changed Korean files, and every finding was repaired or
      explicitly reviewed as an intentional exception.
