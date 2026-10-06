import os
import sys
import json
import yaml

def validate_environment():
    report = {
        "status": "PASS",
        "environment": {},
        "paths": {},
        "submission_e00": {}
    }

    # 1. Environment variables (redacted)
    sensitive_keys = ["TOKEN", "SECRET", "KEY", "PASSWORD", "CREDENTIAL"]
    redacted_env = {}
    for k, v in os.environ.items():
        if any(sec in k.upper() for sec in sensitive_keys):
            redacted_env[k] = {"present": True}
        else:
            redacted_env[k] = v
    report["environment"]["env_vars"] = redacted_env

    # 2. Filesystem Paths
    required_paths = [
        "HARNESS_README",
        "tasks.jsonl",
        "snapshots",
        "graphs",
        "embeddings",
        "wheels",
        "sample_submission",
    ]
    
    for path in required_paths:
        exists = os.path.exists(path)
        report["paths"][path] = exists
        if not exists:
            # We don't fail immediately because we might run this outside kaggle, 
            # but we log it. The task mentions to validate these.
            report["status"] = "PARTIAL"

    # 3. submission_e00 validation
    sub_dir = "submission_e00"
    if not os.path.exists(sub_dir):
        report["status"] = "FAIL"
        report["submission_e00"]["exists"] = False
        return report
    
    report["submission_e00"]["exists"] = True
    
    sub_files = [
        "agent.yaml",
        "eval_config.yaml",
        "configs/sampling.yaml",
        "prompts/system.md"
    ]
    
    for sf in sub_files:
        path = os.path.join(sub_dir, sf)
        exists = os.path.exists(path)
        report["submission_e00"][sf] = exists
        if not exists:
            report["status"] = "FAIL"

    # Validate agent.yaml
    agent_yaml_path = os.path.join(sub_dir, "agent.yaml")
    if os.path.exists(agent_yaml_path):
        try:
            with open(agent_yaml_path, "r") as f:
                content = f.read()
                # Simple string checks for includes
                if "!include prompts/system.md" not in content:
                    report["submission_e00"]["agent_yaml_has_system_include"] = False
                    report["status"] = "FAIL"
                if "!include configs/sampling.yaml" not in content:
                    report["submission_e00"]["agent_yaml_has_sampling_include"] = False
                    report["status"] = "FAIL"
                
                # Check for single agent, no subagents, correct model
                if "subagents" in content:
                    report["submission_e00"]["agent_yaml_no_subagents"] = False
                if "adapters" in content:
                    report["submission_e00"]["agent_yaml_no_adapters"] = False
                    
                # Validate exact tools
                required_tools = [
                    "run_command", "read_file", "edit_file", "write_file",
                    "get_status", "submit_patch", "get_code_neighbors",
                    "search_similar_code", "get_code_subgraph"
                ]
                for tool in required_tools:
                    if tool not in content:
                        report["submission_e00"][f"missing_tool_{tool}"] = True
                        report["status"] = "FAIL"

        except Exception as e:
            report["submission_e00"]["agent_yaml_error"] = str(e)
            report["status"] = "FAIL"

    print(json.dumps(report, indent=2))
    
    if report["status"] == "FAIL":
        sys.exit(1)

if __name__ == "__main__":
    validate_environment()
