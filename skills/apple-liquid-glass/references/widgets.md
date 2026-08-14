# Widgets

Widgets are a **separate rendering system** from in-app Liquid Glass. Do not
apply `glassEffect()` in a widget to "match" the system — the system applies
the appearance itself, and your job is to render correctly *into* it.

## Rendering modes

`WidgetRenderingMode` (via `@Environment(\.widgetRenderingMode)`) tells you how
the widget is being drawn: `.fullColor`, `.accented`, `.vibrant`.

`WidgetAccentedRenderingMode` (iOS 18.0+, macOS 15.0+, watchOS 11.0+,
visionOS 26.0) controls how an individual `Image` behaves in accented mode:

| Value | Behavior |
|---|---|
| `.fullColor` | Image keeps its own colours |
| `.accented` | Image is tinted with the accent colour group |
| `.desaturated` | Image is desaturated |
| `.accentedDesaturated` | Desaturated, then accented |

```swift
Image("logo")
    .widgetAccentedRenderingMode(.desaturated)
```

Group content into accent vs. background using `.widgetAccentable()`:

```swift
VStack {
    Text("Steps").widgetAccentable()
    Text("8,432")
}
```

## Clear and tinted appearances

Home Screen widgets can be shown in clear/tinted appearances alongside icons.
Two rules:

1. **Remove opaque backgrounds.** A hard-coded background defeats the system's
   appearance handling. Use `containerBackground(for: .widget)` and let the
   system decide what to draw:

```swift
.containerBackground(for: .widget) {
    Color.clear      // or a gradient the system can treat as removable
}
```

2. **Keep features consistent across appearances.** As with app icons, the
   widget must remain recognisable in every appearance rather than swapping
   elements per mode.

## visionOS textures

visionOS widgets use a separate coating system. The default is
`WidgetTexture.glass`; choose `.paper` only when the widget needs a matte,
poster-like treatment:

```swift
AppIntentConfiguration(/* ... */) { entry in
    WidgetView(entry: entry)
}
.widgetTexture(.paper)
```

Glass keeps foreground content bright and separates it from the backplate;
Paper responds more strongly to ambient lighting. Test both at different room
brightness and viewing distances. This texture API is not `glassEffect()` and
must not be used as a model for in-app Liquid Glass controls.

## Reviewing a widget for glass

| Lead | Action |
|---|---|
| `glassEffect()` in widget code | Remove — widgets don't take in-app glass |
| Opaque `background(...)` on the root | Move to `containerBackground(for: .widget)` |
| Hard-coded white/black text | Won't survive accented/vibrant; use system colours |
| No `widgetAccentable()` anywhere | Accented mode likely renders as an undifferentiated blob |
| Images with no accented rendering mode | Set one explicitly per image |
| Colour-only status encoding | Fails in desaturated/accented; add a symbol |

## Testing

Preview every mode — full colour, accented, tinted, clear — in both light and
dark, at every supported family size. Accented mode is where most widgets
break, because it discards colour information the design depended on.

## Sources

WWDC25 255 (Design widgets for visionOS); WWDC25 278 (What's new in widgets);
WWDC25 317 (What's new in visionOS 26); WWDC26 277 (WidgetKit foundations);
`WidgetAccentedRenderingMode` API documentation; HIG Widgets; Apple's
"Optimizing widgets for accented rendering and Liquid Glass" and "Preparing
widgets for additional contexts and appearances"; "Updating your widgets for
visionOS".
