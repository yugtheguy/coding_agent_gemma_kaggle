from typing import Dict, Any

class SubmissionBackend:
    def submit_patch(self, patch_bytes: bytes) -> Dict[str, Any]:
        raise NotImplementedError

class FakeSubmissionBackend(SubmissionBackend):
    def __init__(self):
        self.call_count = 0
        self.last_hash = ""
    
    def submit_patch(self, patch_bytes: bytes) -> Dict[str, Any]:
        import hashlib
        import time
        self.call_count += 1
        self.last_hash = hashlib.sha256(patch_bytes).hexdigest()
        time.sleep(0.1)
        return {"status": "SUCCESS", "patch_hash": self.last_hash}

class HarnessSubmissionBackend(SubmissionBackend):
    def submit_patch(self, patch_bytes: bytes) -> Dict[str, Any]:
        raise RuntimeError("INFRA_SUBMISSION_FAILURE: HarnessSubmissionBackend unbound")
