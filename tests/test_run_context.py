from src.infrastructure.run_context import create_run_context

def test_run_context_deterministic():
    config = {"a": 1, "b": 2}
    prompt = "hello"
    ctx1 = create_run_context("E00", "v1", config, prompt)
    ctx2 = create_run_context("E00", "v1", config, prompt)
    assert ctx1.config_hash == ctx2.config_hash
    assert ctx1.prompt_hash == ctx2.prompt_hash

def test_run_context_different():
    ctx1 = create_run_context("E00", "v1", {"a": 1}, "hello")
    ctx2 = create_run_context("E00", "v1", {"a": 2}, "hello")
    assert ctx1.config_hash != ctx2.config_hash
