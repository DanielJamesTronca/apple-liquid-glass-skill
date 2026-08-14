# Design decision tree

The judgment layer. Load this whenever the real question is *should* this be
glass, not *how* to write glass.

## The two layers

Apple's model, stated in WWDC26 251 (Communicate your brand identity on iOS):

> "Think of your app as two distinct layers: the UI layer, which serves as the
> global navigation, and the content layer, which sits beneath these controls
> and contains all the features that make your app unique."

- **UI layer** — tab bars, toolbars, sidebars, floating controls. Glass lives
  here. Use standard components; they adopt glass automatically.
- **Content layer** — your app's actual substance. Glass does **not** belong
  here. HIG Materials: *"Don't use Liquid Glass in the content layer …
  including it in the content layer can result in unnecessary complexity and a
  confusing visual hierarchy."* Use standard materials instead.

Single documented exception: a control in the content layer with a *transient*
interactive element — a slider or toggle — may take on glass while active.

## Walking the tree

**1. Content or functional UI?**
Feed cards, list rows, article bodies, chart surfaces, badges, empty states →
content layer → not glass. Say so plainly and offer the standard material.

**2. Does a system component already exist?**
`TabView`, `.toolbar`, `NavigationSplitView`, `.sheet`, `.searchable`, `Menu`,
`.alert`, `.popover` all adopt glass automatically on recompile. The correct
change is often to *delete* custom chrome, not add glass to it.

**3. Does content move beneath it?**
If no changing content passes beneath a candidate control, glass provides little
visual benefit. Prefer a flat design unless a documented functional reason
remains; HIG Materials remains the authority for the content/UI-layer split.

**4. Interactive?**
Glass signals "you can act on this." On non-interactive chrome it misleads.
`.interactive()` on something that does not respond to touch is always wrong.

**5. Would a plain background be clearer?**
Ask it honestly. Legibility beats material fidelity every time.

**6. Near other glass?**
Only then reach for a container — see below.

**7. Regular or clear?**
`.regular` by default. `.clear` requires **all three**: floats over visually
rich media, the media must stay prominent, and a dimming layer is present.

**8. Does tint mean something?**
State, or one primary action. Otherwise no tint.

**9–11.** Deployment target, OS 27 beta deltas, verification plan — see SKILL.md §5.

## When to use a container (corrected rule)

**Wrong:** "use a `GlassEffectContainer` whenever there is more than one glass
view." That over-groups unrelated elements and produces blending between things
that should stay separate.

**Right:** one container for glass that is **near each other and logically
related** — elements that should share sampling, blend as they approach, or
morph between states. A floating control cluster in the bottom-trailing corner
is one container. A toolbar at the top and a control at the bottom are not
related and share nothing; two containers, or more likely zero, since the
toolbar is a system component.

Never nest containers. Nesting produces double-sampling and unpredictable
blending.

## Rejecting a request well

Requests like "apply Liquid Glass to every card in this feed" should be
declined, with the reasoning and a concrete alternative:

> Cards are content, and HIG is explicit that Liquid Glass doesn't belong in
> the content layer — glassing every card flattens the hierarchy that makes
> glass legible in the first place, and costs performance on long feeds. What
> I'd do instead: leave the cards on a standard material, and let the floating
> controls above them carry the glass. If you want the feed to feel lighter,
> `backgroundExtensionEffect()` under the nav bar gets you that without
> touching the cards.

Give the alternative. "No" alone is not a deliverable.

## Judgment calls that come up repeatedly

| Situation | Answer |
|---|---|
| Badge or pill on a content card | Not glass. Content layer. |
| Floating map/camera control cluster | Glass, one container, regular variant. |
| Video player controls | Glass, clear variant + dimming layer. |
| Toolbar buttons | Already glass. Add nothing. |
| Custom tab bar replacing `TabView` | Reconsider the custom bar first. |
| Onboarding hero card | Not glass. Content. |
| Sheet background | System handles it; don't override `presentationBackground`. |
| Sidebar | System component; glass automatic, more opaque by design. |
| Widget | Different system entirely — see `widgets.md`. |

## Brand expression

WWDC26 251 is the reference: express brand in the **content layer**, not by
recolouring bars. Apple's specific guidance is to move colour *into* the scroll
view so glass controls pick it up dynamically, rather than painting toolbars —
and that custom replacements for utilitarian components *"can make the product
appear less native — or even dated."*

## Sources

HIG Materials; HIG Color § Liquid Glass color; HIG Toolbars; WWDC25 219 (Meet
Liquid Glass); WWDC25 356; WWDC26 251.
