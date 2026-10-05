import os
import sys
import json
import time
import subprocess
import traceback

def probe_environment():
    report = {
        "status": "PARTIAL",
        "timestamp": time.time(),
        "environment": {},
        "network": {},
        "gpu": {},
        "dependencies": {},
        "ports": {},
        "tools": {}
    }

    # 1. Environment variables
    report["environment"]["env_vars"] = {k: v for k, v in os.environ.items() if "KAGGLE" in k or "ADK" in k or "CUDA" in k or "VLLM" in k}
    report["environment"]["cwd"] = os.getcwd()
    report["environment"]["python_version"] = sys.version

    # 2. Filesystem
    try:
        with open("test_write.txt", "w") as f:
            f.write("test")
        report["environment"]["writable_cwd"] = True
        os.remove("test_write.txt")
    except Exception as e:
        report["environment"]["writable_cwd"] = False
        report["environment"]["write_error"] = str(e)
        
    try:
        with open("/tmp/test_write.txt", "w") as f:
            f.write("test")
        report["environment"]["writable_tmp"] = True
        os.remove("/tmp/test_write.txt")
    except Exception as e:
        report["environment"]["writable_tmp"] = False

    # 3. Network
    try:
        import urllib.request
        urllib.request.urlopen("https://github.com", timeout=3)
        report["network"]["internet"] = True
    except Exception as e:
        report["network"]["internet"] = False
        report["network"]["internet_error"] = str(e)

    # 4. GPU
    try:
        nvidia_smi = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"], text=True)
        report["gpu"]["nvidia_smi"] = nvidia_smi.strip().split("\n")
    except Exception as e:
        report["gpu"]["nvidia_smi_error"] = str(e)
        
    try:
        import torch
        report["gpu"]["torch_available"] = True
        report["gpu"]["device_count"] = torch.cuda.device_count()
        if torch.cuda.device_count() > 0:
            report["gpu"]["device_name"] = torch.cuda.get_device_name(0)
    except ImportError:
        report["gpu"]["torch_available"] = False
    except Exception as e:
        report["gpu"]["torch_error"] = str(e)

    # 5. Dependencies
    for pkg in ["google_adk", "kaggle_evaluation", "vllm", "transformers", "openai"]:
        try:
            mod = __import__(pkg)
            report["dependencies"][pkg] = True
            if hasattr(mod, "__version__"):
                report["dependencies"][pkg + "_version"] = mod.__version__
        except ImportError:
            report["dependencies"][pkg] = False

    # 6. Local Ports
    try:
        import socket
        for port in [8000, 8080, 5000]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            report["ports"][f"port_{port}"] = "open" if result == 0 else "closed"
            sock.close()
    except Exception as e:
        report["ports"]["error"] = str(e)

    # 7. ADK / Tools Inspection
    if report["dependencies"].get("google_adk", False):
        try:
            import google_adk
            report["tools"]["google_adk_dir"] = dir(google_adk)
            # Try to see if there is an active agent context or tools available
        except Exception as e:
            report["tools"]["google_adk_error"] = str(e)
            
    if report["dependencies"].get("kaggle_evaluation", False):
        try:
            import kaggle_evaluation
            report["tools"]["kaggle_evaluation_dir"] = dir(kaggle_evaluation)
        except Exception as e:
            report["tools"]["kaggle_evaluation_error"] = str(e)

    # Save report
    os.makedirs("artifacts/stage14", exist_ok=True)
    with open("artifacts/stage14/runtime_validation.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print("Stage 14 validation completed. Artifact saved to artifacts/stage14/runtime_validation.json")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    probe_environment()
