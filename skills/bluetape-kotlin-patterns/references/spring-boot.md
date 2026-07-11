# Spring Boot Kotlin Rules

Use for auto-configuration, configuration properties, conditional beans,
ordering, weaving, or Spring library-module tests.

## Auto-Configuration

- Guard a `compileOnly` bean-signature type with
  `@ConditionalOnClass(name = ["fqcn"])` on the configuration phase.
- Apply `@ConditionalOnProperty` to every phase, not only the entrypoint.
- Ordering annotations affect only classes directly registered in
  `AutoConfiguration.imports`; split ordered phases and register each one.
- Do not rely on same-class or nested `@ConditionalOnBean` ordering when bean
  creation order matters.
- Use an `INHERIT` sentinel when annotation defaults must remain distinguishable
  from property-level global defaults.

## Configuration and Tests

- Prefer constructor/parameter injection and immutable
  `@ConfigurationProperties` values with explicit defaults.
- Prefer Binder `bindOrCreate` when a default instance is required.
- Use `ApplicationContextRunner` for auto-configuration slices.
- In library modules, pair `@SpringBootTest` with a narrow
  `@SpringBootConfiguration` and `@ImportAutoConfiguration`, not a broad
  application scan.
- Compile-time weaving modules do not add `@EnableAspectJAutoProxy`; after
  package moves, search pointcut strings and imports.
- Preserve coroutine cancellation in suspend lifecycle code.

Verify all registered phases, positive/negative conditions, defaults, ordering,
and absence of optional classes with targeted context-runner tests.

## Blocking Spring Checklist

- [ ] **KT-SPR-01 — Guard optional types and phases**
  - **Action:** Apply class-name and property conditions to every required phase containing optional or compileOnly types.
  - **Evidence:** Auto-configuration phase map and condition annotations.
  - **Failure:** Block on any eager optional-type linkage or unguarded phase.
- [ ] **KT-SPR-02 — Prove registration and ordering**
  - **Action:** Register each ordered phase directly and avoid same-class/nested bean-order assumptions.
  - **Evidence:** AutoConfiguration imports and positive/negative ordering tests.
  - **Failure:** Split/reorder phases until the container contract is explicit.
- [ ] **KT-SPR-03 — Preserve configuration semantics**
  - **Action:** Use immutable constructor-bound properties, explicit defaults, Binder creation, and INHERIT sentinel where needed.
  - **Evidence:** Property model and default/override tests.
  - **Failure:** Repair ambiguous or mutable configuration behavior.
- [ ] **KT-SPR-04 — Isolate library tests**
  - **Action:** Use context runners or narrow SpringBootConfiguration/imports and verify optional-class absence.
  - **Evidence:** Targeted slice tests covering presence, absence, defaults, and ordering.
  - **Failure:** Replace broad application scans that hide library boundaries.
- [ ] **KT-SPR-05 — Verify weaving and lifecycle**
  - **Action:** Check pointcut/import drift, avoid redundant proxy enablement, and preserve coroutine cancellation.
  - **Evidence:** Search results and targeted weaving/lifecycle tests, or concrete N/A.
  - **Failure:** Repair stale pointcuts or cancellation handling before PASS.
