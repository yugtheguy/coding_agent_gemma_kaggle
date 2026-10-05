def is_protected(path: str) -> bool:
    protected = ["agent.yaml", "experiments/", "tests/test_", ".github/", "harness/"]
    for p in protected:
        if p in path.replace("\\", "/"):
            return True
    return False

def is_test_file(path: str) -> bool:
    p = path.replace("\\", "/")
    return "test" in p.lower() or "tests/" in p
