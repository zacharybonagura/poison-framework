import json
import os

# Load rows from results file
def load_results(path):
    rows = []

    if not os.path.exists(path):
        print(f"No results file found at: {path}")
        return rows

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    return rows


# Format results and prints a table that displays baseline, ASR, and PR results
# Groups attacks by context label and displays trial IDs
# Shows trigger status for single-instance attacks
# Computes overall ASR and PR summary metrics
def view_results(path):
    rows = load_results(path)

    if not rows:
        print("No results to display.")
        return None

    # Split rows by evaluation type
    baseline_rows = []
    asr_rows = []
    pr_rows = []

    for r in rows:
        t = r.get("eval_type")
        if t == "baseline":
            baseline_rows.append(r)
        elif t == "asr":
            asr_rows.append(r)
        elif t == "pr":
            pr_rows.append(r)

    # Collect attacks used
    attacks_used = {}

    for r in rows:
        for a in r.get("attacks", []):
            name = a.get("name")
            target = a.get("target")
            scope = a.get("scope")

            if name:
                attacks_used[name] = {
                    "target": target,
                    "scope": scope,
                }

    def truncate(text, max_len):
        if text is None:
            return ""
        return text if len(text) <= max_len else text[:max_len - 3] + "..."

    def summarize_tr(rows):
        total = len(rows)
        triggered = sum(
            1 for r in rows
            if any(a.get("triggered") for a in r.get("attacks", []))
        )
        return triggered, total

    def summarize_asr(rows):
        triggered_rows = [
            r for r in rows
            if any(a.get("triggered") for a in r.get("attacks", []))
        ]
        total = len(triggered_rows)
        successes = sum(1 for r in triggered_rows if r.get("success") == "Passed")
        return successes, total

    def summarize_pr(rows):
        total = len(rows)
        successes = sum(1 for r in rows if r.get("success") == "Passed")
        return successes, total

    def summarize_ta(rows):
        scored = [r for r in rows if r.get("task_correct") is not None]
        if not scored:
            return None, 0
        correct = sum(1 for r in scored if r.get("task_correct") is True)
        return correct, len(scored)

    def summarize_rr(rows):
        total = len(rows)
        refused = sum(1 for r in rows if r.get("refused") is True)
        return refused, total

    # Compute all overall counts first
    baseline_ta_correct, baseline_ta_total = summarize_ta(baseline_rows)
    baseline_rr_refused, baseline_rr_total = summarize_rr(baseline_rows)

    asr_triggered, asr_row_total = summarize_tr(asr_rows)
    asr_successes, asr_denominator = summarize_asr(asr_rows)
    asr_ta_correct, asr_ta_total = summarize_ta(asr_rows)
    asr_rr_refused, asr_rr_total = summarize_rr(asr_rows)

    pr_successes, pr_denominator = summarize_pr(pr_rows)
    pr_ta_correct, pr_ta_total = summarize_ta(pr_rows)
    pr_rr_refused, pr_rr_total = summarize_rr(pr_rows)

    # Per-attack counts
    attack_stats = {}

    for r in asr_rows:
        for a in r.get("attacks", []):
            name = a["name"]

            if name not in attack_stats:
                attack_stats[name] = {
                    "scope": a.get("scope"),
                    "row_total": 0,
                    "triggered": 0,
                    "asr_success": 0,
                    "asr_total": 0,
                    "pr_success": 0,
                    "pr_total": 0,
                    "ta_correct": 0,
                    "ta_total": 0,
                    "rr_refused": 0,
                    "rr_total": 0,
                    "ta_fresh_correct": 0,
                    "ta_fresh_total": 0,
                    "rr_fresh_refused": 0,
                    "rr_fresh_total": 0,
                }

            attack_stats[name]["row_total"] += 1

            if a.get("triggered"):
                attack_stats[name]["triggered"] += 1
                attack_stats[name]["asr_total"] += 1
                if a.get("success"):
                    attack_stats[name]["asr_success"] += 1

            if r.get("task_correct") is not None:
                attack_stats[name]["ta_total"] += 1
                if r.get("task_correct") is True:
                    attack_stats[name]["ta_correct"] += 1

            attack_stats[name]["rr_total"] += 1
            if r.get("refused") is True:
                attack_stats[name]["rr_refused"] += 1

    for r in pr_rows:
        for a in r.get("attacks", []):
            name = a["name"]

            if name not in attack_stats:
                attack_stats[name] = {
                    "scope": a.get("scope"),
                    "row_total": 0,
                    "triggered": 0,
                    "asr_success": 0,
                    "asr_total": 0,
                    "pr_success": 0,
                    "pr_total": 0,
                    "ta_correct": 0,
                    "ta_total": 0,
                    "rr_refused": 0,
                    "rr_total": 0,
                    "ta_fresh_correct": 0,
                    "ta_fresh_total": 0,
                    "rr_fresh_refused": 0,
                    "rr_fresh_total": 0,
                }

            if a.get("scope") == "PERSISTENT":
                attack_stats[name]["pr_total"] += 1
                if a.get("success"):
                    attack_stats[name]["pr_success"] += 1

                if r.get("task_correct") is not None:
                    attack_stats[name]["ta_fresh_total"] += 1
                    if r.get("task_correct") is True:
                        attack_stats[name]["ta_fresh_correct"] += 1

                attack_stats[name]["rr_fresh_total"] += 1
                if r.get("refused") is True:
                    attack_stats[name]["rr_fresh_refused"] += 1

    # Print attacks used
    print("\n=== Attacks Used ===")
    if not attacks_used:
        print("None")
    else:
        for name, info in attacks_used.items():
            print(f"- {name} [{info['target']}] ({info['scope']})")

    # Results table
    print("\n=== Results ===\n")

    def format_attack_status(attacks, fresh=False):
        if not attacks:
            return "-"

        parts = []
        for a in attacks:
            name = a["name"]

            if fresh:
                trig = "-"
            else:
                trig = "Yes" if a.get("triggered") else "No"

            succ = "Yes" if a.get("success") else "No"
            parts.append(f"{name} : {trig} : {succ}")

        return ", ".join(parts)

    attack_strings = []
    for r in rows:
        fresh = (r.get("eval_type") == "pr")
        attack_strings.append(format_attack_status(r.get("attacks", []), fresh=fresh))
    attack_col_width = max(30, max(len(s) for s in attack_strings) if attack_strings else 30) + 3

    header = (
        f"{'Label':<30} {'Trial':<8} {'Type':<18} "
        f"{'Attacks : Triggered : Success':<{attack_col_width}} "
        f"{'Task Correct':<13} {'Refused':<8} | {'Result':<8} {'Output':<7}"
    )
    print(header)
    print("-" * len(header))

    def print_row(label, trial, type_name, success, output, attacks, task_correct, refused):
        fresh = (type_name == "attack (fresh)")
        attack_str = format_attack_status(attacks, fresh=fresh)
        ta_str = "-" if task_correct is None else ("Yes" if task_correct else "No")
        rr_str = "Yes" if refused else "No"

        print(
            f"{truncate(label,30):<30} "
            f"{trial:<8} "
            f"{type_name:<18} "
            f"{attack_str:<{attack_col_width}} "
            f"{ta_str:<13} "
            f"{rr_str:<8} "
            f"| "
            f"{success:<8} "
            f"{truncate(output,60)}"
        )

    for r in baseline_rows:
        print_row(
            label=r["label"],
            trial="-",
            type_name="baseline",
            attacks=[],
            success="-",
            output=r["output"],
            task_correct=r["task_correct"],
            refused=r["refused"],
        )

    if baseline_rows and asr_rows:
        print()

    asr_rows.sort(key=lambda r: (r["label"], r.get("trial_id", -1)))
    for r in asr_rows:
        trial = r.get("trial_id")
        trial = trial + 1 if trial is not None else "-"
        print_row(
            label=r["label"],
            trial=trial,
            type_name="attack",
            attacks=r.get("attacks", []),
            success=r["success"],
            output=r["output"],
            task_correct=r["task_correct"],
            refused=r["refused"],
        )

    if pr_rows:
        print()

    pr_rows.sort(key=lambda r: (r["label"], r.get("trial_id", -1)))
    for r in pr_rows:
        trial = r.get("trial_id")
        trial = trial + 1 if trial is not None else "-"
        print_row(
            label=r["label"],
            trial=trial,
            type_name="attack (fresh)",
            attacks=r.get("attacks", []),
            success=r["success"],
            output=r["output"],
            task_correct=r["task_correct"],
            refused=r["refused"],
        )

    # Per-attack summary
    print("\n=== Per-Attack Summary ===")

    for name, stats in attack_stats.items():
        scope = stats["scope"]
        trig = stats["triggered"]
        row_total = stats["row_total"]
        asr_succ = stats["asr_success"]
        asr_total = stats["asr_total"]
        pr_succ = stats["pr_success"]
        pr_total = stats["pr_total"]
        ta_correct = stats["ta_correct"]
        ta_total = stats["ta_total"]
        rr_refused = stats["rr_refused"]
        rr_total = stats["rr_total"]
        ta_fresh_correct = stats["ta_fresh_correct"]
        ta_fresh_total = stats["ta_fresh_total"]
        rr_fresh_refused = stats["rr_fresh_refused"]
        rr_fresh_total = stats["rr_fresh_total"]

        print(f"\n{name}")

        trig_pct = (trig / row_total) * 100 if row_total > 0 else 0.0
        print(f"TR : {trig} / {row_total} ({trig_pct:.1f}%)")

        if asr_total > 0:
            print(f"ASR: {asr_succ} / {asr_total} ({(asr_succ/asr_total)*100:.1f}%)")
        else:
            print("ASR: -")

        if ta_total > 0:
            print(f"TA (attack): {ta_correct} / {ta_total} ({(ta_correct/ta_total)*100:.1f}%)")
        else:
            print("TA (attack): -")

        if rr_total > 0:
            print(f"RR (attack): {rr_refused} / {rr_total} ({(rr_refused/rr_total)*100:.1f}%)")
        else:
            print("RR (attack): -")

        if scope == "PERSISTENT":
            print()

            if pr_total > 0:
                print(f"PR : {pr_succ} / {pr_total} ({(pr_succ/pr_total)*100:.1f}%)")
            else:
                print("PR : 0 / 0 (0.0%)")

            if ta_fresh_total > 0:
                print(f"TA (fresh): {ta_fresh_correct} / {ta_fresh_total} ({(ta_fresh_correct/ta_fresh_total)*100:.1f}%)")
            else:
                print("TA (fresh): -")

            if rr_fresh_total > 0:
                print(f"RR (fresh): {rr_fresh_refused} / {rr_fresh_total} ({(rr_fresh_refused/rr_fresh_total)*100:.1f}%)")
            else:
                print("RR (fresh): -")
        else:
            print("PR : -")

    # Overall summary
    print("\n=== Overall Summary ===")

    if baseline_rows:
        print()

        if baseline_ta_correct is None or baseline_ta_total == 0:
            print("TA (baseline): -")
        else:
            print(f"TA (baseline): {baseline_ta_correct} / {baseline_ta_total} ({(baseline_ta_correct/baseline_ta_total)*100:.1f}%)")

        if baseline_rr_total > 0:
            print(f"RR (baseline): {baseline_rr_refused} / {baseline_rr_total} ({(baseline_rr_refused/baseline_rr_total)*100:.1f}%)")
        else:
            print("RR (baseline): -")

    if asr_rows:
        print()

        if asr_row_total > 0:
            print(f"TR : {asr_triggered} / {asr_row_total} ({(asr_triggered/asr_row_total)*100:.1f}%)")
        else:
            print("TR : -")

        if asr_denominator > 0:
            print(f"ASR: {asr_successes} / {asr_denominator} ({(asr_successes/asr_denominator)*100:.1f}%)")
        else:
            print("ASR: -")

        if asr_ta_correct is None or asr_ta_total == 0:
            print("TA (attack): -")
        else:
            print(f"TA (attack): {asr_ta_correct} / {asr_ta_total} ({(asr_ta_correct/asr_ta_total)*100:.1f}%)")

        if asr_rr_total > 0:
            print(f"RR (attack): {asr_rr_refused} / {asr_rr_total} ({(asr_rr_refused/asr_rr_total)*100:.1f}%)")
        else:
            print("RR (attack): -")
    else:
        print("TR : -")
        print("ASR: -")

    if pr_rows:
        print()

        if pr_denominator > 0:
            print(f"PR : {pr_successes} / {pr_denominator} ({(pr_successes/pr_denominator)*100:.1f}%)")
        else:
            print("PR : -")

        if pr_ta_correct is None or pr_ta_total == 0:
            print("TA (fresh): -")
        else:
            print(f"TA (fresh): {pr_ta_correct} / {pr_ta_total} ({(pr_ta_correct/pr_ta_total)*100:.1f}%)")

        if pr_rr_total > 0:
            print(f"RR (fresh): {pr_rr_refused} / {pr_rr_total} ({(pr_rr_refused/pr_rr_total)*100:.1f}%)")
        else:
            print("RR (fresh): -")
    else:
        print("PR : -")

    print()

    return {
        "baseline": {
            "ta_correct": baseline_ta_correct or 0,
            "ta_total": baseline_ta_total,
            "rr_refused": baseline_rr_refused,
            "rr_total": baseline_rr_total,
        },
        "asr": {
            "triggered": asr_triggered,
            "row_total": asr_row_total,
            "successes": asr_successes,
            "denominator": asr_denominator,
            "ta_correct": asr_ta_correct or 0,
            "ta_total": asr_ta_total,
            "rr_refused": asr_rr_refused,
            "rr_total": asr_rr_total,
        },
        "pr": {
            "successes": pr_successes,
            "denominator": pr_denominator,
            "ta_correct": pr_ta_correct or 0,
            "ta_total": pr_ta_total,
            "rr_refused": pr_rr_refused,
            "rr_total": pr_rr_total,
        },
    }


def view_aggregate_variant_results(all_variant_results, title="Cross-Variant Summary"):
    print(f"\n\n=== {title} ===\n")

    total_asr_triggered = 0
    total_asr_rows = 0
    total_asr_successes = 0
    total_asr_denominator = 0

    total_pr_successes = 0
    total_pr_denominator = 0

    total_ta_asr_correct = 0
    total_ta_asr_total = 0
    total_rr_asr_refused = 0
    total_rr_asr_total = 0

    total_ta_pr_correct = 0
    total_ta_pr_total = 0
    total_rr_pr_refused = 0
    total_rr_pr_total = 0

    for entry in all_variant_results:
        name = entry["variant_name"]
        summary = entry["summary"]

        asr = summary["asr"]
        pr = summary["pr"]

        print(f"{name}:")

        if asr["row_total"] > 0:
            print(f"  TR : {asr['triggered']} / {asr['row_total']} ({(asr['triggered']/asr['row_total'])*100:.1f}%)")
        else:
            print("  TR : -")

        if asr["denominator"] > 0:
            print(f"  ASR: {asr['successes']} / {asr['denominator']} ({(asr['successes']/asr['denominator'])*100:.1f}%)")
        else:
            print("  ASR: -")

        if asr["ta_total"] > 0:
            print(f"  TA (attack): {asr['ta_correct']} / {asr['ta_total']} ({(asr['ta_correct']/asr['ta_total'])*100:.1f}%)")
        else:
            print("  TA (attack): -")

        if asr["rr_total"] > 0:
            print(f"  RR (attack): {asr['rr_refused']} / {asr['rr_total']} ({(asr['rr_refused']/asr['rr_total'])*100:.1f}%)")
        else:
            print("  RR (attack): -")

        print()
        if pr["denominator"] > 0:
            print(f"  PR : {pr['successes']} / {pr['denominator']} ({(pr['successes']/pr['denominator'])*100:.1f}%)")
        else:
            print("  PR : -")

        if pr["ta_total"] > 0:
            print(f"  TA (fresh): {pr['ta_correct']} / {pr['ta_total']} ({(pr['ta_correct']/pr['ta_total'])*100:.1f}%)")
        else:
            print("  TA (fresh): -")

        if pr["rr_total"] > 0:
            print(f"  RR (fresh): {pr['rr_refused']} / {pr['rr_total']} ({(pr['rr_refused']/pr['rr_total'])*100:.1f}%)")
        else:
            print("  RR (fresh): -")

        print()

        total_asr_triggered += asr["triggered"]
        total_asr_rows += asr["row_total"]
        total_asr_successes += asr["successes"]
        total_asr_denominator += asr["denominator"]

        total_pr_successes += pr["successes"]
        total_pr_denominator += pr["denominator"]

        total_ta_asr_correct += asr["ta_correct"]
        total_ta_asr_total += asr["ta_total"]
        total_rr_asr_refused += asr["rr_refused"]
        total_rr_asr_total += asr["rr_total"]

        total_ta_pr_correct += pr["ta_correct"]
        total_ta_pr_total += pr["ta_total"]
        total_rr_pr_refused += pr["rr_refused"]
        total_rr_pr_total += pr["rr_total"]

    print("=== Totals Across All Variants ===\n")

    if total_asr_rows > 0:
        print(f"TR : {total_asr_triggered} / {total_asr_rows} ({(total_asr_triggered/total_asr_rows)*100:.1f}%)")
    else:
        print("TR : -")

    if total_asr_denominator > 0:
        print(f"ASR: {total_asr_successes} / {total_asr_denominator} ({(total_asr_successes/total_asr_denominator)*100:.1f}%)")
    else:
        print("ASR: -")

    if total_ta_asr_total > 0:
        print(f"TA (attack): {total_ta_asr_correct} / {total_ta_asr_total} ({(total_ta_asr_correct/total_ta_asr_total)*100:.1f}%)")
    else:
        print("TA (attack): -")

    if total_rr_asr_total > 0:
        print(f"RR (attack): {total_rr_asr_refused} / {total_rr_asr_total} ({(total_rr_asr_refused/total_rr_asr_total)*100:.1f}%)")
    else:
        print("RR (attack): -")

    print()

    if total_pr_denominator > 0:
        print(f"PR : {total_pr_successes} / {total_pr_denominator} ({(total_pr_successes/total_pr_denominator)*100:.1f}%)")
    else:
        print("PR : -")

    if total_ta_pr_total > 0:
        print(f"TA (fresh): {total_ta_pr_correct} / {total_ta_pr_total} ({(total_ta_pr_correct/total_ta_pr_total)*100:.1f}%)")
    else:
        print("TA (fresh): -")

    if total_rr_pr_total > 0:
        print(f"RR (fresh): {total_rr_pr_refused} / {total_rr_pr_total} ({(total_rr_pr_refused/total_rr_pr_total)*100:.1f}%)")
    else:
        print("RR (fresh): -")

    print()


def main(path):
    view_results(path)

if __name__ == "__main__":
    main()