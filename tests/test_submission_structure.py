import os
from pathlib import Path
import subprocess
import zipfile

def test_agent_yaml_exists():
    root_dir = Path(__file__).resolve().parent.parent
    agent_yaml = root_dir / "agent.yaml"
    assert agent_yaml.exists(), "agent.yaml missing"

def test_agent_yaml_structure():
    root_dir = Path(__file__).resolve().parent.parent
    with open(root_dir / "agent.yaml", "r") as f:
        content = f.read()
    
    assert "gemma-4-31b-it-qat-w4a16-ct" in content, "Missing mandatory model name"
    assert "subagents" in content, "Subagent config missing"
    assert "adapters" in content, "Adapters config missing"
    assert "!include prompts/system_e00.md" in content, "Prompt include missing"
    assert "!include configs/sampling.yaml" in content, "Configuration include missing"

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
        assert ".git" not in namelist, "Prohibited files included"
        # Validate that the directories we expect are somewhat represented, though namelist might just list files
        files_only = [f for f in namelist if not f.endswith('/')]
        assert "agent.yaml" in files_only
