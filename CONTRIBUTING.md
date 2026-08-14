# Contributing

Corrections need the Apple source that supports the change and the OS versions it affects.

## The one hard rule

Every rule must trace to a source and an OS version. Plausible API names and remembered availability do not count.

Specifically: **never take an API name from a WWDC transcript.** Verify it against the
documentation. Transcripts garble identifiers, and this repo exists partly because that keeps
happening:

| Heard in a session | Actual symbol |
|---|---|
| `.toolbarMinimizeBehavior(_:for:)` | `toolbarMinimizationBehavior(_:for:)` (iOS 27 beta) |
| `visibilityPriority` on a view | `ToolbarContent.visibilityPriority(_:)` |

## Verifying an API before you cite it

Apple's HTML doc pages are JavaScript-rendered and return only a title to a plain fetch. The
underlying JSON is what you want:

```bash
# API reference
curl -s "https://developer.apple.com/tutorials/data/documentation/swiftui/glass.json" | \
  python3 -m json.tool | head -40

# HIG page
curl -s "https://developer.apple.com/tutorials/data/design/human-interface-guidelines/materials.json"
```

The `metadata.platforms` array is the authoritative availability, including `beta` and `deprecated`
flags. Quote it exactly — availability is frequently **not uniform across platforms**, and getting
that wrong is worse than omitting the API.

## Source precedence

When sources disagree, resolve in this order:

1. Current Apple API documentation
2. Current HIG
3. Newest WWDC session or Group Lab
4. Apple sample code
5. Apple's exported Xcode skills (`xcrun agent skills export`), matching Xcode version
6. Older Apple sessions
7. Reproducible community implementations

OS 27 beta guidance must not erase OS 26 behavior. Keep both and route by SDK and deployment target.

## Adding or changing a rule

1. Verify against the documentation JSON above.
2. Put it in the right reference file. `SKILL.md` stays under 250 lines and holds routing and
   judgment, not API detail.
3. Cite the source in the affected reference file.
4. Run the tests below.

Community posts can expose useful edge cases, but they do not outrank current Apple documentation.
Keep a community-derived rule only when it is reproducible, primary sources are silent, and the
reference file says so plainly.

## Changing the audit script

`audit_liquid_glass.py` reports leads, never verdicts. Glass
correctness depends on runtime context a regex cannot see. Keep it:

- **Conservative.** A false positive on correct code costs more trust than a missed lead.
- **Backward-looking** for context matching. A modifier attaches to what precedes it; looking
  forward produces phantom findings from unrelated later code.
- **Explanatory.** Every check needs an `inspect` string telling the reader what to check and when
  the flagged pattern is legitimate.

Any new check needs a case in both fixtures:

- `tests/fixtures/BadGlass.swift` should produce the lead.
- `tests/fixtures/GoodGlass.swift` must stay clean at `--min-confidence medium`.

A high-confidence finding in `GoodGlass.swift` is a bug in the audit, not the fixture.

## Running the tests

```bash
python3 tests/test_audit.py
```

This checks that the bad fixture produces the expected leads, the good fixture produces no
medium-or-higher findings, JSON mode is well-formed, linked references exist, and plugin manifests
parse. CI runs the same suite on every push.

## Reporting a wrong rule

Open an issue with the Rule correction template. Include the reference file and line, what it
currently says, what it should say, and the Apple source. Screenshots of rendered UI help for
design-judgment disagreements.
