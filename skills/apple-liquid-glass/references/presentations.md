# Sheets, menus, alerts, popovers

All of these are system presentations that adopt Liquid Glass automatically.
The correct action is almost always **nothing**.

## Sheets

Sheets get the new appearance on recompile, including inset/floating treatment
at smaller detents.

**Do not override `presentationBackground`.** Setting it to a colour or custom
material replaces the system's glass treatment and is the most common cause of
"my sheet looks wrong after upgrading." If you find it in existing code, that's
a strong lead to remove — check whether it predates OS 26.

```swift
// Suspicious — was this added before OS 26?
.presentationBackground(.regularMaterial)

// Usually correct
.sheet(isPresented: $showing) { DetailView() }
```

Legitimate reasons to keep a custom presentation background are rare: a
full-bleed media sheet where the system material fights the content is the main
one, and even then prefer letting content extend under the material.

Related, still current and useful: `presentationDetents`,
`presentationDragIndicator`, `presentationCornerRadius`.

## Menus

Glass automatically. Two OS 27 beta changes:

1. **Images may be hidden by default** in some contexts, including menu bars on
   iPadOS and macOS. Set `preferredImageVisibility` only where the image
   carries meaning that the label doesn't.
2. **Ask Siri** appears automatically when there's relevant content. Don't
   build your own equivalent.

Don't apply glass to menu content, and don't build a custom menu solely to get
a particular look. Prefer the system `Menu` when it provides the required
interaction and semantics.

## Alerts

Fully system-driven. HIG places alerts among the components that use the
**regular** variant *"when components have a significant amount of text."* No
customisation surface, and none needed.

New in OS 27 beta, alerts and confirmation dialogs take an item binding:

```swift
.alert("Delete?", item: $stickerToDelete) { sticker in
    DeleteStickerButton(sticker)
}

.confirmationDialog("Delete?", item: $stickerToDelete) { sticker in
    DeleteStickerButton(sticker)
}
```

## Popovers

Automatic glass; regular variant, for the same legibility reason as alerts and
sidebars. Keep the anchor correct and let the system size them.

## Reviewing presentations

| Lead | Question to ask |
|---|---|
| `presentationBackground` present | Does this predate OS 26? Remove unless media-driven. |
| `.glassEffect()` inside a sheet's content | Is it functional UI, or content-layer decoration? |
| Custom menu implementation | Would a `Menu` do this now? |
| Custom alert view | Almost certainly should be `.alert`. |
| Blur behind a popover | System provides it; remove. |

## Sources

WWDC25 356; WWDC25 323; WWDC26 269; WWDC26 278; HIG Materials.
