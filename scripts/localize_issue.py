import argparse
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.localization.anchor_patterns import extract_anchors
from src.localization.ranking import run_localization

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--issue-file", required=True)
    args = parser.parse_args()
    
    with open(args.issue_file, "r") as f:
        issue = f.read()
        
    print("Extracting anchors...")
    anchors = extract_anchors(issue)
    
    print("\nANCHORS:")
    for a in anchors.anchors:
        print(f"  {a.anchor_type.name}: {a.normalized_value} ({a.confidence.name})")
        
    print("\nRunning localization...")
    result = run_localization(anchors, Path(args.repo))
    
    print(f"\nCONFIDENCE: {result.confidence.name}")
    print("\nTOP FILES:")
    for fc in result.file_candidates:
        print(f"  [{fc.rank}] {fc.path} (score: {fc.score:.1f}, {fc.file_type.name})")
        
    print("\nTOP SYMBOLS:")
    for sc in result.symbol_candidates:
        print(f"  {sc.qualified_name} @ {sc.path}:{sc.line_start} (score: {sc.score:.1f}, {sc.symbol_kind})")
        
    print("\nFOCUSED READS:")
    for fr in result.focused_reads:
        print(f"  {fr.path}:{fr.line_start}-{fr.line_end} ({fr.reason})")
        
    print(f"\nSTATS: {json.dumps(result.stats, indent=2)}")

if __name__ == "__main__":
    main()
