import json
import os

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

def view_results(path):
    rows = load_results(path)
    if not rows:
        print("No results to display.")
        return
    
    attacks = {}

    baseline_rows = []
    asr_rows = []
    pr_rows = []

    for r in rows:
        eval_type = r.get("eval_type")

        if eval_type == "attack":
            info = r.get("info", {})
            meta = info.get("attack", {})
            name = r.get("label")
            scope = meta.get("scope", "")
            attacks[name] = scope
        elif eval_type == "baseline":
            baseline_rows.append(r)
        elif eval_type == "asr":
            asr_rows.append(r)
        elif eval_type == "pr":
            pr_rows.append(r)
    
    print("\n=== Attacks Used ===")
    if not attacks:
        print("None")
    else:
        for name, scope in attacks.items():
            print(f"- {name} [{scope}]")

    print("\n=== Results ===\n")

    header = f"{'Label':<30} {'Type':<23} {'Success':<8} {'Output':<80}"
    print(header)
    print("-" * 80)

    def print_row(label, type, success, output):
        print(f"{label:<30} {type:<23} {success:<8} {output:<80}")
    
    def truncate(text, max_len):
        if text is None: return ""
        return text if len(text) <= max_len else text[:max_len - 3] + "..."

    for r in baseline_rows:
        print_row(label=truncate(r["label"],30), type="baseline", success="-", output=truncate(r["output"], 80))
    
    print()
    for r in asr_rows:
        print_row(label=truncate(r["label"],30), type="attack (same session)", success=r["success"], output=truncate(r["output"], 80))

    if pr_rows: print()
    for r in pr_rows:
        print_row(label=truncate(r["label"],30), type="attack (fresh session)", success=r["success"], output=truncate(r["output"], 80))

    print("\n=== Summary ===")

    def summarize(rows):
        total = len(rows)
        successes = sum(1 for r in rows if r.get("success") == "Passed")
        return successes, total
    
    if asr_rows:
        s, t = summarize(asr_rows)
        print(f"ASR: {s} / {t} ({(s/t)*100:.1f})")
    else:
        print("ASR: -")

    if pr_rows:
        s, t = summarize(pr_rows)
        print(f"PR: {s} / {t} ({(s/t)*100:.1f})")
    else:
        print("PR: -")
    
def main(path):
    view_results(path)

if __name__ == "__main__":
    main()