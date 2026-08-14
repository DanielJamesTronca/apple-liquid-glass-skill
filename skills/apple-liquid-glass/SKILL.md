---
name: apple-liquid-glass
description: Design, implement, review, and migrate Liquid Glass UI on Apple platforms across OS 26 and OS 27 betas. Use for SwiftUI, UIKit, AppKit, WidgetKit, CarPlay, or Icon Composer work involving Liquid Glass adoption, custom glass controls, code review, OS 26-to-27-beta migration, toolbars, tab bars, search, sheets, widgets, app icons, or deciding whether glass belongs in a design. Trigger on Liquid Glass, glassEffect, GlassEffectContainer, UIGlassEffect, NSGlassEffectView, buttonStyle(.glass), scroll edge effects, CarPlay glass controls, and Icon Composer. Do not use for unrelated glassmorphism on non-Apple platforms.
---

# Apple Liquid Glass

Liquid Glass is the material for the **functional UI layer** — controls and
navigation that float above content. It is not a decorative finish. Most
correct adoptions add *less* custom code, not more, because system components
adopt glass automatically on recompile.

**Default assumption: the user does not need custom glass.** Prove otherwise
with the decision tree before writing a single `glassEffect`.

## 1. Detect before advising

Run these before recommending anything. Never assume the framework or target.

```bash
# Deployment target(s) — decides whether fallbacks are needed at all
grep -rhoE '(IPHONEOS|MACOSX|WATCHOS|TVOS|XROS)_DEPLOYMENT_TARGET = [0-9.]+' \
  --include=project.pbxproj . | sort -u
# Active toolchain — decides whether OS 26 or OS 27 beta declarations apply
xcodebuild -version
# Framework mix — decides which reference file to load
find . -name '*.swift' -print0 \
  | xargs -0 grep -hoE 'import (SwiftUI|UIKit|AppKit|WidgetKit|CarPlay)' | sort | uniq -c
# Xcode 26 compatibility opt-out — removed in Xcode 27 beta
grep -rl 'UIDesignRequiresCompatibility' --include='*.plist' .
```

If the project selects Xcode explicitly (for example with `DEVELOPER_DIR`), run
the toolchain check in that environment rather than assuming the system default.

| Finding | Consequence |
|---|---|
| Deployment target ≥ 26 | **No availability fallbacks.** Do not write `if #available` for glass. |
| Deployment target < 26 | Fallbacks required — see `references/swiftui.md` § Back deployment. |
| Xcode 27 beta SDK | OS 27 beta behavior applies; `UIDesignRequiresCompatibility` is gone. Load `references/migration-26-to-27.md`. |
| SwiftUI only | Load `references/swiftui.md` only. |
| UIKit / AppKit present | Load `references/uikit.md` / `references/appkit.md` **in addition**, not instead. |
| WidgetKit / CarPlay present | Also load `references/widgets.md` / `references/icons-and-symbols.md`. |

## 2. Route the request

| User is asking to… | Do this |
|---|---|
| Adopt glass in an existing app | Recompile first, audit what the system already did, then close gaps. §3 → §4 |
| Build a new glass component | Decision tree §3, then `references/swiftui.md` (or uikit/appkit) |
| Add fixed custom bar chrome | Prefer a system toolbar; otherwise `references/swiftui.md` § Custom safe-area bars |
| Review existing code | Run `scripts/audit_liquid_glass.py`, then `references/common-failures.md` |
| Migrate OS 26 → OS 27 beta | `references/migration-26-to-27.md` |
| Decide *whether* to use glass | Decision tree §3 — expect the answer to be "no" |

Adoption order for a whole app: **recompile → fix bars/navigation → search →
presentations → custom controls → icons → widgets**. Do not start with custom
controls; most of them stop being necessary after the bars are correct.

## 3. Decision tree (mandatory, before any code)

Answer these in order. Stop at the first one that disqualifies glass.

1. **Content or functional UI?** Content layer → **not glass.** HIG: *"Don't
   use Liquid Glass in the content layer."* Use a standard material instead.
   (Exception: transient interactive elements like a slider's active thumb.)
2. **Does a system component already do this?** Toolbar, tab bar, sidebar,
   sheet, alert, popover, menu, search field → **use it and add nothing.**
   Toolbar and navigation-bar buttons already receive the correct glass.
3. **Does it float above scrolling/changing content?** If nothing passes
   beneath it, there is nothing to refract; flat design is better.
4. **Is it interactive?** Non-interactive chrome rarely earns glass, and never
   earns `.interactive()`.
5. **Would a plain background be clearer?** If yes, use it.
6. **Is it near other glass?** Only then consider `GlassEffectContainer` —
   for glass that shares sampling, blends, or morphs. Not "whenever there are
   two glass views." Never nest containers.
7. **Regular or clear?** `.regular` unless **all** hold: it floats over
   visually rich media, underlying content must stay prominent, and you supply
   a dimming layer (≈35% black when content is bright; none needed if content
   is dark or AVKit supplies its own).
8. **Does tint carry meaning?** Tint only for state or a single primary
   action. HIG: apply color to the *background*, not the symbol, and never to
   several controls at once.
9. **Deployment target below 26?** Only now write availability branches.
10. **Does OS 27 beta change an assumption here?** Check
    `references/migration-26-to-27.md` before hard-coding bar behavior.
11. **How will this be verified?** Name the check now — see §5.

If the answer to 1–5 is "system component," say so and stop. Deleting a custom
blur is a valid and common deliverable.

## 4. Minimal implementation rules

These hold on every platform; framework specifics live in the reference files.

- **Never** put a raw `.glassEffect()` behind a `Button`. That yields a button
  sitting *on* glass. Use `.buttonStyle(.glass)` or `.buttonStyle(.glassProminent)`,
  shaped with `.buttonBorderShape(_:)`.
- Apply `.glassEffect()` **after** sizing/padding modifiers — it anchors to the
  view's bounds, padding included — and **before** positioning ones.
- Do not stack glass on glass. Do not add custom backgrounds to bars; use the
  content layer to colour them and a `ScrollEdgeEffectStyle` to separate.
- Do not reimplement glass with `.ultraThinMaterial`, `UIBlurEffect`, or a
  hand-tuned blur. There are no public opacity/blur constants to match —
  inventing numbers is a defect, not an approximation.
- Morphing requires all three: a shared `@Namespace`, `.glassEffectID(_:in:)`
  on each participant, and an **animated** state change, inside one
  `GlassEffectContainer`.
- Prefer `ConcentricRectangle` (or `.rect(corners: .concentric)`) over guessed
  corner radii for anything inside a rounded container.
- Let foreground colours come from the system. Hard-coded `.foregroundColor`
  on glass breaks the automatic light/dark adaptation that keeps it legible.

## 5. Verification is part of the task

A code change is not done when it compiles. Require, and say you require:

1. **A real build** against the intended SDK.
2. **Varied backgrounds** — light, dark, busy photo, video. Glass is defined by
   what is behind it, so a single screenshot proves nothing.
3. **Accessibility settings on**: Reduce Transparency, Increase Contrast,
   Reduce Motion. Each changes the material; all three must stay legible.
4. **The OS 27 beta Liquid Glass slider** at both extremes, if targeting OS 27 beta.
5. **Device, not just simulator**, for anything with motion or lensing.

Never claim a visual result you have not seen. If you cannot run the app, state
what the user must check and hand them the list.

## 6. Load references on demand

Read only what the current task needs.

| File | Load when |
|---|---|
| `references/design-decision-tree.md` | Judgment calls, "should this be glass?", rejecting a request |
| `references/swiftui.md` | Any SwiftUI work (default path) |
| `references/uikit.md` | Project imports UIKit |
| `references/appkit.md` | Project imports AppKit |
| `references/navigation-bars-search.md` | Toolbars, tab bars, sidebars, search placement |
| `references/presentations.md` | Sheets, menus, alerts, popovers |
| `references/accessibility.md` | Custom controls, VoiceOver, contrast/transparency settings |
| `references/performance-and-testing.md` | Hitches, profiling, snapshot/visual testing |
| `references/migration-26-to-27.md` | Xcode 27 beta upgrade, OS 27 beta behavior changes |
| `references/widgets.md` | WidgetKit, accented/tinted/clear rendering |
| `references/icons-and-symbols.md` | App icons, Icon Composer, SF Symbols, CarPlay control icons |
| `references/common-failures.md` | Reviewing code, diagnosing "it looks wrong" |
| `references/sources.md` | Citing a rule, checking provenance or OS version |

Use `references/sources.md` to resolve conflicting guidance and check the
verification boundary. Verify beta APIs against current documentation rather
than inferring names or availability from session transcripts.

## 7. Scripts

Paths are relative to this skill's directory, so run them from there or use an
absolute path.

```bash
python3 scripts/audit_liquid_glass.py <path>      # report leads, not verdicts
python3 scripts/audit_liquid_glass.py <path> --json --min-confidence high
```

`audit_liquid_glass.py` emits **leads requiring inspection**, never automatic
rewrites. A flagged line may well be correct in context; read it before acting.

On a Mac with Xcode 27 beta, also run `xcrun agent skills export` and prefer Apple's
own exported skills where they overlap this one — they outrank everything here
except current API documentation.

## 8. Final checklist

- [ ] Glass is confined to the functional UI layer, not content.
- [ ] Every system component that could do the job is doing the job.
- [ ] Custom edge bars use the platform's safe-area bar API, not a hand-pinned glass slab.
- [ ] No raw `glassEffect` behind a `Button`; glass button styles used instead.
- [ ] Containers group *related* glass only; none nested.
- [ ] `.clear` used only over rich media, with a dimming layer.
- [ ] Tint expresses meaning, on backgrounds, on at most one primary action.
- [ ] No custom blur imitating glass; no invented opacity constants.
- [ ] Availability branches exist **only** if deployment target < 26.
- [ ] OS 26 vs OS 27 beta differences accounted for and cited.
- [ ] Accessibility variants and multiple backgrounds actually checked.
- [ ] Every asserted API verified against current documentation.

---

Design judgment, source-linked rules, and OS 26/27 routing are built from
Apple's WWDC25/WWDC26 sessions, the Human Interface Guidelines, and API
documentation. Where this contradicts advice circulating elsewhere, the
reasoning is in `references/common-failures.md` § Corrections.
