---
name: apple-liquid-glass
description: Design, implement, review, and migrate Apple Liquid Glass UI. Use for SwiftUI, UIKit, AppKit, WidgetKit, CarPlay, or Icon Composer work involving Liquid Glass, glassEffect, GlassEffectContainer, UIGlassEffect, NSGlassEffectView, glass button styles, system bars or presentations, widgets, app icons, accessibility, performance, or OS 26-to-27 migration. Do not use for non-Apple glassmorphism or general Apple UI work unrelated to Liquid Glass.
---

# Apple Liquid Glass

Treat Liquid Glass as the functional layer for controls and navigation above
content, not as decoration. Prefer system components and subtraction before
writing custom glass.

## Workflow

### 1. Inspect the target

Determine the active SDK, deployment targets, frameworks, and whether the app
can be built or rendered before recommending code.

```bash
xcodebuild -version
python3 scripts/audit_liquid_glass.py <project-path> --json
rg --no-filename -o --glob '*.swift' '^import (SwiftUI|UIKit|AppKit|WidgetKit|CarPlay)$' \
  <project-path> | sort | uniq -c
```

Honor `DEVELOPER_DIR` or another project-selected toolchain. Do not add OS 26
availability branches when every deployment target is 26 or newer. When the
project builds with an Xcode 27 beta SDK, load
`references/migration-26-to-27.md` and verify beta declarations against the
active SDK or current Apple documentation.

### 2. Decide whether glass belongs

Stop at the first disqualifying answer:

1. Is this functional UI rather than content?
2. Is there no system component that already provides the behavior?
3. Does the element float above content that can move or change beneath it?
4. Is it interactive, or otherwise essential functional chrome?
5. Is glass clearer than a plain or standard-material treatment?

If any answer is no, do not add custom glass. Explain why and offer a concrete
system or standard-material alternative. For ambiguous design requests, load
`references/design-decision-tree.md`.

### 3. Route only to relevant guidance

| Target or task | Load |
|---|---|
| SwiftUI code | `references/swiftui.md` |
| UIKit code | `references/uikit.md` |
| AppKit code | `references/appkit.md` |
| Mixed-framework code | Each framework file actually used |
| Bars, navigation, sidebars, or search | `references/navigation-bars-search.md` |
| Sheets, menus, alerts, or popovers | `references/presentations.md` |
| WidgetKit | `references/widgets.md` |
| App icons, symbols, Icon Composer, or CarPlay icons | `references/icons-and-symbols.md` |
| Custom-control accessibility | `references/accessibility.md` |
| Hitches, profiling, snapshots, or visual testing | `references/performance-and-testing.md` |
| OS 26 to OS 27 beta migration | `references/migration-26-to-27.md` |
| Code review or “looks wrong” diagnosis | `references/common-failures.md` |
| Citation, conflict, or availability question | `references/sources.md` |

Do not load SwiftUI guidance for a pure UIKit or AppKit task. For whole-app
adoption, work in this order: recompile, bars/navigation, search,
presentations, custom controls, icons, then widgets.

### 4. Implement the smallest correct change

- Prefer standard toolbars, tab bars, sidebars, search, and presentations;
  remove custom backgrounds that compete with their automatic glass.
- Use the framework's glass button style for buttons. Do not place a raw glass
  effect behind a button.
- Apply a custom glass effect after sizing and padding, before positioning.
- Group only nearby, related glass that must share sampling, blend, or morph.
  Never nest glass containers.
- Do not imitate Liquid Glass with custom blur or invented opacity constants.
- Let system foreground colors adapt unless a documented semantic color is
  required.

Keep framework-specific signatures, variants, fallbacks, and examples in the
routed reference instead of inferring them from this summary.

### 5. Verify the result

Require:

1. A build against the intended SDK.
2. Light, dark, plain, and visually busy backdrops.
3. Reduce Transparency, Increase Contrast, and Reduce Motion.
4. Both Liquid Glass preference extremes when targeting OS 27 beta.
5. A real device for motion, lensing, or performance-sensitive work.

Never claim a visual result that has not been rendered. If the app cannot run,
state that limitation and give the user the remaining checks.

## Script

Resolve paths relative to this skill directory.

```bash
python3 scripts/audit_liquid_glass.py <project-path>
python3 scripts/audit_liquid_glass.py <project-path> --json --min-confidence high
```

Treat audit findings as leads, not verdicts. Read the surrounding code, layer,
deployment target, and runtime backdrop before editing.

On Xcode 27 beta, also run `xcrun agent skills export` and prefer
matching-version Apple guidance where it overlaps this skill. Use
`references/sources.md` when a beta API, availability claim, or source conflict
needs current verification.

## Definition of done

- Keep glass out of the content layer unless Apple documents the exception.
- Use system components wherever they cover the interaction.
- Account for the active framework, SDK, and deployment targets.
- Build the change and report which visual and accessibility checks ran.
- Verify every asserted beta API against current documentation.
