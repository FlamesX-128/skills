---
name: blind-subagents
description: |
    Audit work using blind subagents. Use this skill to review interfaces, technical solutions, and design decisions, identify issues, and highlight opportunities for improvement.
---

# Blind Subagents

Blind subagents start each run with **zero prior context**.

They may only use:

- the question they receive;
- context explicitly included in the request;
- images or data attached to that request;
- tools authorized for that run, such as Playwright, within the limits described below.

They cannot independently read code, browse repositories, access history, previous conversations, or other agents' responses.

## Types

### Consultation

Receives a question and the minimum context needed to answer it.

Examples:

- How would you implement this?
- How would you model this data?
- What risks do you see?
- What edge cases would you consider?

### Visual

Receives an image or an interface accessible through Playwright and responds only based on what it observes.

Examples:

- What does this screen do?
- What is the primary action?
- What is unclear?
- What appears broken?

## Rule

Give the subagent **the problem, not the existing solution**.

Instead of:

> I'm using Redis to prevent two workers from processing the same resource. Is that okay?

Use:

> Two workers may process the same resource at the same time. Only one should be allowed to do so. How would you solve this?
