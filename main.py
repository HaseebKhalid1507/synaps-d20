#!/usr/bin/env python3
"""
d20 extension — rolls a die before every user message and injects the result.

Subscribes to `before_message` and returns an `inject` action with the roll
plus a flavor tag. Model sees the roll before responding so it can react.

Speaks JSON-RPC 2.0 over stdio with LSP-style Content-Length framing.
"""

import json
import random
import sys


def read_message():
    """Read a Content-Length framed JSON-RPC message from stdin."""
    length = None
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        line = line.decode("utf-8").strip()
        if not line:
            if length is None:
                continue
            break
        name, _, value = line.partition(":")
        if name.strip().lower() == "content-length":
            length = int(value.strip())
    return json.loads(sys.stdin.buffer.read(length))


def write_message(msg):
    """Write a Content-Length framed JSON-RPC message to stdout."""
    body = json.dumps(msg).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8"))
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def flavor(roll: int) -> str:
    """Return a tasting note for the roll."""
    if roll == 1:
        return "NATURAL 1 — catastrophic. Brace for impact."
    if roll == 20:
        return "NATURAL 20 — Joestar himself couldn't have planned this."
    if roll <= 5:
        return "rough roll"
    if roll <= 10:
        return "mid"
    if roll <= 15:
        return "decent"
    return "solid roll"


def handle_hook(params):
    """Handle a hook.handle call."""
    if params.get("kind") == "before_message":
        roll = random.randint(1, 20)
        tag = flavor(roll).rstrip(".")
        return {
            "action": "inject",
            "content": f"[\U0001f3b2 d20 this turn: {roll}/20 — {tag}. "
                       f"React in-character to the roll.]",
        }
    return {"action": "continue"}


def main():
    sys.stderr.write("[d20] rolling bones\n")
    sys.stderr.flush()

    while True:
        try:
            req = read_message()
            if req is None:
                break

            method = req.get("method", "")
            if "id" not in req:  # notification: never answered
                continue
            rid = req["id"]

            if method == "initialize":
                reply = {"result": {"protocol_version": 1, "capabilities": {}}}
            elif method == "hook.handle":
                reply = {"result": handle_hook(req.get("params") or {})}
            elif method == "shutdown":
                write_message({"jsonrpc": "2.0", "result": None, "id": rid})
                sys.stderr.write("[d20] bones away\n")
                sys.stderr.flush()
                break
            else:
                reply = {"error": {"code": -32601, "message": f"method not found: {method}"}}

            write_message({"jsonrpc": "2.0", "id": rid, **reply})

        except Exception as e:
            sys.stderr.write(f"[d20] error: {e}\n")
            sys.stderr.flush()
            break


if __name__ == "__main__":
    main()
