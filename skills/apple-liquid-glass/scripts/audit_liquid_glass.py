#!/usr/bin/env python3
"""
Liquid Glass audit — reports LEADS, not verdicts.

Every finding means "a human or agent should read this line in context",
never "this is broken, rewrite it". Glass correctness depends on which layer
an element lives in, the deployment target, and what is behind the view at
runtime — none of which a regex can see.

Usage:
    python3 audit_liquid_glass.py <path> [--json] [--min-confidence low|medium|high]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict

SWIFT_EXT = ".swift"
CONF_ORDER = {"low": 0, "medium": 1, "high": 2}


@dataclass
class Check:
    id: str
    pattern: str
    message: str
    inspect: str
    confidence: str = "medium"
    # optional: only fire if this other pattern is absent in the file
    absent_in_file: str | None = None
    # optional: only fire if this pattern is present in the file
    present_in_file: str | None = None
    # optional: only fire if a PRECEDING line (within window) matches.
    # Backward-only by design: a modifier attaches to what comes before it,
    # so looking forward produces false positives from unrelated later code.
    near: str | None = None
    near_window: int = 4
    flags: int = 0
    _rx: re.Pattern = field(init=False, repr=False, default=None)

    def compile(self):
        self._rx = re.compile(self.pattern, self.flags)
        return self


CHECKS = [
    Check(
        id="glass-on-button",
        pattern=r"\.glassEffect\s*\(",
        near=r"\bButton\s*[\({]|\bButton\(",
        near_window=6,
        confidence="high",
        message="`.glassEffect()` appears near a Button.",
        inspect="If the glass is applied TO the button, replace with "
                "`.buttonStyle(.glass)` or `.glassProminent` plus "
                "`.buttonBorderShape(_:)`. Raw glassEffect yields a button "
                "sitting ON glass. If the glass belongs to a container that "
                "merely holds a button, this is fine.",
    ),
    Check(
        id="glass-in-toolbar",
        # NOTE: deliberately excludes `.glassProminent` — HIG recommends the
        # prominent style for a toolbar's single key action (Done/Submit).
        pattern=r"\.glassEffect\s*\(|\.buttonStyle\(\s*\.glass\s*\)",
        near=r"\.toolbar\s*[\({]|ToolbarItem|ToolbarItemGroup",
        near_window=8,
        confidence="high",
        message="Redundant glass styling inside a toolbar block.",
        inspect="Toolbar and navigation-bar items already receive the correct "
                "glass automatically. Adding it usually doubles the material. "
                "`.glassProminent` is the exception — HIG recommends it for a "
                "single key action such as Done or Submit.",
    ),
    Check(
        id="glass-in-list-row",
        pattern=r"\.glassEffect\s*\(",
        near=r"\bForEach\b|\bLazyVStack\b|\bLazyHStack\b|\bLazyVGrid\b|\bList\b",
        near_window=6,
        confidence="high",
        message="Glass inside a repeating/scrolling construct.",
        inspect="List rows and grid cells are CONTENT layer — HIG: 'Don't use "
                "Liquid Glass in the content layer.' This is also O(rows) "
                "sampling surfaces. Confirm the element is genuinely floating "
                "functional UI, not a card.",
    ),
    Check(
        id="nested-container",
        pattern=r"GlassEffectContainer",
        present_in_file=r"GlassEffectContainer[\s\S]*GlassEffectContainer",
        confidence="low",
        message="More than one GlassEffectContainer in this file.",
        inspect="Multiple containers are legitimate when groups are far apart "
                "or unrelated. NESTED containers are not — they double-sample. "
                "Check the brace nesting by eye.",
    ),
    Check(
        id="glass-without-container",
        pattern=r"\.glassEffect\s*\(",
        absent_in_file=r"GlassEffectContainer",
        confidence="low",
        message="glassEffect used with no GlassEffectContainer in this file.",
        inspect="Only a problem if several glass elements sit near each other "
                "and should share sampling, blend, or morph. A single isolated "
                "glass element needs no container.",
    ),
    Check(
        id="glass-effect-id-no-namespace",
        pattern=r"\.glassEffectID\s*\(",
        absent_in_file=r"@Namespace",
        confidence="high",
        message="`glassEffectID` used but no `@Namespace` declared in this file.",
        inspect="Morphing requires a shared Namespace.ID, matching IDs, an "
                "enclosing GlassEffectContainer, and an ANIMATED state change. "
                "Check the namespace isn't passed in from elsewhere before acting.",
    ),
    Check(
        id="glass-effect-id-no-animation",
        pattern=r"\.glassEffectID\s*\(",
        absent_in_file=r"withAnimation|\.animation\s*\(",
        confidence="medium",
        message="`glassEffectID` present with no animation in this file.",
        inspect="Without an animated state change the morph never renders. "
                "Verify the transition is driven from another file before editing.",
    ),
    Check(
        id="interactive-glass",
        pattern=r"\.interactive\s*\(\s*(true)?\s*\)|isInteractive\s*=\s*true",
        confidence="low",
        message="Interactive glass enabled.",
        inspect="Only correct if the element actually responds to touch/click. "
                "On static chrome or a badge it is wrong. AppKit guidance: "
                "'A little goes a long way!'",
    ),
    Check(
        id="clear-without-dimming",
        pattern=r"\.glassEffect\s*\(\s*\.clear|Glass\s*\.\s*clear|UIGlassEffect\(\s*style:\s*\.clear",
        confidence="high",
        message="Clear glass variant in use.",
        inspect="Clear requires ALL of: floats over visually rich media, media "
                "must stay prominent, AND a dimming layer beneath (~35% black "
                "when content is bright; none needed if content is dark or "
                "AVKit supplies its own). Confirm the dimming layer exists.",
    ),
    Check(
        id="tint-usage",
        pattern=r"\.tint\s*\(|tintColor\s*=",
        near=r"\.glassEffect|GlassEffect|buttonStyle\(\s*\.glass",
        near_window=6,
        confidence="low",
        message="Tint applied to glass.",
        inspect="Tint should express state or mark ONE primary action, applied "
                "to the background rather than the symbol. HIG: 'refrain from "
                "adding color to the background of multiple controls.' Count "
                "how many tinted glass controls are on screen together.",
    ),
    Check(
        id="hardcoded-foreground-on-glass",
        pattern=r"\.foregroundColor\s*\(\s*\.(white|black)\s*\)|\.foregroundStyle\s*\(\s*\.(white|black)\s*\)",
        near=r"\.glassEffect|buttonStyle\(\s*\.glass",
        near_window=6,
        confidence="high",
        message="Hard-coded white/black foreground near glass.",
        inspect="Glass adapts symbol/text colour to the content behind it "
                "(dark over light content, light over dark). Hard-coding opts "
                "out and will become illegible. Use system colours.",
    ),
    Check(
        id="custom-bar-background",
        pattern=r"\.toolbarBackground\s*\(|UITabBar\.appearance\(\)|UINavigationBar\.appearance\(\)|barTintColor\s*=|setBackgroundImage",
        confidence="medium",
        message="Custom bar background/appearance override.",
        inspect="HIG: 'Reduce the use of toolbar backgrounds and tinted "
                "controls … might overlay or interfere with background effects "
                "that the system provides.' Prefer colouring the content layer "
                "and using a ScrollEdgeEffectStyle. Often safe to delete.",
    ),
    Check(
        id="presentation-background",
        pattern=r"\.presentationBackground\s*\(",
        confidence="medium",
        message="`presentationBackground` override on a presentation.",
        inspect="Sheets adopt Liquid Glass automatically. This override "
                "commonly predates OS 26 and is the usual cause of 'my sheet "
                "looks wrong after upgrading'. Check when it was added.",
    ),
    Check(
        id="custom-blur-imitation",
        pattern=r"\.ultraThinMaterial|\.thinMaterial|UIBlurEffect\s*\(|NSVisualEffectView\s*\(",
        confidence="low",
        message="Standard material / blur in use.",
        inspect="Legitimate in the CONTENT layer, and as a pre-26 fallback. A "
                "defect when it imitates glass on OS 26+. Check the deployment "
                "target and which layer this sits in.",
    ),
    Check(
        id="magic-opacity",
        pattern=r"\.opacity\s*\(\s*0?\.\d+\s*\)",
        near=r"\.glassEffect|GlassEffect|buttonStyle\(\s*\.glass|\.ultraThinMaterial",
        near_window=5,
        confidence="medium",
        message="Hard-coded opacity next to glass/material.",
        inspect="There are no public constants matching system glass, and the "
                "OS 27 beta Liquid Glass slider makes any fixed guess wrong. A "
                "deliberate dimming layer (e.g. 0.35 black under clear glass) "
                "is correct — distinguish the two.",
    ),
    Check(
        id="scroll-edge-override",
        pattern=r"scrollEdgeEffectStyle\s*=|\.scrollEdgeEffectStyle\s*\(",
        confidence="high",
        message="Scroll edge effect style overridden.",
        inspect="OS 27 beta changed `.automatic`: it no longer switches between soft "
                "and hard but provides its own visuals. Apple explicitly says "
                "to re-evaluate overrides, 'especially when set to .soft, as "
                "that no longer matches the default system appearance.'",
    ),
    Check(
        id="glass-button-no-label",
        pattern=r"\.buttonStyle\s*\(\s*\.glass(Prominent)?\s*\)",
        near=r"Image\s*\(\s*systemName:",
        near_window=5,
        absent_in_file=r"accessibilityLabel",
        confidence="medium",
        message="Icon-only glass button with no accessibilityLabel in this file.",
        inspect="Icon-only glass buttons are the most common accessibility "
                "gap. Confirm a label exists (it may come from the Label view "
                "or a shared component).",
    ),
    Check(
        id="motion-without-reduce-motion",
        pattern=r"\.glassEffectTransition\s*\(|withAnimation\s*\(",
        present_in_file=r"\.glassEffect",
        absent_in_file=r"accessibilityReduceMotion|reduceMotion",
        confidence="low",
        message="Glass animation with no Reduce Motion handling in this file.",
        inspect="System components handle Reduce Motion themselves. Custom "
                "glass transitions need an explicit reduced path.",
    ),
    Check(
        id="availability-branch",
        pattern=r"#available\s*\(\s*iOS\s*26|#available\s*\(\s*macOS\s*26",
        confidence="low",
        message="Availability branch for OS 26 glass.",
        inspect="Required ONLY if the deployment target is below 26. If the "
                "target is 26+, this is dead code and should be deleted. See "
                "the deployment target reported in the audit header.",
    ),
]

TEST_CHECKS = [
    Check(
        id="snapshot-only-glass",
        pattern=r"assertSnapshot|verifySnapshot|__Snapshots__|snapshot\(",
        present_in_file=r"[Gg]lass",
        confidence="medium",
        message="Snapshot assertions in a file that references glass.",
        inspect="Glass samples its backdrop; in isolation there is often "
                "nothing to sample, so tinted glass can render black. That is "
                "expected, not a view bug — never fix it by baking a "
                "background into the production view. Snapshot-only validation "
                "does not prove glass is correct.",
    ),
]


def find_deployment_targets(root: str) -> dict[str, str]:
    targets: dict[str, str] = {}
    rx = re.compile(r"(IPHONEOS|MACOSX|WATCHOS|TVOS|XROS)_DEPLOYMENT_TARGET = ([0-9.]+)")
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "build", "DerivedData", ".build"}]
        for fn in filenames:
            if fn == "project.pbxproj" or fn.endswith(".xcconfig"):
                try:
                    with open(os.path.join(dirpath, fn), "r", encoding="utf-8", errors="ignore") as fh:
                        for m in rx.finditer(fh.read()):
                            targets[m.group(1)] = m.group(2)
                except OSError:
                    pass
    return targets


def swift_files(root: str):
    if os.path.isfile(root) and root.endswith(SWIFT_EXT):
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", "build", "DerivedData", ".build", "Pods", "Carthage"}]
        for fn in filenames:
            if fn.endswith(SWIFT_EXT):
                yield os.path.join(dirpath, fn)


def is_test_file(path: str) -> bool:
    base = os.path.basename(path)
    return "Test" in base or "Spec" in base or "/Tests" in path


def scan_file(path: str, checks) -> list[dict]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
    except OSError:
        return []
    lines = text.splitlines()
    out = []
    for chk in checks:
        if chk.absent_in_file and re.search(chk.absent_in_file, text):
            continue
        if chk.present_in_file and not re.search(chk.present_in_file, text):
            continue
        near_rx = re.compile(chk.near) if chk.near else None
        for i, line in enumerate(lines):
            if line.lstrip().startswith("//"):
                continue
            if not chk._rx.search(line):
                continue
            if near_rx:
                lo = max(0, i - chk.near_window)
                if not any(near_rx.search(lines[j]) for j in range(lo, i)):
                    continue
            out.append({
                "file": path,
                "line": i + 1,
                "check": chk.id,
                "confidence": chk.confidence,
                "code": line.strip()[:160],
                "lead": chk.message,
                "inspect": chk.inspect,
            })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--min-confidence", choices=["low", "medium", "high"], default="low")
    args = ap.parse_args()

    for c in CHECKS + TEST_CHECKS:
        c.compile()

    findings = []
    n_files = 0
    for f in swift_files(args.path):
        n_files += 1
        findings.extend(scan_file(f, TEST_CHECKS if is_test_file(f) else CHECKS))

    floor = CONF_ORDER[args.min_confidence]
    findings = [f for f in findings if CONF_ORDER[f["confidence"]] >= floor]
    findings.sort(key=lambda f: (-CONF_ORDER[f["confidence"]], f["file"], f["line"]))

    targets = find_deployment_targets(args.path if os.path.isdir(args.path) else ".")

    if args.json:
        print(json.dumps({"deployment_targets": targets,
                          "files_scanned": n_files,
                          "findings": findings}, indent=2))
        return 0

    print(f"Liquid Glass audit — {n_files} Swift file(s) scanned")
    if targets:
        print("Deployment targets: " + ", ".join(f"{k}={v}" for k, v in sorted(targets.items())))
        low = [v for v in targets.values() if float(v.split(".")[0]) < 26]
        print("  → Availability fallbacks ARE required (target below 26)." if low
              else "  → Target is 26+; `if #available(iOS 26…)` branches are dead code.")
    else:
        print("Deployment targets: not found — determine before advising on fallbacks.")

    if not findings:
        print("\nNo leads found. This is not proof the glass is correct — "
              "verify visually per SKILL.md §5.")
        return 0

    print(f"\n{len(findings)} lead(s). These require INSPECTION, not automatic rewriting.\n")
    current = None
    for f in findings:
        if f["file"] != current:
            current = f["file"]
            print(f"\n{current}")
        print(f"  {f['line']:>5}  [{f['confidence']:<6}] {f['check']}: {f['lead']}")
        print(f"         {f['code']}")
        print(f"         → {f['inspect']}")

    print("\nReminder: a flagged line may be correct in context. Read the "
          "surrounding code, the layer the element lives in, and the "
          "deployment target before changing anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
