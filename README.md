<p align="center">
  <img src="assets/liquid-glass-cover.png" alt="Abstract translucent glass panels in a dark blue-grey space" width="100%">
</p>

<h1 align="center">Apple Liquid Glass</h1>

<p align="center">
  An Agent Skill for Liquid Glass work across SwiftUI, UIKit, and AppKit.
</p>

<p align="center">
  <a href="https://github.com/DanielJamesTronca/apple-liquid-glass-skill/actions/workflows/ci.yml"><img src="https://github.com/DanielJamesTronca/apple-liquid-glass-skill/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-4b5563.svg" alt="MIT License"></a>
</p>

Start most Liquid Glass work by removing custom chrome. System bars, search,
sheets, menus, and popovers already adapt when an app builds with the current
SDK. The skill checks whether custom glass belongs before suggesting an API,
then routes the task to the right framework and verification steps.

## Install

For Codex, Claude Code, Cursor, and other Agent Skills clients:

```bash
npx skills add DanielJamesTronca/apple-liquid-glass-skill -g
```

In Codex, ask `$skill-installer` to install `apple-liquid-glass` from this
repository.

For Claude Code's plugin marketplace:

```text
/plugin marketplace add DanielJamesTronca/apple-liquid-glass-skill
/plugin install apple-liquid-glass@apple-liquid-glass-skill
```

Run `/reload-plugins` if Claude Code asks you to activate the plugin.

## What it covers

| If you need to… | The skill will… |
|---|---|
| Adopt Liquid Glass in an existing app | Recompile first, then inspect bars, search, presentations, custom controls, icons, and widgets. |
| Build or review a custom control | Decide whether glass belongs there before selecting the framework API. |
| Upgrade to Xcode 27 beta | Separate OS 26 behaviour from current beta changes and verify availability. |
| Work in SwiftUI, UIKit, or AppKit | Load only the relevant framework reference. |
| Check widgets, icons, accessibility, or performance | Use the focused reference without pulling unrelated guidance into context. |

## The design position

Liquid Glass belongs to the functional layer: navigation, controls, and other
interactive elements above content. Cards, list rows, and decorative content
surfaces usually should not use it. Use system components, concentric shapes,
semantic tint, and accessibility testing. Skip hand-made blur and arbitrary
opacity values.

## Included tooling

The bundled audit scans a Swift project for patterns worth checking. Read each
match in context before changing code.

```bash
python3 skills/apple-liquid-glass/scripts/audit_liquid_glass.py path/to/Sources
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

`tests/skill_evals.json` records positive and negative trigger prompts so
routing changes can be checked without pretending a keyword matcher measures
agent behaviour.

## Sources and scope

The references were checked against Apple API documentation, Human Interface
Guidelines, WWDC sessions, Group Labs, sample code, and release notes on
14 August 2026. They cover the decisions and APIs that recur in real projects.
When a beta declaration affects a change, verify it against the project's Xcode
SDK.

## Contributing

Corrections need an Apple source and the affected OS versions. See
[CONTRIBUTING.md](CONTRIBUTING.md) for source precedence, test commands, and
the prompt-evaluation workflow.

Released under the [MIT License](LICENSE). This project is independent and is
not affiliated with or endorsed by Apple.
