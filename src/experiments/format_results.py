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
    has_triggered = any("triggered" in r for r in rows)

    if not rows:
        print("No results to display.")
        return
    
    single_instance_attacks = {}
    memory_attacks = {}

    baseline_rows = []
    asr_rows = []
    pr_rows = []

    for r in rows:
        eval_type = r.get("eval_type")

        if eval_type == "memory_inject":
            info = r.get("info", {})
            meta = info.get("attack", {})
            name = r.get("label")
            scope = meta.get("scope", "")
            memory_attacks[name] = scope
        elif "attack" in r:
            meta = r["attack"]
            if meta["scope"] == "SINGLE_INSTANCE":
                single_instance_attacks[meta["name"]] = meta["target"]

        if eval_type == "baseline":
            baseline_rows.append(r)
        elif eval_type == "asr":
            asr_rows.append(r)
        elif eval_type == "pr":
            pr_rows.append(r)
    
    print("\n=== Single-Instance Attacks Used ===")
    if not single_instance_attacks:
        print("None")
    else:
        for name, target in single_instance_attacks.items():
            print(f"- {name} [{target}]")
            
    print("\n=== Attacks Stored In Memory ===")
    if not memory_attacks:
        print("None")
    else:
        for name, scope in memory_attacks.items():
            print(f"- {name} [{scope}]")

    print("\n=== Results ===\n")

    if has_triggered:
        header = f"{'Label':<30} {'Trial':<8} {'Type':<23} {'Triggered':<10} {'Success':<8} {'Output':<7}"
    else:
        header = f"{'Label':<30} {'Trial':<8} {'Type':<23} {'Success':<8} {'Output':<7}"

    print(header)
    print("-" * len(header))

    def print_row(label, trial, type, success, output, triggered="-"):
        if has_triggered:
            print(f"{label:<30} {trial:<8} {type:<23} {triggered:<10} {success:<8} {output}")
        else:
            print(f"{label:<30} {trial:<8} {type:<23} {success:<8} {output}")

    
    def truncate(text, max_len):
        if text is None: return ""
        return text if len(text) <= max_len else text[:max_len - 3] + "..."

    for r in baseline_rows:
        print_row(label=truncate(r["label"],30), trial="-", type="baseline", success="-", output=r["output"])
    
    print()
    asr_rows.sort(key=lambda r: (r["label"], r.get("trial_id", -1)))

    current_label = None
    for r in asr_rows:
        if r["label"] != current_label: 
            if current_label is not None: print()
            current_label = r["label"]

        trial_label = r.get('trial_id') + 1 if r.get('trial_id') is not None else "-"

        print_row(
            label=truncate(r["label"],30),
            trial=trial_label,
            type="attack",
            success=r["success"],
            output=r["output"],
            triggered=r.get("triggered","-")
        )

    if pr_rows: print()
    pr_rows.sort(key=lambda r: (r["label"], r.get("trial_id", -1)))

    current_label = None

    for r in pr_rows:
        if r["label"] != current_label:
            if current_label is not None: print()
            current_label = r["label"]

        trial_label = r.get('trial_id') + 1 if r.get('trial_id') is not None else "-"

        print_row(
            label=truncate(r["label"],30),
            trial=trial_label,
            type="attack (fresh session)",
            success=r["success"],
            output=r["output"],
            triggered=r.get("triggered","-")
        )
        

    print("\n=== Summary ===")

    def summarize(rows):
        total = len(rows)
        successes = sum(1 for r in rows if r.get("success") == "Passed")
        return successes, total

    if asr_rows:
        successes, total = summarize(asr_rows)
        if has_triggered:
            triggered = sum(1 for r in rows if r.get("triggered") == "Yes")
            print(f"TR: {triggered} / {total} ({(triggered/total)*100:.1f})")
        print(f"ASR: {successes} / {total} ({(successes/total)*100:.1f})")
    else:
        print("ASR: -")

    if pr_rows:
        successes, total = summarize(pr_rows)
        print(f"PR: {successes} / {total} ({(successes/total)*100:.1f})")
    
def main(path):
    view_results(path)

if __name__ == "__main__":
    main()