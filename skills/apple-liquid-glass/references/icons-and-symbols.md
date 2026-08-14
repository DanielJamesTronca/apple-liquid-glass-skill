# App icons and SF Symbols

## App icons are Liquid Glass now

HIG App icons: iOS, iPadOS, macOS, and watchOS icons *"include a background
layer and one or more foreground layers that coalesce to create dimensionality.
These icons take on Liquid Glass attributes like specular highlights,
refraction, and translucency."*

Two consequences: a flat exported PNG no longer looks native, and icons *"can
appear differently between system versions"* — so an icon signed off on OS 26
needs re-checking on OS 27 beta.

## Icon Composer workflow

- Design in layers; **imported layers render as glass by default**.
- **Group layers** — Liquid Glass properties (specular highlights, refraction,
  translucency) apply at the *group* level, so grouping is what gives you
  independent control.
- Individual layers can opt out of glass, for pre-rendered raster art or
  decorative watermarks.
- Import layers **fully opaque** and adjust transparency inside Icon Composer,
  so you can preview how system effects and your transparency interact.
- HIG: *"Vary opacity in foreground layers to increase the sense of depth."*

**Xcode integration:** save the `.icon` file, drag it into Xcode, then choose
it as the app icon in the Project Editor.

## Appearance variants

People choose **default, dark, clear, or tinted** Home Screen icons. You can
supply each; the system generates any you don't.

HIG rules:

- *"Keep your icon's features consistent across appearances."* Don't swap
  elements per variant — it makes the app harder to find.
- Design dark/clear/tinted variants to sit comfortably beside system icons.
  Dark icons are more subdued; clear and tinted more so again.
- **Alternate app icons need their own dark, clear, and tinted variants**, and
  all variants are subject to app review.

## Shape per platform

Square with system-applied rounding on iOS/iPadOS/macOS (matching the device
bezel curvature), rectangular with concentric edges on tvOS, circular masking
on visionOS and watchOS. Don't bake corner rounding into artwork.

## Migrating an OS 26 icon to OS 27 beta

Inspect every icon in the current Icon Composer and its target appearances.
Rendering can change between OS releases, so verify actual output on every
supported platform rather than relying on unavailable Group Lab quotations.

**Evaluate at every size**, especially the smallest — grouped on a Home Screen,
outdoors, and beside other icons. *"Simplicity is what lets an icon scale and
hold presence."*

## SF Symbols

Prefer SF Symbols over custom iconography in glass controls: they carry correct
weight, alignment, and vibrancy automatically, and they adapt with the material.

WWDC25 337 (SF Symbols 7) adds Draw effects, Magic Replace, variable draw, and
gradients. Two cautions in a glass context:

- Symbol animations and glass morphs both draw attention — running them
  together on the same control usually reads as noise.
- Honour Reduce Motion for symbol effects, same as for glass transitions.

For custom iconography, prefer familiar, legible symbols and verify Dynamic Type
and accessibility behaviour; WWDC26 251 supports custom-font and
recognizability guidance but is not the authority for Icon Composer-specific
rules.

## CarPlay controls

On iOS 26, buttons in `CPMapTemplate` adopt Liquid Glass automatically. Do not
add a custom glass background. Review every `CPMapButton` and `CPBarButton`
image against the material, then test it in CarPlay Simulator. The icon must
remain legible over changing map content and in every supported vehicle layout.

## Sources

HIG App icons; WWDC25 220 (Say hello to the new look of app icons); WWDC25 361
(Create icons with Icon Composer); WWDC25 337 (What's new in SF Symbols 7);
WWDC25 216 (Turbocharge your app for CarPlay); WWDC26 251.
