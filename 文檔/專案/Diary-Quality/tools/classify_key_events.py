#!/usr/bin/env python3
"""Subject-form classifier for character-diary `key_events` strings.

Reproduces the five-way classification used in the 2026-09-06 diary audit
(RP記憶/實驗與驗證/Diary_機制與Prompt_Audit_2026-09-06.md §3.2):

  1  name at the start      -- a listed name occurs within the first 6 chars
  2  pronoun at the start   -- first char is a listed pronoun
  3  name mid-sentence      -- a listed name occurs, but not within the first 6 chars
  4  pronoun mid-sentence   -- a listed pronoun occurs, but not at the start
  5  no subject             -- none of the above

Plus one sub-count of class 1:

  1s (strict)  -- the string starts with a listed name immediately followed by
                  a full-width colon (the "主体：事件" contract). Any listed
                  name counts, not only the diary owner.

Calibration fixture (frozen baseline, NOT human ground truth): the first
60 / 13 / 3 entries of 范婼慧 / 蘇芮萱 / 徐婷婷 in 银趴邮轮 Branch #12 hold
248 key_events; the audit classified them as 52 / 5 / 19 / 48 / 124.
This script, with the frozen parameters below, yields 52 / 5 / 18 / 48 / 125:
one item differs from the audit and could not be explained within the closed
name set; the user accepted this residual on 2026-09-13 (option A). The frozen
baseline for later comparisons is therefore 52 / 5 / 18 / 48 / 125.

Usage:
  python classify_key_events.py --chat <path.jsonl> [--subset 范婼慧:60,蘇芮萱:13,徐婷婷:3]
                                [--from 范婼慧:60,...] [--dump]
  python classify_key_events.py --selftest

Windows: run with PYTHONIOENCODING=utf-8.
"""
import argparse
import io
import json
import sys

# ---- frozen parameters (do not edit after the calibration commit) ----------
NAMES = ("范婼慧", "蘇芮萱", "徐婷婷", "小秘書", "宇璽")
PRONOUNS = ("他", "她", "我", "你", "主人")   # 主人 = in-story address for the player
PREFIX_WINDOW = 6          # "前 6 字內有無角色名"
FULLWIDTH_COLON = "："
# ----------------------------------------------------------------------------


def classify(text, names=NAMES, pronouns=PRONOUNS, window=PREFIX_WINDOW):
    """Return (cls, strict) where cls in 1..5 and strict is bool."""
    s = (text or "").strip()
    if not s:
        return 5, False
    strict = any(s.startswith(n + FULLWIDTH_COLON) for n in names)
    name_pos = [s.find(n) for n in names if n in s]
    if name_pos and min(name_pos) < window:
        return 1, strict
    if s[0] in pronouns:
        return 2, False
    if name_pos:
        return 3, False
    if any(p in s for p in pronouns):
        return 4, False
    return 5, False


def load_diaries(path):
    with io.open(path, encoding="utf-8") as f:
        meta = json.loads(f.readline())
    return meta["chat_metadata"]["extensions"]["character-diary"]["diaries"]


def parse_spec(spec):
    out = {}
    if spec:
        for part in spec.split(","):
            name, n = part.split(":")
            out[name.strip()] = int(n)
    return out


def collect(diaries, subset=None, start=None):
    """Yield (owner, entry_index, key_event_string)."""
    for owner, entries in diaries.items():
        lo = (start or {}).get(owner, 0)
        hi = (subset or {}).get(owner, len(entries))
        if subset and owner not in subset:
            continue
        for idx, e in enumerate(entries[lo:hi], start=lo):
            for ke in (e.get("key_events") or []):
                yield owner, idx, ke


def tally(rows):
    counts = {k: 0 for k in (1, 2, 3, 4, 5)}
    strict = 0
    detail = []
    for owner, idx, ke in rows:
        c, st = classify(ke)
        counts[c] += 1
        strict += 1 if st else 0
        detail.append((owner, idx, c, st, ke))
    return counts, strict, detail


def report(counts, strict, total_expected=None):
    total = sum(counts.values())
    labels = {1: "① name at start", 2: "② pronoun at start", 3: "③ name mid",
              4: "④ pronoun mid", 5: "⑤ no subject"}
    for k in (1, 2, 3, 4, 5):
        pct = (100.0 * counts[k] / total) if total else 0.0
        print(f"{labels[k]:<22} {counts[k]:>4}  {pct:5.1f}%")
    spct = (100.0 * strict / total) if total else 0.0
    print(f"{'①-strict (name：)':<22} {strict:>4}  {spct:5.1f}%")
    print(f"{'total':<22} {total:>4}")
    if total_expected is not None:
        ok = total == total_expected
        print(f"reconcile: sum={total} expected={total_expected} -> {'OK' if ok else 'MISMATCH'}")
        return ok
    return True


SELFTEST = [
    # (text, expected class, expected strict)
    ("范婼慧：主动索吻", 1, True),
    ("宇璽：答应下周再来", 1, True),
    ("徐婷婷：告诉范婼慧一个秘密", 1, True),
    ("蘇芮萱：拒绝了邀请", 1, True),
    ("小秘書：挑选舞会服装", 1, True),
    ("范婼慧改回直呼宇璽的名字并挑选舞会服装", 1, False),
    ("他问起水之馆，我暗示那里不单纯", 2, False),
    ("在舞池持续贴身挑逗宇璽", 3, False),
    ("带他逛主题区，介绍水之馆", 4, False),
    ("高潮后主动索吻", 5, False),
]


def selftest():
    bad = 0
    for text, exp_c, exp_s in SELFTEST:
        c, st = classify(text)
        flag = "ok " if (c, st) == (exp_c, exp_s) else "BAD"
        bad += flag == "BAD"
        print(f"{flag} cls={c} strict={st!s:<5} expected=({exp_c},{exp_s}) {text}")
    print("selftest:", "PASS" if not bad else f"FAIL ({bad})")
    return bad == 0


def main():
    reconf = getattr(sys.stdout, "reconfigure", None)
    if reconf:
        reconf(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--chat", help="path to a SillyTavern chat .jsonl")
    ap.add_argument("--subset", help="owner:N,... take the first N entries per owner")
    ap.add_argument("--from", dest="start", help="owner:IDX,... take entries from index IDX on")
    ap.add_argument("--expect-total", type=int, help="reconcile the total against this number")
    ap.add_argument("--dump", action="store_true", help="print every key_event with its class")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if not a.chat:
        ap.error("--chat or --selftest required")

    diaries = load_diaries(a.chat)
    rows = list(collect(diaries, parse_spec(a.subset), parse_spec(a.start)))
    counts, strict, detail = tally(rows)
    if a.dump:
        for owner, idx, c, st, ke in detail:
            print(f"[{c}{'s' if st else ' '}] {owner}#{idx} {ke}")
    ok = report(counts, strict, a.expect_total)
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
