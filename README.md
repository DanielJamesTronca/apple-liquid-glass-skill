# Apple Liquid Glass

An [Agent Skill](https://agentskills.io) for designing, implementing, reviewing, and migrating Liquid Glass UI on Apple platforms. It covers SwiftUI, UIKit, AppKit, widgets, and app icons across OS 26 and the current OS 27 betas.

The first question is whether an element should be glass at all. Cards, list rows, and other content surfaces usually should not. System bars, search fields, sheets, menus, and popovers already adopt Liquid Glass when you build with the current SDK. The skill checks those cases before it writes custom glass code.

## Install

For Codex, Claude Code, Cursor, and other Agent Skills clients:

```bash
npx skills add DanielJamesTronca/apple-liquid-glass-skill -g
```

In Codex, you can instead ask `$skill-installer` to install `apple-liquid-glass` from this repository.

For Claude Code's plugin marketplace:

```text
/plugin marketplace add DanielJamesTronca/apple-liquid-glass-skill
/plugin install apple-liquid-glass@apple-liquid-glass-skill
```

Run `/reload-plugins` if Claude Code asks you to activate the plugin.

## What it handles

| Ask | Result |
|---|---|
| "Adopt Liquid Glass in this app" | Recompile first, then inspect bars, search, presentations, custom controls, icons, and widgets in that order. |
| "Make this floating control glass" | Decide whether glass belongs there, then use the documented API for the project's framework and deployment target. |
| "Review my Liquid Glass code" | Run the conservative audit and inspect each lead in context. |
| "I upgraded to Xcode 27 beta" | Check the OS 26 to OS 27 beta changes, especially scroll-edge behavior and availability. |
| "Should this be glass?" | Give a direct answer and a concrete alternative when the answer is no. |

The skill keeps SwiftUI as the default path and loads UIKit, AppKit, widget, icon, accessibility, testing, or migration guidance only when the task needs it.

## Sources and versions

The guidance is grounded in Apple API documentation, the Human Interface Guidelines, WWDC sessions and Group Labs, sample code, and release notes. Each reference file cites the Apple material behind its rules.

OS 27 APIs are currently beta. The skill keeps OS 26 guidance beside the beta material and routes by SDK, platform, and deployment target. Verify beta declarations against the documentation bundled with the Xcode version in use.

## Included checks

```bash
# Report leads for inspection. This script never rewrites code.
python3 skills/apple-liquid-glass/scripts/audit_liquid_glass.py path/to/Sources

# Run the repository tests.
python3 tests/test_audit.py
```

The audit reports leads because a regex cannot see the UI layer, runtime backdrop, or design intent. A flagged line can be correct. Read its surrounding code before changing it.

## Repository layout

```text
skills/apple-liquid-glass/
├── SKILL.md                 # routing, decision rules, implementation constraints
├── agents/openai.yaml       # Codex and ChatGPT display metadata
├── references/              # framework and task guidance, loaded on demand
└── scripts/
    └── audit_liquid_glass.py # conservative Swift source review
```

The repository also includes manifests for Codex/ChatGPT plugins and the Claude Code marketplace. Both point to the same skill folder.

## Contributing

Corrections need an Apple source and the affected OS versions. See [CONTRIBUTING.md](CONTRIBUTING.md) for the source order and test commands.

## License

[MIT](LICENSE). Apple, Liquid Glass, and the cited Apple documentation remain the property of Apple Inc. This project is independent and is not endorsed by Apple.
