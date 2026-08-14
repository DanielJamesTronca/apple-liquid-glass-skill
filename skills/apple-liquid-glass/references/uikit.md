# UIKit — Liquid Glass

Load in addition to `swiftui.md` when the project imports UIKit.

## Verified API surface

| API | Availability | Notes |
|---|---|---|
| `UIGlassEffect` | iOS/iPadOS/Catalyst/tvOS 26.0 | `init(style: UIGlassEffect.Style)`; `var isInteractive: Bool`; `var tintColor: UIColor?`. **No macOS-native, watchOS, or visionOS.** |
| `UIGlassContainerEffect` | iOS/iPadOS/Catalyst/tvOS 26.0 | Merges multiple glass elements into a combined effect |

Both are applied through `UIVisualEffectView`.

```swift
let effect = UIGlassEffect(style: .regular)
effect.isInteractive = true
effect.tintColor = isRecording ? .systemRed : nil

let view = UIVisualEffectView(effect: effect)
view.contentView.addSubview(control)
```

Container, for related glass that should merge:

```swift
let container = UIVisualEffectView(effect: UIGlassContainerEffect())
container.contentView.addSubview(firstGlassView)
container.contentView.addSubview(secondGlassView)
```

Same rule as SwiftUI: group **nearby, related** glass only, and never nest
containers.

## What is automatic

Recompiling against the iOS 26+ SDK gives glass to `UINavigationBar`,
`UITabBar`, `UIToolbar`, sheets, popovers, menus, and `UISearchController`
without code. The first adoption pass is deleting overrides that now fight the
system:

- Custom `UINavigationBar` background images / `barTintColor`
- `UIVisualEffectView` blur layers hand-placed behind bars
- Custom tab bar replacements that exist only to look modern

## Bars (iOS 27 beta)

```swift
navigationItem.barMinimizationBehavior = .always      // or .never
navigationItem.barMinimizationSafeAreaAdjustment = .never  // if you manage insets
```

Set `barMinimizationSafeAreaAdjustment = .never` only if you handle safe-area
avoidance yourself; otherwise let the system update insets.

**Scroll edge effects — the key OS 27 beta check.** The `.automatic` style no longer
switches between soft and hard; it has its own visuals. Apple: *"If you have
overridden the style from `.automatic` previously, that decision should be
re-evaluated, especially when set to `.soft`, as that no longer matches the
default system appearance."* Grep for `scrollEdgeEffectStyle` and justify every
non-`.automatic` value.

## Tabs and sidebars (iOS 27 beta)

```swift
tabBarController.sidebar.preferredPlacement = .sidebar   // iPhone opt-in
tabBarController.prominentTabIdentifier = "cart"
```

The sidebar is an **app choice** on iPhone with no user-facing toggle; the
system shows it only when space allows (typically regular horizontal size
class). Always check `tabBarController.sidebar.isAvailable` and provide the same
destinations via nested tabs when it is not.

The prominent tab stays visible even when the tab bar collapses during scroll.

## Menus (iOS 27 beta)

Images on menu elements may not be shown by default in some contexts, including
menu bars on iPadOS and macOS. Override only where the image carries meaning:

```swift
menuElement.preferredImageVisibility = .visible
```

Menus automatically show an **Ask Siri** button when there is relevant content.
Do not build your own.

## Drag and drop with Apple Intelligence

Siri can load resources from your drag handlers. Apple's constraint: *"Avoid
performing animations or presenting modal UI from `sessionWillBegin`. Drag
sessions can be initiated without a user gesture."* Move stateful UI into
`sessionDidMove`.

## Custom controls

Before building one, re-read `design-decision-tree.md` §2 — most custom UIKit
controls should become system components. If a custom control genuinely needs
glass:

1. Wrap it in `UIVisualEffectView` with `UIGlassEffect`, don't draw a blur.
2. Set `isInteractive` only if it responds to touch.
3. Give it a concentric corner radius relative to its container.
4. Provide accessibility label/traits/actions — see `accessibility.md`.

## Sources

WWDC26 278 (Modernize your UIKit app); WWDC25 284 (Build a UIKit app with the
new design); WWDC25 243; API pages for `UIGlassEffect` and
`UIGlassContainerEffect`.
