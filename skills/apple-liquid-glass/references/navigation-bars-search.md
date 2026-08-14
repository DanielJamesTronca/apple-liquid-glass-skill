# Navigation, bars, and search

Load for toolbars, tab bars, sidebars, and search placement.

## Bars are automatic — subtraction first

Standard bars adopt Liquid Glass on recompile. The first adoption pass is
removing what now conflicts:

- Custom toolbar/tab bar backgrounds and tints
- `UIVisualEffectView` blur strips behind bars
- Custom tab bars that only ever existed to look modern
- Hard-coded bar foreground colours

HIG Toolbars: *"Reduce the use of toolbar backgrounds and tinted controls. Any
custom backgrounds and appearances you use might overlay or interfere with
background effects that the system provides. Instead, use the content layer to
inform the color and appearance of the toolbar, and use a `ScrollEdgeEffectStyle`
when necessary to distinguish the toolbar area from the content area."*

## Toolbar composition

- **Prominence**: HIG — *"Use the `.prominent` style for key actions such as
  Done or Submit … Only specify one primary action, and put it on the trailing
  side of the toolbar."*
- **Grouping**: related items share a glass background. Use `ToolbarSpacer` to
  separate groups that should read as distinct.
- **Concentric corners**: standard components get this automatically; custom
  ones must match the bar's corner curvature.
- **Dropping the shared background** (e.g. a profile photo that should not sit
  on glass):

```swift
ToolbarItem(placement: .topBarTrailing) {
    ProfileImage()
}
.sharedBackgroundVisibility(.hidden)   // iOS/macOS 26.0
```

The modifier belongs on `ToolbarItem` (or other `ToolbarContent`), not the view
inside it. Hiding the shared background can also change grouping and spacing,
so use it only when the item should genuinely appear bare.

```swift
// Wrong: the toolbar item still owns the shared background.
ToolbarItem(placement: .topBarTrailing) {
    ProfileImage().sharedBackgroundVisibility(.hidden)
}

// Right
ToolbarItem(placement: .topBarTrailing) { ProfileImage() }
    .sharedBackgroundVisibility(.hidden)
```

- **Colour**: HIG — *"Avoid applying a similar color to toolbar item labels and
  content layer backgrounds. If your app already has bright, colorful content
  … prefer using the default monochromatic appearance."*

## OS 27 beta toolbar APIs (check availability)

```swift
// iOS/iPadOS/Catalyst/visionOS 27 beta only — NOT macOS
ToolbarItem(placement: .topBarPinnedTrailing) { ShareButton() }

ToolbarOverflowMenu {          // same platform restriction
    ChoosePhotoButton()
    ExportAsImageButton()
}

ToolbarItemGroup { UndoButton(); RedoButton() }
    .visibilityPriority(.high)   // iOS 27 beta / macOS 26.1

.toolbarMinimizationBehavior(.onScrollDown, for: .navigationBar)  // 27, all platforms
```

OS 27 beta also provides `toolbarMinimizationRestoration(_:for:)` and
`toolbarMinimizationSafeAreaAdjustment(_:for:)`. Keep their defaults unless the
product has a specific restoration requirement or manages full-bleed content
while the bar minimizes; disabling safe-area adjustment transfers inset
responsibility to the app.

`tabBarMinimizeBehavior(_:)` is iOS 26 and unchanged — do not migrate it to the
"minimization" spelling.

## Search placement (WWDC26 292)

Apple's search field supplies a leading search icon, placeholder text, a clear
button, and — on iOS when focused — a Cancel button. Critically:

> "Depending on where your Search Field is placed, it will automatically adopt
> the correct presentation style. Such as using glass when placed in a Toolbar
> or using standard content styling when placed in the scroll region."

So **placement is the decision; styling is not**. Never apply `.glassEffect()`
to a search field.

### iPhone

| Placement | When |
|---|---|
| **Bottom toolbar (preferred)** | Default. Field animates up over the keyboard — best for reachability. |
| Top toolbar | When the bottom bar is occupied (e.g. a persistent sheet). |
| Inline in content | When search should stay at the top and avoid bottom UI. |
| **Search tab** | Tab-based apps. A standard tab navigates to a landing page with the field at top. |
| **Prominent search tab** | Button appearance — *"tapping will immediately engage search, and bring up the keyboard."* |

### iPad and macOS

Place the primary field in the **trailing position of the toolbar**, at the top
of the sidebar, or in a dedicated search tab/section.

- Split-view apps searching across columns (like Mail) → trailing toolbar. The
  field scales or collapses to a button as space allows.
- Filtering content that lives in the sidebar (like Settings) → sidebar.
- Apple: *"I recommend trying to keep your iPad and Mac search experiences as
  closely aligned as possible."*

### Choosing

Two questions from the session: how are people navigating the app (does a tab
bar need accommodating?), and what is the **scope** of search — placement
changes people's perception of what is being searched.

"Search as a tab on iPhone, a field on iPad" is a normal, correct answer: a
search tab on compact, trailing toolbar field on regular.

## Sidebars

System components; glass is automatic. HIG notes glass *"appears more opaque in
larger elements like sidebars to preserve legibility over complex backgrounds."*
That opacity is intentional — do not fight it with a custom background.

macOS 27 beta: sidebars extend to window edges, selection is semi-bold, bordered
toolbar items over the sidebar adopt glass.

## Sources

HIG Toolbars; HIG Color; WWDC26 292 (Design intuitive search experiences);
WWDC26 269; WWDC26 278; WWDC25 356.
