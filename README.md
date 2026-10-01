# AgentPoisonFramework

An extensible evaluation framework for studying **runtime poisoning attacks on LLM-based agents**.

The framework provides a common experimental interface for studying how adversarial content can influence different components of an agent at inference time, without requiring access to model weights, training data, or internal model state.

> **Research project:** This framework is designed for controlled evaluation and comparison of poisoning mechanisms rather than maximizing attack strength.

## Paper

This repository accompanies the paper:

**Poisoning Attacks on LLM-Based Agents: A General Evaluation Framework**

The full paper is available here:

[Read the paper](Poisoning_Attacks_on_LLM_Based_Agents.pdf)

---

## Overview

Modern LLM agents combine multiple components to perform tasks, including:

* System prompts and user inputs
* Intermediate reasoning
* External tools
* Retrieval-augmented memory
* Action-selection policies
* Persistent storage

Each component introduces a potential runtime attack surface.

**AgentPoisonFramework** provides a unified environment for evaluating these surfaces under consistent experimental conditions.

The framework supports:

1. Multiple poisoning attack surfaces
2. Single-instance and persistent poisoning
3. Trigger-conditioned attacks
4. Configurable memory retrieval
5. Rule-based and LLM-based evaluation
6. Single-surface experiments
7. Pairwise attack composition
8. Multi-surface poisoning
9. Multi-trial stochastic evaluation
10. Structured JSONL experiment results

The framework is built around a shared attack abstraction so that different poisoning mechanisms can be evaluated using the same execution and measurement pipeline.

---

## Research Goal

The goal is to study **how runtime poisoning propagates through an LLM-agent pipeline**.

Rather than introducing highly optimized attack-generation techniques, the framework uses controlled, manually constructed attack instances. This reduces variability caused by attack optimization and makes it easier to compare the behavior of different agent components under a common experimental setup.

The framework should therefore be viewed as a **mechanism-level evaluation framework**, rather than a benchmark for maximum attack strength.

---

# Attack Surfaces

The framework currently supports five poisoning surfaces.

| Attack Surface       | Target                     | Description                                             |
| -------------------- | -------------------------- | ------------------------------------------------------- |
| **Prompt Injection** | User/prompt construction   | Injects adversarial instructions into the prompt        |
| **Reasoning**        | Reasoning guidance         | Manipulates the reasoning policy used by the agent      |
| **Tool Interface**   | Tool descriptions/policies | Alters how the agent interprets and uses tools          |
| **Memory Retrieval** | Retrieved memory           | Poisons memory that can influence future agent behavior |
| **Action Policy**    | Action-selection guidance  | Manipulates how the agent selects or structures actions |

All attack types use the same underlying attack abstraction and execution pipeline.

### Prompt Injection

`PromptInjectionAttack` modifies the `user_input` portion of the execution context.

The attack can be positioned as a prefix, suffix, or relative to a trigger phrase.

### Reasoning Manipulation

`ReasoningAttack` inserts a malicious reasoning directive into the system prompt.

This allows the framework to evaluate poisoning of the agent's intermediate reasoning policy rather than directly modifying the final response.

### Tool Interface Poisoning

`ToolInterfaceAttack` modifies the natural-language description of a target tool and can inject tool-use policy text.

The current implementation focuses on description-level and policy-level poisoning rather than directly modifying tool outputs.

### Memory Retrieval Poisoning

`MemoryRetrievalAttack` inserts malicious entries into the agent's memory context.

Persistent experiments can store these entries in the external memory store and evaluate whether they influence a later session through retrieval.

### Action-Policy Poisoning

`ActionPolicyAttack` modifies the agent's action-selection guidance by appending a malicious directive to the execution plan.

This allows the framework to study attacks against the decision-making layer of an agent.

---

# Threat Model

The framework considers a **black-box runtime adversary**.

The attacker does **not** have access to:

* Model weights
* Training data
* Hidden model state
* Agent source code

Instead, the attacker influences the agent through runtime-accessible surfaces such as:

* Prompts
* Reasoning guidance
* Tool interfaces
* Retrieved memory
* Action-policy guidance

Attacks can be either temporary or persistent.

---

# Poisoning Scopes

## Single-Instance Poisoning

A single-instance attack affects only the current agent execution.

The malicious content is injected into the runtime context and is discarded when the session ends.

```text
Clean Context
      │
      ▼
Attack Injection
      │
      ▼
Poisoned Agent Execution
      │
      ▼
Output
```

This setting measures the immediate effectiveness of an attack.

---

## Persistent Poisoning

Persistent attacks are evaluated across sessions.

The attack is first injected during an actively compromised session and then written to long-term memory.

A fresh agent session is subsequently created without active injection.

If the attack succeeds during the fresh session, the behavior must result from the poisoned memory being retrieved and used by the agent.

```text
Session 1
─────────
Attack Injection
      │
      ▼
Poisoned Execution
      │
      ▼
Write Malicious Content
to Persistent Memory
      │
      ▼
      └──────────────────┐
                         │
                         ▼
Session 2          Memory Retrieval
─────────                │
                         ▼
                  Fresh Agent Session
                         │
                         ▼
                       Output
```

This separates:

* **Immediate attack effectiveness**
* **Cross-session persistence**

The memory store is represented as a lightweight JSON-backed collection containing entries such as keys, values, and source labels.

---

# Framework Architecture

The main components are:

### `AgentContext`

Represents the information available to the agent during execution.

It can contain:

* Task label
* System prompt
* User input
* Available tools
* Retrieved memory
* Action-policy guidance
* Metadata

The `AgentContext` provides the common object that attacks manipulate at runtime.

### `Attack`

All poisoning attacks inherit from a common abstract interface.

An attack defines concepts such as:

* Attack name
* Target component
* Success checker
* Poisoning scope
* Optional trigger

The primary method is:

```python
inject()
```

Persistent attacks may additionally implement:

```python
persist_longterm()
```

This allows different attack mechanisms to participate in the same experimental pipeline.

### `Agent Runner`

The agent runner executes the agent under clean or poisoned conditions.

The execution loop can involve:

```text
Prompt
  ↓
LLM
  ↓
Tool Call?
  ↓
Tool Execution
  ↓
Tool Observation
  ↓
LLM
  ↓
Final Output
```

This provides a common execution structure for reasoning, tool use, and memory retrieval.

### `ExperimentRunner`

The experiment runner manages:

* Baseline evaluation
* Attack construction
* Memory reset
* Attack injection
* Evaluation
* Persistent-session evaluation
* Trial execution
* Result logging

---

# Evaluation Metrics

The framework evaluates both attack effectiveness and the effect attacks have on the underlying task.

## Attack Success Rate — ASR

Measures the fraction of actively attacked evaluation instances in which the attack succeeds.

```text
ASR =
successful attack instances
───────────────────────────
triggered attack instances
```

For trigger-conditioned attacks, ASR is calculated over triggered instances rather than all evaluation contexts.

---

## Persistence Rate — PR

Measures whether a persistent attack continues to influence the agent during a fresh session after active injection has been removed.

```text
PR =
successful persistent instances
──────────────────────────────
persistent evaluation instances
```

PR is therefore specifically concerned with **cross-session persistence**.

---

## Task Accuracy — TA

Measures whether the agent still completes the original task correctly.

TA is independent of whether the attack itself succeeds.

This allows the framework to distinguish:

* Successful poisoning
* General task failure
* Partial task degradation

---

## Refusal Rate — RR

Measures how frequently the agent refuses or declines to complete the task.

This helps distinguish attack-induced behavior from cases where the model simply refuses to respond.

---

## Trigger Rate — TR

For trigger-conditioned attacks, TR measures how frequently the attack condition is activated.

ASR is calculated over the triggered subset.

---

# Evaluation Methods

Attack and task success can be evaluated using:

### Rule-Based Evaluation

Composable output predicates such as:

* Substring checks
* Field-level checks
* AND / OR / NOT logic

This supports both free-form and structured outputs.

### LLM-as-a-Judge

An optional LLM evaluator can determine:

* Task correctness
* Attack success

Each evaluation context can provide a task judge specification, while attacks can provide their own judge specification.

### Hybrid Evaluation

Combines structured rule-based checks with semantic LLM-based evaluation.

---

# Memory Retrieval

Persistent experiments support configurable memory retrieval strategies.

| Mode     | Description                     |
| -------- | ------------------------------- |
| `all`    | Retrieve all memory entries     |
| `top_k`  | Retrieve the top `k` entries    |
| `by_key` | Retrieve entries matching a key |
| `random` | Randomly sample memory entries  |

These retrieval policies are controlled by the experiment configuration rather than the attack itself, allowing the same poisoned memory to be tested under different retrieval conditions.

---

# Experiment Types

## Single-Surface Experiments

Each attack surface can be evaluated independently.

This isolates the effect of poisoning a particular component while keeping the rest of the execution setup consistent.

The framework evaluates:

```text
Clean Baseline
      │
      ├── Single-Instance Attack
      │        └── ASR / TA / RR
      │
      └── Persistent Attack
               └── PR / TA / RR
```

---

## Pairwise Combined Attacks

Multiple attack surfaces can be applied to the same execution.

For each pair, the framework evaluates:

1. Attack A alone
2. Attack B alone
3. Attack A + B

This allows the combined result to be compared with the behavior of each individual attack.

The framework supports all pairwise combinations of the five attack surfaces.

---

## Full-Sweep Attacks

The framework can also apply all five attack surfaces simultaneously:

```text
Prompt
   +
Reasoning
   +
Tool Interface
   +
Memory
   +
Action Policy
   ↓
Poisoned Agent
```

This provides a broader multi-surface evaluation condition.

---

# Experiment Execution

Experiments are executed through:

```bash
python run.py <attack_type> <experiment_name> [options]
```

Example:

```bash
python run.py prompt_injection pi_small_persistent --num_trials 2
```

This:

1. Loads the `prompt_injection` attack category
2. Loads the `pi_small_persistent` experiment
3. Runs two independent trials

---

# Command Arguments

| Argument     | Description                                 |
| ------------ | ------------------------------------------- |
| `attack`     | Folder name under `experiments/benchmarks/` |
| `experiment` | Python experiment name without `.py`        |

### Optional Flags

| Flag               | Description                          | Default        |
| ------------------ | ------------------------------------ | -------------- |
| `--llm`            | LLM backend (`fake` or `real`)       | `real`         |
| `--num_trials`     | Number of independent trials         | `1`            |
| `--retrieval_mode` | Memory retrieval strategy            | `all`          |
| `--retrieval_k`    | `k` for `top_k` / `random` retrieval | `None`         |
| `--retrieval_key`  | Key for `by_key` retrieval           | `None`         |
| `--memory_path`    | Custom memory file                   | Auto-generated |
| `--output_path`    | Custom results file                  | Auto-generated |

---

# Experiment Outputs

Unless custom paths are provided, persistent memory and results are stored under:

```text
experiments/
├── memory/
│   └── <attack>/
│       └── <experiment>.json
│
└── results/
    └── <attack>/
        └── <experiment>.jsonl
```

### Memory

```text
experiments/memory/<attack>/<experiment>.json
```

### Results

```text
experiments/results/<attack>/<experiment>.jsonl
```

Results are recorded as structured JSONL records containing information such as:

* Evaluation type
* Context label
* Attack metadata
* Success indicator
* Agent output

---

# Experimental Pipeline

For a typical attack experiment:

```text
                  ┌─────────────────┐
                  │ Clean Baseline  │
                  └────────┬────────┘
                           │
                           ▼
                    Baseline Metrics
                           │
                           ▼
                  ┌─────────────────┐
                  │  Start Trial    │
                  └────────┬────────┘
                           │
                           ▼
                    Reset Memory
                           │
                           ▼
                    Build Attacks
                           │
                           ▼
                    Inject Attack
                           │
                           ▼
                  Active Agent Run
                           │
                           ├──────► ASR / TA / RR
                           │
                           ▼
                 Persistent Attack?
                     /          \
                   No            Yes
                   │              │
                   │              ▼
                   │       Store Poison
                   │       in Memory
                   │              │
                   │              ▼
                   │       Fresh Session
                   │              │
                   │              ▼
                   │           PR / TA
                   │
                   ▼
                 Results
                   │
                   ▼
             JSONL Output
```

The baseline is executed once. Attack experiments can then be repeated across independent trials, with memory reset and attack reconstruction between trials.

---

# Design Philosophy

The framework is built around several principles:

### 1. Common Interface

Different poisoning mechanisms use the same attack abstraction.

### 2. Controlled Comparison

Attack instances are manually constructed rather than independently optimized, reducing attack-generation variability.

### 3. Surface Isolation

Single-surface experiments allow individual components to be studied independently.

### 4. Composability

Multiple attacks can be applied to the same execution context.

### 5. Persistence

The framework explicitly separates immediate poisoning from cross-session memory-based influence.

### 6. Reproducibility

Experiments use consistent execution, evaluation, memory-reset, and logging procedures.

---

# Limitations and Future Work

The current study is limited to **Llama-3.1-70B-Instruct**.

Future extensions include:

* Evaluation across additional model families and scales
* More realistic tool environments
* More realistic retrieval systems
* Multi-turn agent workflows
* Additional memory architectures
* Poisoning defenses
* Memory filtering
* Tool-use validation
* Attack-aware retrieval
* Cross-surface consistency checks

These extensions would help determine which observed behaviors generalize beyond the current experimental configuration.

---

# Citation

If you use this framework in research, please cite:

```bibtex
@article{bonagura2026poisoning,
  title   = {Poisoning Attacks on LLM-Based Agents: A General Evaluation Framework},
  author  = {Bonagura, Zachary},
  year    = {2026},
  institution = {Rensselaer Polytechnic Institute}
}
```

---

# Project Status

This framework is an active research project.

Current capabilities include:

* [x] Prompt injection attacks
* [x] Reasoning manipulation
* [x] Tool interface poisoning
* [x] Memory retrieval poisoning
* [x] Action-policy poisoning
* [x] Single-instance poisoning
* [x] Persistent poisoning
* [x] Configurable memory retrieval
* [x] Rule-based evaluation
* [x] LLM-as-a-judge evaluation
* [x] Multi-trial experiments
* [x] Pairwise attack composition
* [x] Multi-surface/full-sweep evaluation
* [x] Structured JSONL results

Future work will extend the framework to additional models, environments, attack settings, and defenses.
