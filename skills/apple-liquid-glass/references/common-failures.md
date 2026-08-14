# Common failures & corrections

Load when reviewing code or diagnosing "my glass looks wrong."

## Diagnostic table

| Symptom | Likely cause | Fix |
|---|---|---|
| Button looks like it sits *on* a glass slab | Raw `.glassEffect()` on a `Button` | `.buttonStyle(.glass)` / `.glassProminent` + `.buttonBorderShape` |
| Glass shape too big / too small | `glassEffect` applied before sizing, or `.frame` after it | Size → pad → `glassEffect` → position |
| Doubled or muddy material in a toolbar | Added glass to items that already get it | Remove it; toolbar items are glass automatically |
| Unrelated controls blend into each other | One container wrapping everything | Split into containers by proximity/relationship, or drop the container |
| Blending is unpredictable | Nested `GlassEffectContainer` | Never nest; flatten to one |
| Morph does nothing | `glassEffectID` without an animated state change, or no shared namespace, or outside a container | All three are required together |
| Text unreadable over video | `.clear` with no dimming layer | ~35% black beneath when content is bright |
| Glass invisible / flat | Nothing scrolling beneath it | It's in the content layer — use a standard material |
| Looks wrong only with Reduce Transparency | Hard-coded colours fighting the fallback | Let system colours adapt; re-test |
| Tinted glass renders black in snapshots | Snapshot host has no real backdrop to sample | Not a code bug — see Testing below |
| Bars behave differently after Xcode 27 beta | OS 27 beta scroll-edge/minimize changes | `migration-26-to-27.md` |
| Menu icons vanished after upgrade | OS 27 beta hides menu images in some contexts | `preferredImageVisibility` |

## Testing: why snapshots mislead

Liquid Glass samples what is behind it. A snapshot test renders the view in
isolation, so there is frequently nothing to sample — tinted glass can come out
black or flat. **This is expected, not a defect to fix in the view code.**

Do not "fix" a failing glass snapshot by hard-coding a background colour into
the production view. Either composite the snapshot over a representative
backdrop, or exclude the material from snapshot assertions and verify it
visually instead. Snapshot-only validation is not sufficient evidence that
glass is correct.

## Corrections

Several rules about Liquid Glass circulate widely — in blog posts, sample
projects, and other agent skills — that are wrong or too broad against current
Apple guidance. If you have seen the left column somewhere, the right column is
what Apple actually says.

| Commonly repeated | What Apple says | Source |
|---|---|---|
| Use a container whenever multiple glass views exist | One container per group of *nearby, related* glass that shares sampling, blends, or morphs | Over-grouping blends unrelated elements; containers are a sampling boundary, not a bag |
| Cards and surfaces are glass candidates | Decide the layer first; content-layer elements are not glass candidates at all | HIG: *"Don't use Liquid Glass in the content layer"* |
| Apply raw glass to buttons | `.buttonStyle(.glass)` / `.glassProminent` + `buttonBorderShape` | SwiftUI API documentation; validate in the target SDK |
| Always provide a pre-26 fallback | Only when the deployment target is below 26 | Dead availability branches on a 26+ target |
| Tint as needed | Tint only for state or one primary action, on backgrounds | HIG: *"refrain from adding color to the background of multiple controls"* |
| API correctness is the main review goal | Review layer choice, structure, accessibility, performance, and OS behavior too | Compiling code can still be the wrong design |
| Static snippets demonstrate success | Require builds, varied backgrounds, accessibility variants, device testing | Glass is defined by what's behind it |

## Review posture

When auditing, report **leads**, not verdicts. `.glassEffect()` on a `Button`
is nearly always wrong; glass inside a `LazyVStack` row usually is; a custom
blur *might* be a deliberate pre-26 fallback. Read the surrounding code, the
deployment target, and the layer the element lives in before proposing an edit.

Rewriting a flagged line without reading its context is itself a failure mode.

## Things never to invent

- Opacity, blur radius, or saturation constants "matching" system glass. There
  are no public values; the OS 27 beta slider makes any guess wrong by definition.
- API names. Verify against current documentation — WWDC transcripts garble
  identifiers. (`toolbarMinimizeBehavior` in a transcript is
  `toolbarMinimizationBehavior(_:for:)` in the SDK; `visibilityPriority` is on
  `ToolbarContent`, not `View`.)
- Availability. Check per platform: `ToolbarOverflowMenu` has no macOS variant;
  `visibilityPriority` shipped on macOS 26.1 but iOS 27 beta.
