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

def print_table(rows):
    if not rows:
        print("No results to display.")
        return

    print("\n=== Experiment Results ===\n")

    header = f"{'Attack Name':<16} {'Triggered':<10} {'Success':<8} Output"
    print(header)
    print("-" * len(header))

    did_trigger_count = 0
    success_count = 0

    for r in rows:
        info = r["info"]

        label = r.get("label", "No Name").strip()
        triggered = info.get("did_trigger", False)
        success = info.get("success", False)
        output = r.get("output", "").strip()

        if triggered: did_trigger_count += 1
        if success: success_count += 1

        if len(label) > 16: label = label[:13] + "..."
        if len(output) > 50: output = output[:47] + "..."

        print(
            f"{label:<16} "
            f"{str(triggered):<10} "
            f"{str(success):<8} "
            f"{output}"
        )

    asr = (success_count / did_trigger_count) if did_trigger_count else 0.0

    print("\n=== Summary ===")
    print(f"Total runs: {len(rows)}")
    print(f"Triggered runs: {did_trigger_count}")
    print(f"Successful attacks: {success_count}")
    print(f"ASR: {asr:.3f}")
    print()

def view_results(path: str):
    rows = load_results(path)
    print_table(rows)
