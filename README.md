# d20

A [SynapsCLI](https://github.com/HaseebKhalid1507/SynapsCLI) extension that rolls a
d20 before every user message and puts the roll into the model's context, so the model
can react to it in character.

```
[🎲 d20 this turn: 20/20 — NATURAL 20 — Joestar himself couldn't have planned this. React in-character to the roll.]
```

## How it works

`d20` subscribes to the `before_message` hook (permission `privacy.llm_content`). On
each turn it returns an `inject` action with the roll and a flavor tag:

| roll | tag |
|---|---|
| 1 | natural 1, catastrophic |
| 2–5 | rough roll |
| 6–10 | mid |
| 11–15 | decent |
| 16–19 | solid roll |
| 20 | natural 20 |

Synaps attaches `before_message` injections to the newest user message, after the
cache marker, so a different roll every turn doesn't break the prompt cache.

It speaks JSON-RPC 2.0 over stdio with LSP-style `Content-Length` framing, the
standard SynapsCLI process-extension protocol (v1). It's dependency-free Python 3.

| JSON-RPC method | d20 response |
|---|---|
| `initialize` | `{"protocol_version": 1, "capabilities": {}}` |
| `hook.handle` (`kind: before_message`) | `{"action": "inject", "content": "[🎲 …]"}` |
| `shutdown` | `null` |

## Install

With [synaps-overclocked](https://github.com/HaseebKhalid1507/synaps-overclocked)
(`overclock`), or from `/plugins` after adding that marketplace. To install by hand:

```bash
git clone https://github.com/HaseebKhalid1507/synaps-d20 ~/.synaps-cli/plugins/d20
```

It loads on the next Synaps start. Requires `python3`. Tested against SynapsCLI 0.10.x.

## License

MIT © Haseeb Khalid
