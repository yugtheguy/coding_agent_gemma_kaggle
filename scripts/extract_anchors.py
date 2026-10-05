import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.localization.anchor_patterns import extract_anchors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", default="")
    parser.add_argument("--file", type=str)
    args = parser.parse_args()
    
    text = ""
    if args.file:
        with open(args.file, "r") as f:
            text = f.read()
    else:
        text = args.text
        
    anchors = extract_anchors(text)
    
    for a in anchors.anchors:
        print(f"[{a.confidence.name}] {a.anchor_type.name}: {a.normalized_value}")
        
    print("\n" + anchors.to_search_plan())

if __name__ == "__main__":
    main()
