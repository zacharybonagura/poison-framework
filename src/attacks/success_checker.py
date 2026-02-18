from typing import Callable, Optional, Any

# A success checker returns True if the attack "succeeded" on this output.
SuccessChecker = Callable[[str],bool]

def contains(text: str) -> SuccessChecker:
    t = text.lower()
    return lambda output: t in output.lower()

def contains_any(texts: list[str]) -> SuccessChecker:
    lowered = [t.lower() for t in texts]
    return lambda output: any(t in output.lower() for t in lowered)

def excludes(markers: list[str]) -> SuccessChecker:
    lowered = [m.lower() for m in markers]
    return lambda output: not any(m in output.lower() for m in lowered)

def AND(*checkers: SuccessChecker) -> SuccessChecker:
    return lambda output: all(c(output) for c in checkers)

def OR(*checkers: SuccessChecker) -> SuccessChecker:
    return lambda output: any(c(output) for c in checkers)

def NOT(checker: SuccessChecker) -> SuccessChecker:
    return lambda output: not checker(output)