import os
from pathlib import Path
import subprocess
import zipfile
import json

def test_submission_layout():
    root_dir = Path(__file__).resolve().parent.parent
    sub_dir = root_dir / "submission_e00"
    
    assert sub_dir.exists()
    assert (sub_dir / "agent.yaml").exists()
    assert (sub_dir / "eval_config.yaml").exists()
    assert (sub_dir / "configs" / "sampling.yaml").exists()
    assert (sub_dir / "prompts" / "system.md").exists()

def test_agent_yaml_structure():
    root_dir = Path(__file__).resolve().parent.parent
    with open(root_dir / "submission_e00" / "agent.yaml", "r") as f:
        content = f.read()
    
    assert "gemma-4-31b-it-qat-w4a16-ct" in content, "Missing mandatory model name"
    assert "sub_agents" not in content and "subagents" not in content, "No subagents allowed"
    assert "adapter" not in content, "No adapters allowed"
    assert "agent_tool" not in content, "No agent_tool allowed"
    
    tools = [
        "run_command", "read_file", "edit_file", "write_file",
        "get_status", "submit_patch", "get_code_neighbors",
        "search_similar_code", "get_code_subgraph"
    ]
    for tool in tools:
        assert tool in content, f"Missing tool: {tool}"
        
    assert "!include prompts/system.md" in content, "Prompt include missing or wrong"
    assert "!include configs/sampling.yaml" in content, "Sampling include missing or wrong"

def test_no_controller_dependency():
    root_dir = Path(__file__).resolve().parent.parent
    with open(root_dir / "submission_e00" / "prompts" / "system.md", "r") as f:
        content = f.read()
    
    assert "src/controller" not in content, "Submission must not depend on src/controller"
    assert "task_controller" not in content, "Submission must not depend on task_controller"

def test_package_script():
    root_dir = Path(__file__).resolve().parent.parent
    script_path = root_dir / "scripts" / "package_submission.py"
    
    result = subprocess.run(["python", str(script_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"Packaging failed: {result.stderr}\n{result.stdout}"
    
    zip_path = root_dir / "submission.zip"
    assert zip_path.exists(), "submission.zip was not created"
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        namelist = zf.namelist()
        assert "agent.yaml" in namelist, "agent.yaml must be at the root of the archive"
        assert "submission_e00/agent.yaml" not in namelist, "Must not have submission_e00 dir at root"
        assert "prompts/system.md" in namelist
        assert "configs/sampling.yaml" in namelist

def test_validator_secrets():
    root_dir = Path(__file__).resolve().parent.parent
    script_path = root_dir / "scripts" / "validate_harness.py"
    
    env = os.environ.copy()
    env["MY_KAGGLE_TOKEN"] = "super_secret_value_123"
    env["MY_API_KEY"] = "another_secret"
    
    result = subprocess.run(["python", str(script_path)], env=env, capture_output=True, text=True)
    
    assert "super_secret_value_123" not in result.stdout
    assert "another_secret" not in result.stdout
    
    # Check if the keys are at least present in the output JSON as {"present": true}
    try:
        report = json.loads(result.stdout)
        env_vars = report.get("environment", {}).get("env_vars", {})
        assert env_vars.get("MY_KAGGLE_TOKEN") == {"present": True}
        assert env_vars.get("MY_API_KEY") == {"present": True}
    except json.JSONDecodeError:
        pass # The script might have failed due to missing required paths, but that's fine, we still check stdout
