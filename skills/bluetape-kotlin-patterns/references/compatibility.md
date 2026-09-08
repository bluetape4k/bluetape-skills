# Kotlin JVM and Serialization Compatibility

Use when changing published signatures, generated JVM owners, data-class
construction, enums, or serialized formats. Evaluate only compatibility promises
that the affected API/version actually makes; an intentional breaking release
needs an explicit migration decision, not an invented compatibility shim.

## Published JVM Surface

- Kotlin source compatibility does not prove binary compatibility. A defaulted
  constructor parameter can change constructor, `copy`, and `copy$default`
  descriptors. Inspect affected constructors, overloads, component methods,
  generated facades/owners, and Java callers.
- For claimed binary compatibility, run a prior-compiled consumer against the
  new artifact or the repository's ABI check with equivalent linkage coverage.
  Fresh Kotlin/Java source recompilation is a separate check.
- Moving a top-level function can change its `*Kt` owner even if its Kotlin
  import is unchanged. Preserve published owners or document an approved break.
  Internal build helpers with no published consumer are not automatically ABI.
- Check enum names and persisted ordinals only where their consumers or wire
  formats depend on them. Do not impose ordinal stability on private enums.
- Constructor validation must also cover generated `copy` and relevant
  deserialization paths. `Serializable` and an unchanged `serialVersionUID`
  alone do not prove legacy-stream compatibility: distinguish missing fields
  from explicitly supplied default/zero values where semantics differ.

## Cross-Version Payloads

- Keep current roundtrip tests separate from old-producer/new-reader tests.
  Record the actual old producer version, dependency/catalog ref, fixture hash,
  schema/type registration, and serializer mode. Do not regenerate the old
  fixture with the upgraded dependency and call it historical evidence.
- Test only promised directions and supported modes; schema-consistent and
  schema-compatible formats are not interchangeable by assumption.
- Assert decoded semantics and malformed-input behavior. Require exact bytes
  only for a byte-stability contract; an upgrade need not change wire bytes.
  Keep unrelated serializer warm-up outside decode-timeout measurements.

## Blocking Compatibility Checklist

- [ ] **KT-ABI-01 — Check published linkage**
  - **Action:** Inventory changed JVM signatures/owners and affected Java/Kotlin consumers; exercise claimed prior-binary linkage separately from source compilation.
  - **Evidence:** ABI report or prior-compiled fixture, or concrete non-published/no-compatibility-promise N/A.
  - **Failure:** Reject source-only compatibility claims or record the approved breaking migration.
- [ ] **KT-ABI-02 — Verify model evolution**
  - **Action:** Test relevant generated construction, legacy missing/default fields, and consumed enum identities.
  - **Evidence:** Targeted invariant/legacy-stream tests and consumer-specific enum checks, or concrete N/A.
  - **Failure:** Do not infer validation or serialized compatibility from defaults/serialVersionUID.
- [ ] **KT-ABI-03 — Pin cross-version fixtures**
  - **Action:** Verify fixture producer provenance and promised reader/writer directions and modes separately from current roundtrip.
  - **Evidence:** Version/ref/hash manifest, decoded semantics, malformed-input checks, or concrete N/A.
  - **Failure:** Reject mislabeled historical fixtures and unsupported cross-mode claims.
