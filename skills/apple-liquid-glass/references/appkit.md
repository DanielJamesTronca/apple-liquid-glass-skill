# AppKit — Liquid Glass

Load for AppKit code. In a mixed SwiftUI/AppKit project, also load `swiftui.md`.

## Verified API surface

| API | Availability | Notes |
|---|---|---|
| `NSGlassEffectView` | macOS 26.0 | *"A view that embeds its content view in a dynamic glass effect."* |
| `NSGlassEffectContainerView` | macOS 26.0 | *"Efficiently merges descendant glass effect views together when they are within a specified proximity."* |
| `NSViewCornerConfiguration` | **macOS 27.0 beta** | Concentric corner configuration |

Note `NSGlassEffectContainerView`'s own documentation states the merge is
proximity-based — which is precisely why a container should wrap *nearby*
glass, not all glass in a window.

```swift
let glassView = NSGlassEffectView()
glassView.contentView = customControl

let container = NSGlassEffectContainerView()
container.contentView = stackOfNearbyGlassViews
```

## What is automatic (macOS 26)

Recompiling gives glass to `NSToolbar`, sidebars, sheets, popovers, and menus.
Remove hand-rolled `NSVisualEffectView` chrome behind those.

## macOS 27 beta refinements

- **Scroll edge effects**: `NSScrollEdgeEffectStyle` resolves to a **hard**
  edge effect when free-floating text — such as the window title in the title
  bar — is present.
- **Sidebars** now extend to the window's edges, selection uses a semi-bold
  text style, and content continues to flow behind them.
- **Bordered toolbar items** placed over the sidebar adopt Liquid Glass.
- **Interactive glass**: glass can bounce subtly on click. Apple's guidance:
  use it *"with controls and buttons"* and *"with glass containers of
  interactive controls"* — and *"A little goes a long way!"* Maps uses it for
  custom controls.

## Concentricity (macOS 27 beta)

`NSViewCornerConfiguration` replaces guessed radii. From WWDC26 289:

```swift
class LocalWeatherView: NSView {
    override var cornerConfiguration: NSViewCornerConfiguration? {
        let radius: NSViewCornerRadius = .containerConcentric(minimumCornerRadius)
        return .uniformCorners(radius: radius)
    }
}
```

Key pieces:

- `cornerConfiguration` — override on the `NSView` subclass.
- `NSViewCornerRadius.containerConcentric(_:)` — derives radius from the
  container, with a minimum so corners are always rounded.
- `NSViewCornerConfiguration.uniformCorners(radius:)` — same radius on all four.

The design principle: the closer a view sits to its container's corner, the
more its own radius should match that curve.

## Toolbars and grouping

Group related toolbar items so they share one glass background rather than
each rendering separately; separate unrelated groups so they read as distinct.
Prominence should mark a single primary action — the same "one primary action"
rule as every other platform.

If a Mac toolbar's grouping looks wrong, the usual causes are: unrelated items
sharing a group, every item marked prominent, or a custom background view
competing with the system's.

## Mixed SwiftUI + AppKit

WWDC26 272 confirms that incremental SwiftUI adoption alongside AppKit is
supported and that system-control glass uses shared SwiftUI rendering. Choose
SwiftUI or `NSGlassEffectView` for a custom surface based on the project's
ownership and lifecycle; the session does not prescribe one host framework.

## Sources

WWDC26 289 (Modernize your AppKit app); WWDC25 310 (Build an AppKit app with
the new design); WWDC26 272; API pages for `NSGlassEffectView`,
`NSGlassEffectContainerView`, `NSViewCornerConfiguration`.
