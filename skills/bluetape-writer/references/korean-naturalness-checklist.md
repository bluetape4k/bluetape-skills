# Korean Naturalness Checklist

Use this for Korean bluetape4k blog drafts that read like translated prose, generic AI prose, or marketing copy. The goal is natural technical writing, not detector evasion.

## Preservation Rules

- Preserve facts, numbers, dates, commands, source links, benchmark values, identifiers, product names, and direct quotes.
- Preserve the article genre. Do not turn an engineering note into an essay, press release, or sales page.
- Change only what improves clarity, rhythm, or Korean naturalness.
- Prefer small local edits over rewriting a whole section.
- If the evidence is uncertain, keep the uncertainty explicit. Do not make cautious claims sound stronger than the source supports.

## Core Principle

Specific beats generic. Facts beat significance claims. Direct beats over-hedged prose.

- Replace "중요합니다" with why it matters in this code path.
- Replace "효율적입니다" with the measured result, removed step, or simpler failure mode.
- Replace "다양한 장점을 제공합니다" with the two or three concrete advantages that the article actually proves.

## Korean Translationese

Prefer natural Korean technical phrasing:

| Avoid | Prefer |
|---|---|
| `~를 통해` | `~로`, `~해서`, or the concrete verb |
| `~에 있어서` | `~에서`, `~할 때`, `여기서` |
| `~되어진다` | `~된다`, or active voice |
| `가지고 있다` | `있다`, `제공한다`, `담고 있다` only when concrete |
| `~에 의해 생성된` | `~가 만든`, `~에서 만든` |
| `~할 수 있을 것으로 보인다` | `~할 수 있다`, `~로 보인다`, or state the evidence |
| `~할 필요가 있다` | `~해야 한다`, or explain the condition |

## LLM-Like Structure

Revise formulaic structure when it adds no clarity:

- Avoid mechanical `첫째/둘째/셋째` unless the sequence is genuinely ordered.
- Avoid triplets that list three broad virtues, such as "빠르고, 유연하고, 안정적인".
- Avoid "A뿐만 아니라 B도" when "A와 B" is enough.
- Avoid "X부터 Y까지" unless X and Y are real endpoints of a range.
- Avoid ending with a vague future outlook. End with the concrete operational lesson or the next article link.

## Hollow Emphasis

Do not claim importance when the article can show it:

- Replace `주목할 만하다`, `시사하는 바가 크다`, `혁신적이다`, `강력하다`, `포괄적이다` with concrete behavior.
- Replace anonymous authority such as "업계에서는", "많은 개발자가" with a named source, project evidence, or deletion.
- Remove promotional phrases that do not add information.

## Rhythm And Flow

- Vary sentence length, but do not force drama.
- Keep paragraph openings concrete. Avoid repeated `또한`, `따라서`, `즉`, `나아가`.
- Prefer short transitions: `그래서`, `문제는`, `반대로`, `실제로`, `이제`.
- Split long sentences when they carry more than one idea.
- Merge tiny sentences when they create a choppy checklist feel.

## Technical Voice

- Use concrete verbs: `읽고`, `저장하고`, `무효화하고`, `재시도하고`, `측정합니다`.
- Keep identical concepts under identical names. Do not rotate `캐시`, `저장소`, `계층`, `구성요소` if they refer to different or same things ambiguously.
- Keep Korean prose natural, but keep public API names, class names, method names, configuration keys, and CLI flags exact.
- Keep light humor close to the engineering pain. Remove jokes that obscure a claim.

## Humor And Korean Sentence Sense

Natural Korean comes before wit. If a sentence is funny only after translating
it back to English, rewrite it.

- Prefer Korean engineering idioms developers actually use: `삽질했다`, `똥
  치우기`, `뚜껑이 열린다`, `장애가 터진다`, `엄격하게 검증한다`.
- Do not create new metaphors just to be playful. If the phrase sounds clever
  but unfamiliar in Korean technical writing, delete it or make it direct.
- Check the sentence owner. Blog prose should explain the library or user
  problem, not the writer's private impression.
- Check noun and predicate compatibility. Ranges are `작다/크다`, not
  `짧다/길다`; code is `조심히 다뤄야 한다`, not `진지하다`; validation
  `검증한다`, not `겨냥한다`.
- Keep humor proportional to the failure mode. Cache inconsistency is dangerous,
  not merely `귀찮다`; routing validation is `엄격하다`, not `빡빡하다`.

Recent accepted corrections:

| Avoid | Prefer |
|---|---|
| `버그도 성실해집니다` | `버그가 여러 곳에서 발호합니다` |
| `중복 header도 그냥 넘기지 않습니다` | `중복 header도 그냥 넘기면 안 됩니다` |
| `입력 경계를 넣어두면 덜 미끄러집니다` | `입력 경계를 넣어두면 추가 작업이 줄고 완성도가 높아집니다` |
| `테스트도 이 위험을 그대로 겨냥합니다` | `테스트도 이 위험을 검증합니다` |
| `PATCH ... 빡빡하게 처리합니다` | `PATCH ... 엄격하게 처리합니다` |
| `이 예제 값들은 장식이 아닙니다` | `이 예제의 실행 결과 값들은 실제 수행한 결과입니다` |
| `이런 검증은 조금 귀찮습니다. 하지만` | `이런 검증은 조금 귀찮습니다만,` |

## English Localization Pass

For English blog posts or bilingual localization:

- Scan for clusters of AI-preferred English words such as `delve`, `tapestry`, `landscape`, `nuanced`, `multifaceted`, `pivotal`, `crucial`, `foster`, `underscore`, `showcase`, `leverage`, `intricate`, `comprehensive`, `robust`, `seamless`, `groundbreaking`.
- Do not ban these words mechanically. Replace them when several cluster in a paragraph or when a simpler word is more precise.
- Prefer `use`, `show`, `explain`, `support`, `key`, `solid`, `field`, and direct technical nouns when they fit.

## Final Pass

- Does every paragraph either advance the technical explanation, provide evidence, or guide the reader through the source?
- Are claims supported by code, docs, benchmark numbers, commands, or links?
- Could a Korean engineer say this sentence naturally in a technical conversation?
- Does the humor use a Korean expression developers would actually say?
- Is every subject, predicate, and noun pairing natural in Korean?
- Did the edit preserve meaning and avoid over-polishing the author's voice?

## Blocking Naturalness Checklist

- [ ] **KO-01 — Freeze meaning-bearing evidence**
  - **Action:** Preserve facts, numbers, dates, commands, links, benchmark values, identifiers, names, quotes, genre, and uncertainty.
  - **Evidence:** Before/after fact ledger with no unexplained semantic changes.
  - **Failure:** Revert meaning-changing edits before style work.
- [ ] **KO-02 — Replace generic and promotional claims**
  - **Action:** Replace hollow importance/efficiency/benefit language with concrete behavior or evidence and remove anonymous authority.
  - **Evidence:** Claim-level prose review tied to source evidence.
  - **Failure:** Delete or qualify unsupported emphasis.
- [ ] **KO-03 — Remove translationese and formulaic structure**
  - **Action:** Repair English sentence skeletons, mechanical triplets/transitions, vague outlooks, and unnecessary nominalization.
  - **Evidence:** Sentence-level review using the avoid/prefer tables.
  - **Failure:** Keep the paragraph blocked until it reads naturally in Korean technical conversation.
- [ ] **KO-04 — Verify technical vocabulary and sentence sense**
  - **Action:** Keep identifiers exact, concepts consistently named, verbs concrete, and subject/predicate/noun dimensions compatible.
  - **Evidence:** Terminology and semantic-dimension pass.
  - **Failure:** Repair ambiguous term rotation or unnatural predicate pairing.
- [ ] **KO-05 — Bound humor and personal voice**
  - **Action:** Keep only familiar Korean engineering idioms that clarify a real failure mode and preserve accepted user wording.
  - **Evidence:** Humor/voice review with no invented metaphor or obscured claim.
  - **Failure:** Make the sentence direct or remove the joke.
- [ ] **KO-06 — Pass paragraph and localization checks**
  - **Action:** Ensure every paragraph advances explanation/evidence/navigation and, for English, remove clustered AI-preferred wording without mechanical bans.
  - **Evidence:** Final primary and localized prose review.
  - **Failure:** Do not approve filler, over-polish, or literal idiom translation.
