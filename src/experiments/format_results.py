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
    # pr_rows = []

    for r in rows:
        t = r.get("eval_type")

        if t == "baseline":
            baseline_rows.append(r)
        elif t == "asr":
            asr_rows.append(r)
        # elif t == "pr":
        #     pr_rows.append(r)

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
    attack_col_width = max(25, max(len(s) for s in attack_strings))

    header = f"{'Label':<30} {'Trial':<8} {'Type':<18} {'Attacks : Triggered : Success':<{attack_col_width}}{'Result':<8} {'Output':<7}"
    print(header)
    print("-" * len(header))

    def truncate(text, max_len):
        if text is None: return ""
        return text if len(text) <= max_len else text[:max_len - 3] + "..."
    
    
    def print_row(label, trial, type, success, output, attacks):
        attack_str = format_attack_status(attacks)

        print(
            f"{truncate(label,30):<30} "
            f"{trial:<8} "
            f"{type:<18} "
            f"{attack_str:<{attack_col_width}} "
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
        )

    # if pr_rows: print()
    # pr_rows.sort(key=lambda r: (r["label"], r.get("trial_id", -1)))

    # for r in pr_rows:
    #     trial = r.get("trial_id")
    #     trial = trial + 1 if trial is not None else "-"

    #     print_row(
    #         label=r["label"],
    #         trial=trial,
    #         type="attack (fresh)",
    #         attacks=r.get("attacks", []),
    #         success=r["success"],
    #         output=r["output"],
    #     )
        
    print("\n=== Per-Attack Summary ===")

    attack_stats = {}

    for r in rows:
        if r.get("eval_type") != "asr":
            continue

        for a in r.get("attacks", []):
            name = a["name"]

            if name not in attack_stats:
                attack_stats[name] = {
                    "triggered": 0,
                    "success": 0,
                    "total": 0,
                    "scope": a.get("scope")
                }

            attack_stats[name]["total"] += 1

            if a.get("triggered"):
                attack_stats[name]["triggered"] += 1

            if a.get("success"):
                attack_stats[name]["success"] += 1


    for name, stats in attack_stats.items():
        total = stats["total"]
        trig = stats["triggered"]
        succ = stats["success"]
        scope = stats["scope"]

        print(f"\n{name}")

        if scope == "PERSISTENT": print("TR : -")
        else: print(f"TR : {trig} / {total} ({(trig/total)*100:.1f}%)")

        print(f"ASR: {succ} / {total} ({(succ/total)*100:.1f}%)")
        
    print("\n=== Overall Summary ===")

    def summarize(rows):
        total = len(rows)
        successes = sum(1 for r in rows if r.get("success") == "Passed")
        return successes, total

    if asr_rows:
        s, t = summarize(asr_rows)
        print(f"ASR: {s} / {t} ({(s/t)*100:.1f}%)")
    else:
        print("ASR: -")

    # if pr_rows:
    #     s, t = summarize(pr_rows)
    #     print(f"PR : {s} / {t} ({(s/t)*100:.1f}%)")
    
def main(path):
    view_results(path)

if __name__ == "__main__":
    main()