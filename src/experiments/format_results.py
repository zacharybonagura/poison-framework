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
        return

    # Collect all attacks used
    attacks_used = {}

    for r in rows:
        for a in r.get("attacks", []):
            name = a.get("name")
            target = a.get("target")
            scope = a.get("scope")

            if name:
                attacks_used[name] = {
                    "target": target,
                    "scope": scope
                }

    # Print attacks used
    print("\n=== Attacks Used ===")

    if not attacks_used:
        print("None")
    else:
        for name, info in attacks_used.items():
            print(f"- {name} [{info['target']}] ({info['scope']})")

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

    print("\n=== Results ===\n")

    def format_attack_status(attacks):
        if not attacks:
            return "-"

        parts = []
        for a in attacks:
            name = a["name"]
            scope = a.get("scope")

            if scope == "PERSISTENT": trig = "-"
            else: trig = "Yes" if a.get("triggered") else "No"

            succ = "Yes" if a.get("success") else "No"

            parts.append(f"{name} : {trig} : {succ}")

        return ", ".join(parts)
    
    attack_strings = [
        format_attack_status(r.get("attacks", []))
        for r in rows
    ]
    attack_col_width = max(30, max(len(s) for s in attack_strings))

    header = f"{'Label':<30} {'Trial':<8} {'Type':<18} {'Attacks : Triggered : Success':<{attack_col_width}} {'Task Correct':<13} {'Refused':<8} | {'Result':<8} {'Output':<7}"
    print(header)
    print("-" * len(header))

    def truncate(text, max_len):
        if text is None: return ""
        return text if len(text) <= max_len else text[:max_len - 3] + "..."
    
    
    def print_row(label, trial, type, success, output, attacks, task_correct, refused):
        attack_str = format_attack_status(attacks)
        ta_str = "-" if task_correct is None else ("Yes" if task_correct else "No")
        rr_str = "Yes" if refused else "No"

        print(
            f"{truncate(label,30):<30} "
            f"{trial:<8} "
            f"{type:<18} "
            f"{attack_str:<{attack_col_width}} "
            f"{ta_str:<13} "
            f"{rr_str:<8} "
            "| "
            f"{success:<8} "
            f"{truncate(output,60)}"
        )

    for r in baseline_rows:
        print_row(
            label=r["label"],
            trial="-",
            type="baseline",
            attacks=[],
            success="-",
            output=r["output"],
            task_correct=r["task_correct"],
            refused=r["refused"],
        )

    print()
    asr_rows.sort(key=lambda r: (r["label"], r.get("trial_id", -1)))

    for r in asr_rows:
        trial = r.get("trial_id")
        trial = trial + 1 if trial is not None else "-"

        print_row(
            label=r["label"],
            trial=trial,
            type="attack",
            attacks=r.get("attacks", []),
            success=r["success"],
            output=r["output"],
            task_correct=r["task_correct"],
            refused=r["refused"],
        )

    if pr_rows: print()
    pr_rows.sort(key=lambda r: (r["label"], r.get("trial_id", -1)))

    for r in pr_rows:
        trial = r.get("trial_id")
        trial = trial + 1 if trial is not None else "-"

        print_row(
            label=r["label"],
            trial=trial,
            type="attack (fresh)",
            attacks=r.get("attacks", []),
            success=r["success"],
            output=r["output"],
            task_correct=r["task_correct"],
            refused=r["refused"],
        )
        
    print("\n=== Per-Attack Summary ===")

    attack_stats = {}

    # Collect ASR + TA + RR stats
    for r in rows:
        if r.get("eval_type") != "asr":
            continue

        for a in r.get("attacks", []):
            name = a["name"]

            if name not in attack_stats:
                attack_stats[name] = {
                    "scope": a.get("scope"),
                    "triggered": 0,
                    "asr_success": 0,
                    "asr_total": 0,
                    "pr_success": 0,
                    "pr_total": 0,
                    "ta_correct": 0,
                    "ta_total": 0,
                    "rr_refused": 0,
                    "rr_total": 0,
                }

            attack_stats[name]["asr_total"] += 1

            if a.get("triggered"):
                attack_stats[name]["triggered"] += 1

            if a.get("success"):
                attack_stats[name]["asr_success"] += 1

            # TA
            if r.get("task_correct") is not None:
                attack_stats[name]["ta_total"] += 1
                if r.get("task_correct") is True:
                    attack_stats[name]["ta_correct"] += 1

            # RR
            attack_stats[name]["rr_total"] += 1
            if r.get("refused") is True:
                attack_stats[name]["rr_refused"] += 1

    # Collect PR stats
    for r in rows:
        if r.get("eval_type") != "pr":
            continue

        for a in r.get("attacks", []):
            name = a["name"]

            if name not in attack_stats:
                attack_stats[name] = {
                    "scope": a.get("scope"),
                    "triggered": 0,
                    "asr_success": 0,
                    "asr_total": 0,
                    "pr_success": 0,
                    "pr_total": 0,
                    "ta_correct": 0,
                    "ta_total": 0,
                    "rr_refused": 0,
                    "rr_total": 0,
                }

            # Only persistent attacks should count toward PR
            if a.get("scope") == "PERSISTENT":
                attack_stats[name]["pr_total"] += 1
                if a.get("success"):
                    attack_stats[name]["pr_success"] += 1

    for name, stats in attack_stats.items():
        scope = stats["scope"]
        trig = stats["triggered"]
        asr_succ = stats["asr_success"]
        asr_total = stats["asr_total"]
        pr_succ = stats["pr_success"]
        pr_total = stats["pr_total"]
        ta_correct = stats["ta_correct"]
        ta_total = stats["ta_total"]
        rr_refused = stats["rr_refused"]
        rr_total = stats["rr_total"]

        print(f"\n{name}")

        if scope == "PERSISTENT":
            print("TR : -")
        else:
            trig_pct = (trig / asr_total) * 100 if asr_total > 0 else 0.0
            print(f"TR : {trig} / {asr_total} ({trig_pct:.1f}%)")

        if asr_total > 0:
            print(f"ASR: {asr_succ} / {asr_total} ({(asr_succ/asr_total)*100:.1f}%)")
        else:
            print("ASR: -")

        if ta_total > 0:
            print(f"TA : {ta_correct} / {ta_total} ({(ta_correct/ta_total)*100:.1f}%)")
        else:
            print("TA : -")

        if rr_total > 0:
            print(f"RR : {rr_refused} / {rr_total} ({(rr_refused/rr_total)*100:.1f}%)")
        else:
            print("RR : -")

        if scope == "PERSISTENT":
            if pr_total > 0:
                print(f"PR : {pr_succ} / {pr_total} ({(pr_succ/pr_total)*100:.1f}%)")
            else:
                print("PR : 0 / 0 (0.0%)")
        else:
            print("PR : -")
        
    print("\n=== Overall Summary ===\n")

    def summarize(rows):
        total = len(rows)
        successes = sum(1 for r in rows if r.get("success") == "Passed")
        return successes, total
    
    def summarize_task_accuracy(rows):
        scored = [r for r in rows if r.get("task_correct") is not None]
        if not scored:
            return None, 0
        correct = sum(1 for r in scored if r.get("task_correct") is True)
        return correct, len(scored)

    def summarize_refusal_rate(rows):
        total = len(rows)
        refused = sum(1 for r in rows if r.get("refused") is True)
        return refused, total

    if baseline_rows:
        correct, total = summarize_task_accuracy(baseline_rows)
        if correct is None or total == 0:
            print(f"TA (baseline): -")
        else:
            print(f"TA (baseline): {correct} / {total} ({(correct/total)*100:.1f}%)")
        refused, total = summarize_refusal_rate(baseline_rows)
        print(f"RR (baseline): {refused} / {total} ({(refused/total)*100:.1f}%)")
        
    if asr_rows:
        print()
        successes, total = summarize(asr_rows)
        print(f"ASR: {successes} / {total} ({(successes/total)*100:.1f}%)")

        correct, total = summarize_task_accuracy(asr_rows)
        if correct is None or total == 0:
            print("TA (attack): -")
        else:
            print(f"TA (attack): {correct} / {total} ({(correct/total)*100:.1f}%)")

        refused, total = summarize_refusal_rate(asr_rows)
        print(f"RR (attack): {refused} / {total} ({(refused/total)*100:.1f}%)")
    else:
        print("ASR: -")

    if pr_rows:
        print()
        successes, total = summarize(pr_rows)
        print(f"PR : {successes} / {total} ({(successes/total)*100:.1f}%)")

        correct, total = summarize_task_accuracy(pr_rows)
        if correct is None or total == 0:
            print("TA (fresh): -")
        else:
            print(f"TA (fresh): {correct} / {total} ({(correct/total)*100:.1f}%)")

        refused, total = summarize_refusal_rate(pr_rows)
        print(f"RR (fresh): {refused} / {total} ({(refused/total)*100:.1f}%)")
    else:
        print("PR : -")
    
    print()

def main(path):
    view_results(path)

if __name__ == "__main__":
    main()