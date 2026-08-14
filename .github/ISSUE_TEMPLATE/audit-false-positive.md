---
name: Audit false positive
about: audit_liquid_glass.py flagged correct code
title: "[audit] false positive: "
labels: audit
---

A false positive on correct code costs more trust than a missed lead, so these are treated as
bugs in the audit.

## Which check

The check id from the output, e.g. `glass-in-list-row`.

## The code it flagged

```swift
// paste enough surrounding context to show why it's correct
```

## Why it's correct

Which layer does the element live in, and what is behind it at runtime?

## Output

```
paste the audit output line, including the confidence level
```

## Deployment target

Relevant when the finding concerns availability branches or fallbacks.
