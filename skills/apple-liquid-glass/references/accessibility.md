# Accessibility

Liquid Glass is a translucent, motion-bearing material. Accessibility is not a
post-hoc pass here — three system settings change what the material *is*.

## Contents

- [System settings](#the-three-settings-that-change-glass)
- [Adaptive foreground colors](#why-hard-coded-foreground-colours-break-glass)
- [Custom controls](#custom-controls-wwdc26-220)
- [Glass-specific checks](#glass-specific-accessibility-checks)

## The three settings that change glass

| Setting | Effect | What you must check |
|---|---|---|
| **Reduce Transparency** | Glass becomes substantially more opaque | Text/symbol contrast still correct; nothing depended on seeing through |
| **Increase Contrast** | Borders and colour differences become far more apparent | Custom colours don't clash; hierarchy survives |
| **Reduce Motion** | Lensing/morph animations reduced | Custom glass transitions have a reduced path; nothing becomes unreachable |

Test all three. A design that only works with defaults is unfinished.

```swift
@Environment(\.accessibilityReduceTransparency) private var reduceTransparency
@Environment(\.accessibilityReduceMotion) private var reduceMotion

// Morphing: don't animate the morph when Reduce Motion is on
withAnimation(reduceMotion ? nil : .spring) { expanded.toggle() }
```

Do **not** hard-code a substitute appearance for Reduce Transparency — the
system already adapts the material. Hard-coded colours are the usual reason a
view looks wrong *only* with the setting enabled.

## Why hard-coded foreground colours break glass

Glass adapts symbol/text colour to the content behind it — HIG: on toolbars and
tab bars, symbols and text *"become darker when the underlying content is
light, and lighter when it's dark."* A hard-coded `.foregroundColor(.white)`
opts out of that and will become illegible over light content. Let the system
drive it.

## Custom controls (WWDC26 220)

Four things must reach assistive technology: **purpose, value, actions,
feedback**.

```swift
CoffeeFillView(level: coffee)
    .accessibilityElement()
    .accessibilityLabel("Coffee Dispenser")
    .accessibilityValue("\(Int(coffee)) ounces")
```

### Single-axis controls — adjustable trait

```swift
.accessibilityAddTraits(.adjustable)
.accessibilityAdjustableAction { direction in
    switch direction {
    case .increment: increaseCoffeeAmount()
    case .decrement: decreaseCoffeeAmount()
    @unknown default: break
    }
}
```

### Multi-axis or complex — custom actions

```swift
.accessibilityActions("Move Up")    { increaseY(by: 10) }
.accessibilityActions("Move Right") { increaseX(by: 10) }
```

Each action gets a descriptive label VoiceOver reads; users swipe to select and
double-tap to activate.

### Fine-grained adjustment — passthrough

Set the activation point to match the control's current value so the gesture
starts where the value is:

```swift
.accessibilityActivationPoint(UnitPoint(x: 0.5, y: 1 - coffee))
```

Announce changes, but **throttle** them (Apple suggests roughly every 0.3s)
so speech doesn't flood:

```swift
.onChange(of: coffee) { _, newValue in
    if sufficientTimeSinceLastAnnouncement() && valueHasChanged() {
        cacheLastSpokenValue(newValue)
        AccessibilityNotification.Announcement(newValue).post()
    }
}
```

### Gestural controls — direct touch

```swift
.accessibilityDirectTouch([.requiresActivation])
```

- `.requiresActivation` — control ignores direct touch until double-tapped,
  preventing accidental activation while navigating. Use this by default.
- `.silentOnTouch` — VoiceOver stays silent; only when the control provides its
  own audio feedback.

Apple's rule: **even with direct touch, expose custom actions too**, so Switch
Control and Voice Control users can still operate the control.

## Glass-specific accessibility checks

- Every glass button has a meaningful label. Icon-only glass buttons are the
  most common offender — a capsule with an SF Symbol and no label is unusable.
- Hit targets stay ≥44×44pt even when the visual glass shape is smaller.
- Tint is never the *only* carrier of state; pair it with a symbol or label.
- Text over `.clear` glass has a dimming layer — contrast is a requirement, not
  an aesthetic preference.
- Dynamic Type: WWDC26 251 — Dynamic Type is built into system fonts, but with
  custom fonts *"you'll need to build support, and test for this."* Glass
  shapes must grow with the text they contain.

## Sources

WWDC26 220 (Refine accessibility for custom controls); WWDC26 251; WWDC25 219;
WWDC25 316 (Principles of inclusive app design); HIG Materials; HIG Color;
HIG Accessibility.
