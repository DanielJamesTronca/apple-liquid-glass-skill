# Performance and visual testing

## Why glass costs

Liquid Glass samples and refracts what is behind it. Cost scales with the
number of *separate* glass surfaces, their area, and how often what's behind
them changes. Two consequences:

1. **Glass in a scrolling list is expensive by construction** — every row is a
   new sampling surface over constantly-changing content. This is a performance
   argument on top of the design argument (rows are content layer, so they
   shouldn't be glass anyway).
2. **A container is a performance tool, not just a visual one.** Apple's
   `GlassEffectContainer` documentation: rendering the effects together
   *"improv[es] rendering performance and allow[s] the effects to interact with
   and morph into one another."* `NSGlassEffectContainerView` likewise
   *"efficiently merges descendant glass effect views."*

So: fewer, larger, grouped glass surfaces beat many small independent ones.

## Profiling

Use Instruments on a **real device** — the simulator does not reproduce glass
rendering cost or hitches.

- **SwiftUI template / Hitches**: look for hitches correlated with scrolling
  under glass, and for view bodies re-evaluating during scroll.
- **Animation Hitches**: frame drops when glass morphs or bars minimize.
- Check the oldest device you support, not the newest.

WWDC25 306 (Optimize SwiftUI performance with Instruments) is the reference for
the workflow: profile on device, find the expensive update, fix the cause
rather than the symptom.

## Common performance mistakes

| Mistake | Fix |
|---|---|
| Glass on every cell/row | Remove — content layer, and O(rows) sampling surfaces |
| Many small independent glass views | One `GlassEffectContainer` for the related group |
| Nested containers | Flatten; nesting double-samples |
| Glass over continuously-animating content | Reconsider whether it needs glass |
| Custom blur imitating glass | Usually *more* expensive than the real thing, and desyncs from the OS 27 beta slider |

## Visual testing — what actually validates glass

A compiling build proves nothing about a material defined by its backdrop.

**Required matrix:**

| Axis | Values |
|---|---|
| Appearance | Light, Dark |
| Backdrop | Plain, busy photo, playing video |
| Accessibility | Default, Reduce Transparency, Increase Contrast, Reduce Motion |
| OS 27 beta | Liquid Glass slider at both extremes |
| Hardware | Device (not just simulator) for motion/lensing |

Also check Dynamic Type at large sizes — glass shapes must grow with content.

## Snapshot tests

Snapshot tests render views in isolation, so glass often has **nothing to
sample**. Tinted glass rendering black in a snapshot is expected behavior, not
a bug in the view.

Do not fix a failing glass snapshot by baking a background colour into the
production view. Options, in order of preference:

1. Composite the snapshot over a representative backdrop.
2. Assert on layout/structure and exclude the material from the comparison.
3. Verify the material visually and keep it out of snapshot assertions.

Snapshot-only validation is never sufficient evidence that glass is correct.

## What to tell the user when you can't run the app

State it plainly and hand over the checklist rather than implying you verified
something. For example:

> I can't render this here, so I haven't seen it. Before you ship: check it
> over a photo and a video background in both light and dark, then with Reduce
> Transparency and Increase Contrast on — those three are where this kind of
> change usually breaks.

## Sources

WWDC25 306; `GlassEffectContainer` and `NSGlassEffectContainerView`
API documentation; HIG Materials.
