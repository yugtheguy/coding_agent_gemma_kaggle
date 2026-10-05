import subprocess
import hashlib
import time

def extract_patch(timeout_seconds: int = 180) -> dict:
    start = time.time()
    try:
        res = subprocess.run(["git", "diff"], capture_output=True, timeout=timeout_seconds, text=False)
        duration = time.time() - start
        if res.returncode != 0:
            return {"status": "INFRA_PATCH_EXTRACTION_FAILURE", "duration": duration}
            
        patch_bytes = res.stdout
        if not patch_bytes:
            return {"status": "PATCH_EMPTY", "duration": duration}
            
        patch_hash = hashlib.sha256(patch_bytes).hexdigest()
        return {
            "status": "SUCCESS",
            "patch_bytes": patch_bytes,
            "patch_hash": patch_hash,
            "duration": duration,
            "files_changed": len([line for line in patch_bytes.split(b"\n") if line.startswith(b"diff --git")])
        }
    except subprocess.TimeoutExpired:
        return {"status": "INFRA_PATCH_EXTRACTION_TIMEOUT", "duration": time.time() - start}
