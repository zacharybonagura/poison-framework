# AgentPoisonFramework

An extensible evaluation framework for studying poisoning attacks on LLM agents.

This framework supports:

### Attacks
- Prompt injection
- Chain-of-thought reasoning
  
### Scopes
- Single instance poisoning
- Persistent memory poisoning

### Metrics
- Attack Success Rate (ASR) evaluation
- Persistence Rate (PR) evaluation
- Multi-trial stochastic evaluation

---

## Overview

Modern LLM agents often use:

- System prompts
- Tool interfaces
- Retrieval-augmented memory
- Persistent storage

These components introduce new attack surfaces. This framework provides a modular way to:

1. Define attack strategies
2. Inject attacks into prompt or memory
3. Measure attack effectiveness
4. Measure attack persistence across sessions
5. Run multiple stochastic trials
6. Log structured results for analysis

---

## Metrics

### ASR (Attack Success Rate)

Measures the percentage of evaluation prompts for which the attack successfully influences the model output.

ASR = successful attack responses / total evaluation prompts

### PR (Persistence Rate)

Measures whether a persistent memory attack continues to influence the model when run in a fresh session.

PR = successful responses in fresh session / total evaluation prompts

Baseline runs are executed once.
Attack experiments can run multiple trials for more accurate statistics.

## Running an Experiment

Experiments are executed through the `run.py` entrypoint.
```bash
python run.py <attack_type> <experiment_name> [options]
```

Example
```bash
python run.py prompt_injection pi_small_persistent --num_trials 2
```
This command:
- Loads the `prompt_injection` attack type
- Runs the `pi_small_persistent` experiment
- Executes 2 independent trials

### Command Arguments

| Argument     | Description |
|--------------|-------------|
| `attack`     | Folder name under `experiments/benchmarks/` |
| `experiment` | Python file name (without `.py`) |

### Optional Flags
| Flag | Description | Default |
|------|-------------|---------|
| `--llm` | LLM backend (`fake` or `real`) | `real` |
| `--num_trials` | Number of independent trials | `1` |
| `--retrieval_mode` | Memory retrieval strategy (`all`, `top_k`, `by_key`, `random`) | `all` |
| `--retrieval_k` | k value for `top_k` or `random` retrieval | `None` |
| `--retrieval_key` | Key for `by_key` retrieval | `None` |
| `--memory_path` | Custom memory file path | Auto-generated |
| `--output_path` | Custom results file path | Auto-generated |

### Default Memory/Output Locations

If not specified:
- **Memory file:**
```bash
experiments/memory/<attack>/<experiment>.json
```

- **Results file:**
```bash
experiments/results/<attack>/<experiment>.jsonl
```


## Execution Flow
For attack experiments:

1. Baseline is run once.

2. For each trial:
    - Memory is reset
    - Attack is injected (prompt or persistent).
    - ASR is evaluated.
    - PR is evaluated for persistent attacks.

3. Results are logged in structured JSONL format.
   - `format_results.py` prints grouped trial summaries.

