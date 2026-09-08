# Korean Naturalness Checklist

Use this for Korean software technical documentation in the bluetape
ecosystem. It owns naturalness and register checks, not repository-specific
facts or an ever-growing terminology dictionary. Domain terms and contextual
collision rules live in `terminology-glossary.md` and
`terminology-rules.json`.

## Preservation Rules

- Preserve facts, numbers, dates, commands, links, benchmark values,
  identifiers, product names, quotes, genre, and uncertainty.
- Verify factual claims against the intended repository ref before polishing
  prose. A style pass must not preserve stale technical claims.
- Prefer small local edits. Do not rewrite correct prose merely to impose one
  voice.
- Apply the pass to titles, frontmatter, tables, captions, alt text, link text,
  and reader-facing diagram labels as well as body paragraphs.

## Natural Korean Technical Prose

Specific beats generic. Facts beat significance claims. Direct verbs beat
nominalized or over-hedged prose.

| Avoid | Prefer |
|---|---|
| `~를 통해` | `~로`, `~해서`, or the concrete verb |
| `~에 있어서` | `~에서`, `~할 때` |
| `~되어진다` | `~된다`, or active voice |
| `가지고 있다` | `있다`, `제공한다`, or a concrete state |
| `~에 의해 생성된` | `~가 만든`, `~에서 만든` |
| `~할 수 있을 것으로 보인다` | `~할 수 있다`, or state the uncertainty |
| `중요하다`, `강력하다`, `효율적이다` | the behavior, measurement, or failure avoided |

- Avoid mechanical `첫째/둘째/셋째`, broad virtue triplets, repeated
  transitions, and vague future-outlook endings.
- Remove anonymous authority such as `업계에서는` or `많은 개발자가` unless
  a named source supports it.
- Use concrete verbs such as `읽고`, `저장하고`, `무효화하고`,
  `재시도하고`, and `측정한다`.
- Keep identical concepts under identical names. Do not rotate terminology for
  stylistic variety.
- Vary sentence length naturally; split sentences carrying multiple ideas and
  merge choppy fragments.

## Register And Terminology

Natural does not mean casual. Match the artifact:

- KDoc and technical articles use precise established terminology.
- Plans, reviews, and lessons may be direct, but should not become chatty.
- Personal retrospectives may use limited humor when it clarifies the
  engineering pain.
- Preserve API names, identifiers, configuration keys, CLI flags, source
  excerpts, and official product names exactly.
- Translate general English prose when a precise Korean technical term exists;
  do not translate code tokens or invent literal Korean expansions.

Choose the term that names the software state or operation precisely:

| Avoid when imprecise | Prefer when the meaning matches |
|---|---|
| `값을 바꾼다` | `값을 변경한다` |
| `결과를 돌려준다` | `결과를 반환한다` |
| `쓰기를 막는다` | `쓰기를 차단한다` |
| `결과가 엇갈린다` | `결과가 불일치한다` |
| `계약을 하나로 모은다` | `계약을 단일화한다` |
| `authority boundary` -> `권위 경계` | `책임 경계`, `상태 변경 경계` |
| `source of truth` -> `진실의 원천` | `기준 데이터 원본`, `SSOT` when useful |

Use established Korean loanwords consistently when the domain has approved
them, for example `아웃박스`, `페이로드`, `메트릭`, `트랜잭션`, and `커넥션
풀`. Do not force one Korean word onto every occurrence of an English source
term: distinguish the domain role first, then preserve exact English only when
it is an identifier, official name, or source excerpt.

Do not ban words such as `행` or `영속` globally. A database row can be a `행`,
while an action-queue item is a `조치 메시지(작업 요청)`; a contract may use
`영속`, while reader-facing prose may be clearer as `저장된`. Use the
context-aware audit rules to find candidates, then review the sentence.

## Technical Claim Boundaries

Prose must distinguish adjacent contracts instead of flattening them:

- request acceptance, queue insertion, durable write, and drain completion;
- execution order, shared transaction, idempotency, and exactly-once effects;
- structural parsing, authentication, cryptographic verification, and caller
  trust responsibilities;
- common interface support, optional capabilities, backend overrides, and
  unsupported behavior;
- application-owned, framework-owned, and shared-resource lifecycles;
- current implementation, released-tag behavior, proposed design, and roadmap.

When these distinctions matter, name the actual boundary and evidence. Do not
turn a source-backed checklist into domain-specific prose rules here; record
one-off findings in the task lesson.

## Humor And Voice

- Keep humor only when Korean engineers would naturally use it and the failure
  remains clear.
- Remove invented metaphors, translated jokes, and promotional phrasing.
- Prefer a direct failure description over `딱 좋다`, `빡빡하다`, `귀찮다`,
  or a clever but unfamiliar expression.
- Preserve accepted author voice unless it obscures meaning or changes the
  artifact's register.

## English Localization

For English counterparts, remove clusters of generic AI-preferred wording such
as `delve`, `tapestry`, `multifaceted`, `pivotal`, `robust`, `seamless`, and
`groundbreaking` when a simpler technical word is more precise. Do not ban
individual words mechanically.

## Blocking Naturalness Checklist

- [ ] **KO-01 — Freeze meaning-bearing evidence**
  - **Action:** Preserve facts, identifiers, links, genre, and uncertainty.
  - **Evidence:** before/after fact ledger with no unexplained semantic change.
  - **Failure:** revert meaning-changing edits.
- [ ] **KO-02 — Replace hollow claims**
  - **Action:** Replace generic importance, efficiency, and benefit language
    with behavior or evidence.
  - **Evidence:** claim-level review tied to current sources.
  - **Failure:** delete or qualify unsupported emphasis.
- [ ] **KO-03 — Remove translationese and formulaic structure**
  - **Action:** Repair English sentence skeletons, mechanical lists,
    transitions, and nominalization.
  - **Evidence:** sentence-level naturalness review.
  - **Failure:** keep the paragraph blocked.
- [ ] **KO-04 — Verify register and terminology**
  - **Action:** Keep identifiers exact, terms consistent, and predicates
    compatible with their subjects.
  - **Evidence:** terminology and artifact-register pass.
  - **Failure:** repair ambiguous or casual phrasing.
- [ ] **KO-05 — Bound humor and voice**
  - **Action:** Keep only familiar, clarifying Korean engineering idioms.
  - **Evidence:** no invented metaphor or obscured claim.
  - **Failure:** make the sentence direct.
- [ ] **KO-06 — Verify every reader-facing surface**
  - **Action:** Review body, metadata, tables, links, captions, alt text, and
    diagram labels; verify paired locale links at the intended ref.
  - **Evidence:** final content and link review.
  - **Failure:** do not approve partial localization or stale facts.
- [ ] **KO-07 — Run the contextual terminology audit**
  - **Action:** Run `node ~/.codex/skills/bluetape-writer/scripts/audit-korean-terms.mjs`
    for each changed Korean file after facts and code tokens are frozen.
  - **Evidence:** machine-readable or text report, with every finding repaired
    or recorded as an intentional context-specific exception.
  - **Failure:** do not approve the draft while a terminology collision is
    unexplained; never repair it with a global replacement.

Promote a new global rule only when multiple independent tasks demonstrate the
same reusable failure. Otherwise keep the finding in the task lesson.
