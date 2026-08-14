---
name: Rule correction
about: A rule in this skill contradicts current Apple guidance
title: "[correction] "
labels: correction
---

## Which rule

File and section, e.g. `references/swiftui.md` § Buttons.

## What it currently says

Quote the rule as written.

## What it should say

## Apple source

**Required.** A rule only changes when a source outranks the one it currently cites.
Use the precedence order in CONTRIBUTING.md — API documentation beats the HIG, which beats WWDC
sessions.

- URL:
- If an API: paste the `metadata.platforms` availability from the documentation JSON:
  ```
  curl -s "https://developer.apple.com/tutorials/data/documentation/<path>.json"
  ```
- If a WWDC session: session number and timestamp.

## OS versions affected

Does this change OS 26 behavior, OS 27, or both? OS 27 guidance must not erase OS 26 behavior —
both are retained and routed by deployment target.
