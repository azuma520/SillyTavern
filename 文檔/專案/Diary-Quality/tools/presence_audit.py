#!/usr/bin/env python3
"""presence_audit.py -- frozen instrument for the diary-presence-gate acceptance.

Reads SillyTavern chat files (first line = chat metadata) produced by the
character-diary extension and scores one scenario against the frozen
expectation table (presence_expect.json).

Two independent signals are read per run (one child branch = one run):
  * diaries           -> did an entry for the role land at message_id == range_top?
                         (this is the ground truth of "wrote into the store")
  * presenceAudit     -> what presence label did the model give, and what did
                         the gate decide (written / reason)?

Errors are split into two kinds and never merged (design D11):
  * model_error : the label the model gave contradicts the expectation
                  (wrote because it said participated/witnessed for an absent
                  role, or refused a present role by labelling it absent/etc.)
  * gate_error  : the label was right but the program did the wrong thing
                  (blocked label yet a diary landed; passing label yet nothing
                  landed and no benign reason).

Modes
  --selftest                       run the built-in fixture, exit 1 on mismatch
  --baseline                       old-code mode: no presenceAudit, only count
                                   diaries that landed (validity check)
  --parent F --run F [--run F ...] mother branch + child branches
  --scenario S1|S2|S3|S4
  --expect PATH                    defaults to presence_expect.json beside this file
  --json                           machine-readable report on stdout

Frozen: after the calibration commit this file must not change (CLAUDE.md
Instrument rule). Defects found later are recorded, not fixed here.
"""
import argparse
import hashlib
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_EXPECT = os.path.join(HERE, "presence_expect.json")
STORE_PATH = ("chat_metadata", "extensions", "character-diary")


# --------------------------------------------------------------------------- io

def load_store(path):
    """Return (store_dict, sha1_of_file) for a chat jsonl file."""
    with open(path, "rb") as fh:
        raw = fh.read()
    first = raw.split(b"\n", 1)[0]
    meta = json.loads(first.decode("utf-8"))
    node = meta
    for key in STORE_PATH:
        node = node.get(key) or {}
    return node, hashlib.sha1(raw).hexdigest()


def load_expect(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ extraction

def entries_at(store, role, top):
    lst = (store.get("diaries") or {}).get(role) or []
    return [e for e in lst if e and e.get("message_id") == top]


def audit_at(store, role, top):
    recs = store.get("presenceAudit") or []
    out = []
    for r in recs:
        if not isinstance(r, dict) or r.get("message_id") != top:
            continue
        if r.get("main") == role or r.get("name") == role:
            out.append(r)
    return out


def norm_presence(v):
    if v is None:
        return None
    return str(v).strip().lower()


# ----------------------------------------------------------------- scoring

def score_run(parent, child, scenario_expect, cfg, baseline=False):
    """Score one run. Returns dict role -> cell result."""
    top = cfg["range_top"]
    pass_values = set(cfg["pass_values"])
    valid_values = set(cfg["presence_values"])
    result = {}
    for role, exp in scenario_expect.items():
        new_entries = len(entries_at(child, role, top)) - len(entries_at(parent, role, top))
        written = new_entries > 0
        cell = {
            "situation": exp["situation"],
            "expected_presence": exp["presence"],
            "expected_write": exp["write"],
            "written": written,
            "new_entries": new_entries,
            "labels": [],
            "reasons": [],
            "audit_written": [],
            "label_status": "n/a",
            "outcome": "ok",
            "error_kind": None,
        }
        if baseline:
            cell["outcome"] = "ok" if written == exp["write"] else "mismatch"
            result[role] = cell
            continue

        recs = audit_at(child, role, top)
        parent_recs = audit_at(parent, role, top)
        recs = recs[len(parent_recs):] if len(parent_recs) else recs
        labels = [norm_presence(r.get("presence")) for r in recs]
        cell["labels"] = labels
        cell["reasons"] = [r.get("reason") for r in recs]
        cell["audit_written"] = [bool(r.get("written")) for r in recs]

        # label status (report only, never a threshold)
        if not labels:
            cell["label_status"] = "no_record"
        else:
            ok_set = {exp["presence"]} | set(exp.get("label_deviation_ok") or [])
            if labels[-1] == exp["presence"]:
                cell["label_status"] = "match"
            elif labels[-1] in ok_set:
                cell["label_status"] = "deviation_ok"
            elif labels[-1] in valid_values:
                cell["label_status"] = "mismatch"
            else:
                cell["label_status"] = "invalid"

        model_said_pass = any(l in pass_values for l in labels)

        if not exp["write"]:
            if written:
                cell["outcome"] = "wrong_write"
                cell["error_kind"] = "model_error" if model_said_pass else "gate_error"
        else:
            if not written:
                cell["outcome"] = "missed_write"
                cell["error_kind"] = "gate_error" if model_said_pass else "model_error"
        result[role] = cell
    return result


def consistency_checks(child, scenario_expect, cfg):
    """Standard 5 (audit <-> diaries agree) and 5b (cap)."""
    top = cfg["range_top"]
    issues = []
    for role in scenario_expect:
        n_entries = len(entries_at(child, role, top))
        n_audit_written = sum(1 for r in audit_at(child, role, top) if r.get("written"))
        if n_entries != n_audit_written:
            issues.append(f"{role}: diaries@{top}={n_entries} but audit written={n_audit_written}")
    cap = cfg["thresholds"]["5b_audit_cap"]
    n_audit = len(child.get("presenceAudit") or [])
    if n_audit > cap:
        issues.append(f"presenceAudit length {n_audit} > cap {cap}")
    return issues


def aggregate(run_results, cfg, baseline=False):
    thr = cfg["thresholds"]
    sit_written = {s: 0 for s in "ABCDE"}
    sit_opps = {s: 0 for s in "ABCDE"}
    model_errors = []
    gate_errors = []
    label_counts = {}
    for run_name, cells in run_results:
        for role, c in cells.items():
            s = c["situation"]
            sit_opps[s] += 1
            if c["written"]:
                sit_written[s] += 1
            if not baseline:
                label_counts[c["label_status"]] = label_counts.get(c["label_status"], 0) + 1
                if c["error_kind"] == "model_error":
                    model_errors.append((run_name, role, c["outcome"], c["labels"]))
                elif c["error_kind"] == "gate_error":
                    gate_errors.append((run_name, role, c["outcome"], c["labels"], c["reasons"]))
    agg = {
        "runs": len(run_results),
        "written_by_situation": sit_written,
        "opportunities_by_situation": sit_opps,
        "model_errors": model_errors,
        "gate_errors": gate_errors,
        "label_status_counts": label_counts,
    }
    if baseline:
        agg["baseline_absent_written"] = sit_written["C"] + sit_written["D"] + sit_written["E"]
        agg["baseline_valid"] = agg["baseline_absent_written"] >= 1
        return agg
    agg["standards"] = {
        "1a": {"value": sit_written["C"], "threshold": thr["1a_mentioned_only_written"],
               "pass": sit_written["C"] <= thr["1a_mentioned_only_written"]},
        "1b": {"value": sit_written["D"], "threshold": thr["1b_absent_written"],
               "pass": sit_written["D"] <= thr["1b_absent_written"]},
        "1c": {"value": sit_written["E"], "threshold": thr["1c_uncertain_written"],
               "pass": sit_written["E"] <= thr["1c_uncertain_written"]},
        "2": {"value": sit_written["A"], "opportunities": sit_opps["A"],
              "threshold": thr["2_participated_written_min"],
              "pass": sit_written["A"] >= thr["2_participated_written_min"]},
        "2b": {"value": sit_written["B"], "opportunities": sit_opps["B"],
               "threshold": thr["2b_witnessed_written_min"],
               "pass": sit_written["B"] >= thr["2b_witnessed_written_min"]},
    }
    return agg


# ----------------------------------------------------------------- reporting

def print_report(scenario, agg, run_results, issues_by_run, baseline):
    print(f"== presence_audit :: scenario {scenario} :: {'BASELINE (old code)' if baseline else 'FORMAL'} :: runs={agg['runs']}")
    for run_name, cells in run_results:
        print(f"-- {run_name}")
        for role, c in cells.items():
            if baseline:
                print(f"   {role:<4} [{c['situation']}] written={int(c['written'])} (expected {int(c['expected_write'])}) -> {c['outcome']}")
            else:
                print(f"   {role:<4} [{c['situation']}] labels={c['labels']} reasons={c['reasons']} written={int(c['written'])} "
                      f"(expected {c['expected_presence']}/{int(c['expected_write'])}) label={c['label_status']} -> {c['outcome']}"
                      + (f" [{c['error_kind']}]" if c['error_kind'] else ""))
        for iss in issues_by_run.get(run_name, []):
            print(f"   !! consistency: {iss}")
    print("-- totals")
    print(f"   written by situation: {agg['written_by_situation']}  (opportunities {agg['opportunities_by_situation']})")
    if baseline:
        print(f"   absent-role diaries written (C+D+E): {agg['baseline_absent_written']} -> scenario {'VALID' if agg['baseline_valid'] else 'INVALID (rewrite scene)'}")
        return
    for k, v in agg["standards"].items():
        opp = f"/{v['opportunities']}" if "opportunities" in v else ""
        print(f"   std {k}: {v['value']}{opp} (threshold {v['threshold']}) -> {'PASS' if v['pass'] else 'FAIL'}")
    print(f"   model_errors: {len(agg['model_errors'])}  gate_errors: {len(agg['gate_errors'])}   (kept separate, never summed)")
    for e in agg["model_errors"]:
        print(f"      model  {e}")
    for e in agg["gate_errors"]:
        print(f"      gate   {e}")
    print(f"   label status: {agg['label_status_counts']}")


# ----------------------------------------------------------------- selftest

def _store(diaries=None, audit=None):
    return {"diaries": diaries or {}, "presenceAudit": audit or []}


def _entry(top):
    return {"turn": top, "date": "", "entry": "x", "mood": "平静", "attitude_to_user": "", "secret": "",
            "key_events": [], "relationship_with_others": {}, "message_id": top}


def _rec(top, role, presence, written, reason):
    return {"message_id": top, "name": role, "main": role, "presence": presence, "written": written,
            "reason": reason, "ts": 0}


def selftest(cfg):
    top = cfg["range_top"]
    S1 = cfg["scenarios"]["S1"]
    parent = _store({"范婼慧": [_entry(1000)], "蘇芮萱": [], "徐婷婷": [_entry(1300)]}, [])
    F, S, X = "范婼慧", "蘇芮萱", "徐婷婷"

    def child(diaries_new, audit):
        d = {F: [_entry(1000)], S: [], X: [_entry(1300)]}
        for role in diaries_new:
            d[role] = d[role] + [_entry(top)]
        return _store(d, audit)

    runs = [
        ("run1", child([F, S], [_rec(top, F, "participated", True, "ok"),
                                _rec(top, S, "witnessed", True, "ok"),
                                _rec(top, X, "absent", False, "presence_blocked")])),
        ("run2", child([F], [_rec(top, F, "participated", True, "ok"),
                             _rec(top, S, "absent", False, "presence_blocked"),
                             _rec(top, X, "absent", False, "presence_blocked")])),
        ("run3", child([F, S, X], [_rec(top, F, "participated", True, "ok"),
                                   _rec(top, S, "witnessed", True, "ok"),
                                   _rec(top, X, "participated", True, "ok")])),
        ("run4", child([F, S, X], [_rec(top, F, "participated", True, "ok"),
                                   _rec(top, S, "witnessed", True, "ok"),
                                   _rec(top, X, "absent", True, "presence_blocked")])),
        ("run5", child([], [_rec(top, F, None, False, "invalid_presence"),
                            _rec(top, S, "witnessed", False, "ok"),
                            _rec(top, X, "mentioned_only", False, "presence_blocked")])),
    ]
    results = [(n, score_run(parent, c, S1, cfg)) for n, c in runs]
    agg = aggregate(results, cfg)
    issues = {n: consistency_checks(c, S1, cfg) for n, c in runs}

    expect = {
        "A_written": 4, "B_written": 3, "D_written": 2,
        "model_errors": 3,   # run3 X wrong_write, run2 S missed, run5 F missed(invalid)
        "gate_errors": 2,    # run4 X wrong_write, run5 S missed
        "std_2_pass": False,  # 4 < 16 on 5 runs (threshold is for 20 opps) -> FAIL expected
        "std_2b_pass": True,  # 3 >= 3
        "std_1b_pass": False,  # D written 2 > 0
        "std_1a_pass": True, "std_1c_pass": True,
        # run2 S absent vs witnessed; run3 X participated vs absent; run5 X mentioned_only vs absent
        # (S1 has no label_deviation_ok, so all three are plain mismatches)
        "label_mismatch": 3,
        "label_invalid": 1,   # run5 F None
    }
    got = {
        "A_written": agg["written_by_situation"]["A"],
        "B_written": agg["written_by_situation"]["B"],
        "D_written": agg["written_by_situation"]["D"],
        "model_errors": len(agg["model_errors"]),
        "gate_errors": len(agg["gate_errors"]),
        "std_2_pass": agg["standards"]["2"]["pass"],
        "std_2b_pass": agg["standards"]["2b"]["pass"],
        "std_1b_pass": agg["standards"]["1b"]["pass"],
        "std_1a_pass": agg["standards"]["1a"]["pass"],
        "std_1c_pass": agg["standards"]["1c"]["pass"],
        "label_mismatch": agg["label_status_counts"].get("mismatch", 0),
        "label_invalid": agg["label_status_counts"].get("invalid", 0),
    }
    # consistency: run5 S has audit written=False and no diary -> consistent; craft an inconsistent case
    bad = child([X], [_rec(top, X, "absent", False, "presence_blocked")])  # diary landed, audit says not written
    bad_issues = consistency_checks(bad, S1, cfg)
    got["inconsistent_detected"] = len(bad_issues) == 1
    expect["inconsistent_detected"] = True
    # cap
    capped = _store({}, [_rec(top, X, "absent", False, "presence_blocked")] * (cfg["thresholds"]["5b_audit_cap"] + 1))
    got["cap_detected"] = any("cap" in i for i in consistency_checks(capped, S1, cfg))
    expect["cap_detected"] = True
    # baseline mode: old code, X diary landed, no audit
    base_runs = [("b1", child([F, X], [])), ("b2", child([F], []))]
    base_res = [(n, score_run(parent, c, S1, cfg, baseline=True)) for n, c in base_runs]
    base_agg = aggregate(base_res, cfg, baseline=True)
    got["baseline_absent_written"] = base_agg["baseline_absent_written"]
    expect["baseline_absent_written"] = 1
    got["baseline_valid"] = base_agg["baseline_valid"]
    expect["baseline_valid"] = True
    # S4 deviation: mentioned_only for E role must be deviation_ok
    S4 = cfg["scenarios"]["S4"]
    dev_child = child([F], [_rec(top, F, "participated", True, "ok"),
                            _rec(top, S, "mentioned_only", False, "presence_blocked"),
                            _rec(top, X, "absent", False, "presence_blocked")])
    dev = score_run(parent, dev_child, S4, cfg)
    got["S4_deviation_ok"] = dev[S]["label_status"] == "deviation_ok" and dev[S]["outcome"] == "ok"
    expect["S4_deviation_ok"] = True

    bad_keys = [k for k in expect if expect[k] != got[k]]
    print("== selftest ==")
    for k in expect:
        flag = "ok " if expect[k] == got[k] else "BAD"
        print(f"  [{flag}] {k}: expected {expect[k]!r} got {got[k]!r}")
    print_report("S1(fixture)", agg, results, issues, baseline=False)
    if bad_keys:
        print(f"SELFTEST FAILED: {bad_keys}")
        return 1
    print("SELFTEST PASSED")
    return 0


# ----------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--expect", default=DEFAULT_EXPECT)
    ap.add_argument("--scenario")
    ap.add_argument("--parent")
    ap.add_argument("--run", action="append", default=[])
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    cfg = load_expect(args.expect)

    if args.selftest:
        return selftest(cfg)
    if not (args.scenario and args.parent and args.run):
        ap.error("--scenario, --parent and at least one --run are required (or --selftest)")
    if args.scenario not in cfg["scenarios"]:
        ap.error(f"unknown scenario {args.scenario}")
    scen = cfg["scenarios"][args.scenario]
    parent, parent_sha = load_store(args.parent)
    results, issues = [], {}
    for rp in args.run:
        child, _ = load_store(rp)
        name = os.path.basename(rp)
        results.append((name, score_run(parent, child, scen, cfg, baseline=args.baseline)))
        if not args.baseline:
            issues[name] = consistency_checks(child, scen, cfg)
    agg = aggregate(results, cfg, baseline=args.baseline)
    agg["parent_sha1"] = parent_sha
    if args.json:
        print(json.dumps({"scenario": args.scenario, "baseline": args.baseline, "aggregate": agg,
                          "runs": {n: c for n, c in results}, "consistency": issues}, ensure_ascii=False, indent=2))
    else:
        print(f"parent sha1 {parent_sha}")
        print_report(args.scenario, agg, results, issues, args.baseline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
