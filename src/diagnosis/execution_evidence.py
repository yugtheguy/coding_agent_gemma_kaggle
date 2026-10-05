from dataclasses import dataclass, field
from typing import List, Optional
import re

@dataclass
class ExecutionEvidence:
    command: str
    exit_code: int
    duration_seconds: float
    timed_out: bool
    result_type: str  
    salient_output: str
    traceback_summary: str = ""
    failing_test: str = ""
    failure_location: str = ""
    observed_behavior: str = ""
    supports_hypothesis: Optional[str] = None
    contradicts_hypothesis: Optional[str] = None
    artifact_ref: str = ""

def extract_traceback_signal(output: str) -> str:
    tb_lines = []
    in_tb = False
    lines = output.split('\n')
    for line in lines:
        if "Traceback (most recent call last):" in line:
            in_tb = True
            tb_lines.append(line)
        elif in_tb:
            tb_lines.append(line)
            if line and not line.startswith(" ") and ("Error:" in line or "Exception:" in line):
                break
    
    if tb_lines:
        return "\n".join(tb_lines[-6:])
    
    exceptions = [line for line in lines if ("Error:" in line or "Exception:" in line) and not line.startswith(" ")]
    if exceptions:
        return exceptions[-1]
        
    return ""

def extract_salient_output(output: str) -> str:
    lines = output.split('\n')
    if len(lines) <= 20:
        return output
        
    salient = []
    salient.extend(lines[:5])
    salient.append("... [truncated] ...")
    
    failures = []
    in_failure = False
    for line in lines:
        if "FAILURES" in line and "===" in line:
            in_failure = True
        elif in_failure and "===" in line and "summary info" in line:
            in_failure = False
            
        if in_failure:
            failures.append(line)
            
    if failures:
        salient.extend(failures[:30]) 
        if len(failures) > 30:
            salient.append("... [truncated failures] ...")
            
    if not failures:
        # just grab the traceback lines if present
        tb = extract_traceback_signal(output)
        if tb:
            salient.extend(tb.split('\n'))
            
    salient.extend(lines[-5:])
    return "\n".join(salient)
