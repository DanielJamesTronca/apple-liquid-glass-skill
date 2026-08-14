<p align="center">
  <img src="assets/liquid-glass-cover.png" alt="Abstract translucent glass panels in a dark blue-grey space" width="100%">
</p>

<h1 align="center">Apple Liquid Glass</h1>

<p align="center">
  Practical design and implementation guidance for Liquid Glass on Apple platforms.
</p>

<p align="center">
  <a href="https://github.com/DanielJamesTronca/apple-liquid-glass-skill/actions/workflows/ci.yml"><img src="https://github.com/DanielJamesTronca/apple-liquid-glass-skill/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-4b5563.svg" alt="MIT License"></a>
</p>

Most Liquid Glass work should begin by removing custom chrome, not adding more
of it. System bars, search, sheets, menus, and popovers already adapt when an
app builds with the current SDK. This skill helps an agent decide when custom
glass is justified, use the right API for the active framework, and review
results in context.

## Install

For Agent Skills clients such as Codex, Claude Code, and Cursor:

```bash
npx skills add DanielJamesTronca/apple-liquid-glass-skill -g
```

In Codex, ask `$skill-installer` to install `apple-liquid-glass` from this
repository. For Claude Code's plugin marketplace:

```text
/plugin marketplace add DanielJamesTronca/apple-liquid-glass-skill
/plugin install apple-liquid-glass@apple-liquid-glass-skill
```

Run `/reload-plugins` if Claude Code asks you to activate the plugin.

## What it covers

| Need | The skill helps you |
|---|---|
| Adopt Liquid Glass in an existing app | Recompile first, then inspect bars, search, presentations, custom controls, icons, and widgets. |
| Build or review a custom control | Decide whether glass belongs there before selecting the framework API. |
| Upgrade to Xcode 27 beta | Separate OS 26 behaviour from current beta changes and verify availability. |
| Work in SwiftUI, UIKit, or AppKit | Load only the relevant framework reference. |
| Check widgets, icons, accessibility, or performance | Use the focused reference without pulling unrelated guidance into context. |

## The design position

Liquid Glass belongs to the functional layer: navigation, controls, and other
interactive elements above content. Cards, list rows, and decorative content
surfaces usually should not use it. The skill prefers system components,
concentric shapes, semantic tint, and accessibility checks over hand-made blur
or arbitrary opacity values.

## Included tooling

The bundled audit reports conservative leads for a Swift project; it never
rewrites code or treats a match as a verdict.

```bash
python3 skills/apple-liquid-glass/scripts/audit_liquid_glass.py path/to/Sources
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

`tests/skill_evals.json` records positive and negative trigger prompts so
routing changes can be checked without pretending a keyword matcher measures
agent behaviour.

## Sources and scope

This is a curated snapshot reviewed against Apple API documentation, Human
Interface Guidelines, WWDC sessions, Group Labs, sample code, and release notes
on 14 August 2026. It prioritizes the decisions and APIs that recur in real
projects instead of reproducing Apple's documentation. For a consequential beta
claim, verify the declaration against the Xcode version in use.

## Contributing

Corrections need an Apple source and the affected OS versions. See
[CONTRIBUTING.md](CONTRIBUTING.md) for source precedence, test commands, and
the prompt-evaluation workflow.

Released under the [MIT License](LICENSE). This project is independent and is
not affiliated with or endorsed by Apple.
