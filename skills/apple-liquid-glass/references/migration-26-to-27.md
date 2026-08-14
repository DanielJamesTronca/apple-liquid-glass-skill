# Migrating OS 26 → OS 27 beta

Load when the project builds against the Xcode 27 beta SDK, or the user reports that
bars/menus/icons changed after an upgrade.

## Contents

- [No-code behavior changes](#what-happens-with-no-code-change)
- [Liquid Glass preference](#the-user-facing-liquid-glass-slider)
- [SwiftUI](#swiftui-changes)
- [UIKit](#uikit-changes)
- [AppKit](#appkit-changes-macos-27-beta)
- [App icons](#app-icons)
- [Migration checklist](#migration-checklist)

Read the current iOS/iPadOS and macOS 27 release notes before adding a
workaround. Apple is still fixing Liquid Glass rendering and interaction bugs
between betas; a workaround for an earlier seed can become the defect in the
next one. Record the beta build used for every reproduction.

OS 27 beta guidance **does not erase** OS 26 behavior. If the deployment target
still includes 26, both rules apply — route by SDK *and* deployment target.

## What happens with no code change

On OS 27 beta, apps already using Liquid Glass receive the refined appearance
automatically without code changes. WWDC26 269 confirms that glass
*"automatically responds to the new Liquid Glass slider to adjust its tint."*

`UIDesignRequiresCompatibility` is **removed** in Xcode 27 beta. The opt-out that
existed in Xcode 26 is gone; adoption is not optional once you build with the
new SDK. Delete the key if it is still in Info.plist — it does nothing.

## The user-facing Liquid Glass slider

OS 27 beta adds a system setting letting people adjust Liquid Glass intensity/tint.
Consequences:

- Your layout must hold at **both extremes**. Test both.
- Never hard-code an opacity to "match" system glass — the user can move it.
- Custom blur imitations now visibly desynchronise from real glass when the
  slider moves. This is the strongest practical argument for deleting them.

## SwiftUI changes

| Change | Detail |
|---|---|
| `toolbarMinimizationBehavior(_:for:)` | **New in 27**, all platforms. The OS 26 toolbar-minimize spelling is no longer in current docs — verify the symbol in your SDK if you support both. |
| `toolbarMinimizationRestoration(_:for:)` | **New in 27**, all platforms. Leave automatic unless restoration behavior is an explicit product decision. |
| `toolbarMinimizationSafeAreaAdjustment(_:for:)` | **New in 27**, all platforms. Disable only when the app deliberately manages full-bleed insets during minimization. |
| `tabBarMinimizeBehavior(_:)` | **Unchanged**, still iOS 26.0. Do not "migrate" it. |
| `ToolbarOverflowMenu` / `toolbarOverflowMenu(content:)` | New in 27, **iOS/iPadOS/Catalyst/visionOS only** — no macOS/watchOS/tvOS. Guard cross-platform code. |
| `ToolbarItemPlacement.topBarPinnedTrailing` | New in 27, **no macOS**. |
| `ToolbarContent.visibilityPriority(_:)` | iOS 27 beta, but **macOS 26.1** — availability is not uniform. |
| Interactive glass on Mac | Custom glass elements can be marked interactive to respond to clicks. |
| iPad inactive appearance | Apps dim icons/text when inactive; check custom chrome still reads correctly. `@Environment(\.appearsActive)` exposes this. |

## UIKit changes

From WWDC26 278 (Modernize your UIKit app):

- **Scroll edge effects**: *"the `.automatic` style no longer switches between
  the existing soft and hard styles but provides its own visuals."* Apple's
  explicit instruction: *"If you have overridden the style from `.automatic`
  previously, that decision should be re-evaluated, especially when set to
  `.soft`, as that no longer matches the default system appearance."* **This is
  the single highest-yield migration check in a UIKit app.**
- **Menu images**: *"images you set on menu elements may not be shown by
  default in some contexts, such as in the menu bars on iPadOS and macOS."* Set
  `preferredImageVisibility` if an image must remain visible.
- **Navigation bars** minimize on scroll; force with
  `navigationItem.barMinimizationBehavior = .always / .never`, and set
  `barMinimizationSafeAreaAdjustment = .never` if you manage safe area yourself.
- **iPhone sidebars**: opt in with `tabBarController.sidebar.preferredPlacement
  = .sidebar`. There is no user-facing toggle — the system decides based on
  available space. Check `sidebar.isAvailable` and surface the same UI via
  nested tabs when it is not.
- **Prominent tab**: `tabBarController.prominentTabIdentifier = "cart"` stays
  visible even when the tab bar collapses on scroll.
- **Ask Siri** appears in menus automatically when content is relevant; do not
  hand-roll one.

## AppKit changes (macOS 27 beta)

From WWDC26 289 (Modernize your AppKit app):

- `NSScrollEdgeEffectStyle` resolves to a **hard** edge effect when free-floating
  text (e.g. a window title) sits in the bar.
- **Sidebars** extend to the window's edges; selection uses a semi-bold text
  style; content still flows behind.
- **Bordered toolbar items** over the sidebar adopt Liquid Glass.
- **Interactive glass** is new — glass bounces subtly on click. Apple: *"Use
  with controls and buttons … A little goes a long way!"*
- **`NSViewCornerConfiguration`** (macOS 27 beta) gives real concentricity:

```swift
class LocalWeatherView: NSView {
    override var cornerConfiguration: NSViewCornerConfiguration? {
        let radius: NSViewCornerRadius = .containerConcentric(minimumCornerRadius)
        return .uniformCorners(radius: radius)
    }
}
```

## App icons

Review every existing Icon Composer file in Xcode 27 beta. Rendering may change, so
do not assume an OS 26 sign-off is still valid; confirm current Icon Composer
documentation before changing translucency, highlights, or refraction.

1. **Reduced translucency.** OS 27 beta reduced translucency for sharper icons; that
   change does not apply retroactively to your settings.
2. **Specular highlights** (now automatic inside/outside based on layer and
   background colour) and **refraction on overlapping layers**.

Back deployment needs no special workflow: *"For legacy OS versions, the system
faithfully renders your current design with the appropriate corner radius."*

## Migration checklist

- [ ] Remove `UIDesignRequiresCompatibility` from Info.plist.
- [ ] Re-evaluate every non-`.automatic` scroll edge effect style, especially `.soft`.
- [ ] Audit menu images; add `preferredImageVisibility` only where needed.
- [ ] Verify OS 27 beta-only toolbar APIs are guarded on macOS/watchOS/tvOS.
- [ ] If toolbar minimization is customized, verify restoration and safe-area behavior while scrolling.
- [ ] Check layout at both ends of the Liquid Glass slider.
- [ ] Re-open Icon Composer file; review translucency, highlights, refraction.
- [ ] Delete custom blur imitations — they desync from the slider.
- [ ] Re-test accessibility variants; the material changed underneath them.

## Sources

WWDC26 269, 278, 289; Apple API documentation for each symbol (see
`sources.md`). Availability strings verified against developer.apple.com.
