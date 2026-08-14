# SwiftUI — Liquid Glass

Default path. Every symbol below was verified against Apple's documentation
JSON; availability strings are Apple's, not inferred.

## Contents

- [API surface](#verified-api-surface)
- [Buttons](#buttons--the-most-common-mistake)
- [Modifier order](#modifier-order)
- [Custom bars](#custom-safe-area-bars)
- [Containers and morphing](#containers-unions-morphing)
- [Variants and interaction](#clear-variant)
- [Back deployment](#back-deployment)
- [Concentricity](#concentricity)

## Verified API surface

| API | Availability | Notes |
|---|---|---|
| `glassEffect(_:in:)` | iOS/iPadOS/Catalyst/macOS/tvOS/watchOS 26.0 | `func glassEffect(_ glass: Glass = .regular, in shape: some Shape = DefaultGlassEffectShape()) -> some View` |
| `Glass` | iOS/iPadOS/Catalyst/macOS/tvOS/watchOS 26.0 | `.regular`, `.clear`, `.identity`; `.tint(Color?)`, `.interactive(Bool = true)` |
| `Glass.identity` | Same as `Glass` | Content unaffected, as if no glass applied; use for conditional glass without branching |
| `GlassEffectContainer` | iOS/iPadOS/Catalyst/macOS/tvOS/watchOS 26.0 | `init(spacing: CGFloat?, content: () -> Content)` |
| `glassEffectID(_:in:)` | iOS/iPadOS/Catalyst/macOS/tvOS/watchOS 26.0 | `(some Hashable & Sendable)?`, `Namespace.ID` |
| `glassEffectUnion(id:namespace:)` | iOS/iPadOS/Catalyst/macOS/tvOS/watchOS 26.0 | Fuses several shapes into one glass shape |
| `glassEffectTransition(_:)` | iOS/iPadOS/Catalyst/macOS/tvOS/watchOS 26.0 | Takes `GlassEffectTransition` |
| `PrimitiveButtonStyle.glass` | iOS/iPadOS/Catalyst/macOS/tvOS/watchOS 26.0 | `GlassButtonStyle` |
| `PrimitiveButtonStyle.glassProminent` | iOS/iPadOS/Catalyst/macOS/tvOS/watchOS 26.0 | `GlassProminentButtonStyle` |
| `ConcentricRectangle` | All Apple platforms 26.0, including visionOS | Squared, rounded, and container-concentric corners |
| `backgroundExtensionEffect()` | All Apple platforms 26.0, including visionOS | Mirrors and blurs the view into adjacent safe area |
| `safeAreaBar(edge:alignment:spacing:content:)` | All Apple platforms 26.0, including visionOS | Places custom edge chrome and extends affected scroll-edge effects |
| `ToolbarContent.sharedBackgroundVisibility(_:)` | iOS/iPadOS/Catalyst/macOS 26.0 | `.hidden` drops the shared glass background for an item |
| `tabBarMinimizeBehavior(_:)` | 26.0 (all platforms) | Still current; not renamed |
| `ToolbarContent.visibilityPriority(_:)` | iOS/iPadOS/Catalyst/tvOS/watchOS/visionOS **27.0 beta**; macOS 26.1 | `ToolbarItemVisibilityPriority` |
| `toolbarMinimizationBehavior(_:for:)` | **27.0 beta** (all platforms) | Supersedes the OS 26 toolbar spelling; see migration file |
| `toolbarMinimizationRestoration(_:for:)` | **27.0 beta** (all platforms) | Controls how a minimized toolbar restores |
| `toolbarMinimizationSafeAreaAdjustment(_:for:)` | **27.0 beta** (all platforms) | Controls whether safe areas update during minimization |
| `ToolbarOverflowMenu` | **27.0 beta** iOS/iPadOS/Catalyst/visionOS | **No macOS, watchOS, tvOS.** Also `View.toolbarOverflowMenu(content:)` |
| `ToolbarItemPlacement.topBarPinnedTrailing` | **27.0 beta** iOS/iPadOS/Catalyst/visionOS | **No macOS.** Pins an item to the trailing edge |

Note the asymmetry: `tabBarMinimizeBehavior` kept its OS 26 name; the toolbar
equivalent is `toolbarMinimizationBehavior(_:for:)` and is OS 27 beta-only. Do not
assume the two follow the same naming.

## Buttons — the most common mistake

```swift
// WRONG — a button sitting on top of a glass slab
Button("Save") { save() }
    .glassEffect()

// RIGHT
Button("Save") { save() }
    .buttonStyle(.glass)
    .buttonBorderShape(.capsule)

// RIGHT — single primary action only
Button("Done") { done() }
    .buttonStyle(.glassProminent)
```

Use the documented `.buttonStyle(.glass)` / `.glassProminent` APIs for custom
functional buttons, and apply `buttonBorderShape` when needed. Standard toolbar
and navigation controls remain system-managed; do not add a competing custom
glass treatment. Verify visual behaviour in the target SDK rather than relying
on the unavailable Group Lab transcript.

## Modifier order

`glassEffect` anchors to the view's bounds *including padding*, so order is
semantic, not cosmetic.

```swift
Image(systemName: "location.fill")
    .font(.title2)          // 1. content sizing
    .padding(12)            // 2. grow the glass shape
    .glassEffect(in: .circle)   // 3. material fills that shape
    .padding(.trailing, 16) // 4. position the finished element
```

Padding after `glassEffect` moves the element; padding before it enlarges the
glass. Putting `.frame` after the effect is the usual cause of "my glass is the
wrong size."

## Custom safe-area bars

Prefer a standard toolbar or tab bar first. When the app genuinely needs custom
fixed chrome at an edge, use `safeAreaBar` instead of pinning a glass view with
an overlay or `VStack`. It updates the safe area and continues the scroll-edge
effect behind the bar. It does not justify applying one large `glassEffect` to
the whole bar; style the actual controls appropriately.

```swift
content
    .safeAreaBar(edge: .bottom) {
        HStack {
            Button("Share") { share() }.buttonStyle(.glass)
            Button("Done") { done() }.buttonStyle(.glassProminent)
        }
    }
```

When back-deploying below 26, use `safeAreaInset` as the structural fallback
and a standard material, not an imitation of Liquid Glass.

For edge-to-edge media that doesn't naturally fill the adjacent safe area,
`backgroundExtensionEffect()` extends that content behind the functional layer.
It is a layout effect, not a way to turn content into glass.

## Containers, unions, morphing

Use one container for glass that is **near and related** — sharing sampling,
blending as it approaches, or morphing. Not for every pair of glass views on
screen, and never nested.

```swift
@Namespace private var glassNamespace
@State private var expanded = false

GlassEffectContainer(spacing: 20) {
    HStack(spacing: 12) {
        Button { withAnimation(.spring) { expanded.toggle() } } label: {
            Image(systemName: "plus")
        }
        .buttonStyle(.glass)
        .glassEffectID("toggle", in: glassNamespace)

        if expanded {
            ForEach(actions) { action in
                ActionButton(action)
                    .buttonStyle(.glass)
                    .glassEffectID(action.id, in: glassNamespace)
            }
        }
    }
}
```

Morphing needs all three of: one container, matching `glassEffectID` values in
a shared namespace, and an **animated** state change. `glassEffectID` without
`withAnimation` (or an `.animation` modifier) does nothing visible.

Use `glassEffectUnion(id:namespace:)` when several shapes should read as a
single piece of glass rather than morph between states.

## Clear variant

```swift
ZStack {
    VideoPlayer(player: player)
    Color.black.opacity(0.35)     // dimming layer — required over bright media
    controls.glassEffect(.clear, in: .rect(cornerRadius: 22))
}
```

Apple's `Glass.clear` documentation: *"When using clear glass, ensure content
remains legible by adding a dimming layer or other treatment beneath the
glass."* HIG gives the number: ≈35% dark layer when underlying content is
bright; unnecessary when it is already dark, or when AVKit's standard playback
controls supply their own.

## Tint

```swift
.glassEffect(.regular.tint(isRecording ? .red : nil))
```

Tint communicates state or marks one primary action. HIG: apply colour to the
*background* rather than the symbol, and *"refrain from adding color to the
background of multiple controls."* A tinted row of five buttons is a defect.

## Interactive

`.interactive()` makes glass flex and respond to touch. Apply it only to things
that actually respond to touch. On a static badge it is wrong. AppKit's
equivalent arrives in macOS 27 beta (see `appkit.md`); Apple's guidance there —
*"A little goes a long way!"* — applies everywhere.

## Back deployment

Only when the deployment target is below 26. If it is 26+, availability
branches are dead code and should be deleted.

```swift
extension View {
    @ViewBuilder
    func floatingControlBackground() -> some View {
        if #available(iOS 26, macOS 26, *) {
            glassEffect(in: .capsule)
        } else {
            background(.ultraThinMaterial, in: .capsule)   // approximation, not glass
        }
    }
}
```

`.ultraThinMaterial` is a *fallback*, not a reproduction. Never present it as
equivalent, and never use it on OS 26+ to "match" glass.

`Glass.identity` avoids branching when you want glass conditionally on a
supported OS:

```swift
.glassEffect(isFloating ? .regular : .identity, in: .capsule)
```

## Concentricity

```swift
// Corners that follow the container instead of a guessed radius
.clipShape(ConcentricRectangle(corners: .concentric, isUniform: true))
```

HIG (Toolbars): *"By default, standard buttons, text fields, headers, and
footers have corner radii that are concentric with bar corners. If you need to
create a custom component, ensure that its corner radius is also concentric."*

## Sources

WWDC26 269 (What's new in SwiftUI), WWDC25 323
(Build a SwiftUI app with the new design), WWDC25 256, HIG Materials, HIG
Toolbars, and the API pages listed above. Verification policy and source
precedence live in `sources.md`.
