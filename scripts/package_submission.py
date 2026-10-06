import os
import zipfile
import shutil
from pathlib import Path

def package_submission():
    root_dir = Path(__file__).resolve().parent.parent
    submission_dir = root_dir / "submission_e00"
    
    agent_yaml = submission_dir / "agent.yaml"
    if not agent_yaml.exists():
        raise FileNotFoundError("agent.yaml must exist inside submission_e00 directory")

    zip_path = root_dir / "submission.zip"
    
    print(f"Packaging submission from {submission_dir}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(submission_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(submission_dir)
                zf.write(file_path, arcname)
                print(f"Added: {arcname}")
                
    zip_size = zip_path.stat().st_size
    print(f"Successfully generated submission.zip. Size: {zip_size} bytes.")
    
    # Verify the zip root
    with zipfile.ZipFile(zip_path, 'r') as zf:
        root_files = {Path(p).parts[0] for p in zf.namelist()}
        print(f"Zip root contains: {root_files}")
        if "agent.yaml" not in root_files:
            print("ERROR: agent.yaml is not at the root of the zip archive!")
        if "submission_e00" in root_files:
            print("ERROR: submission_e00 directory found at the root, contents were not packaged correctly.")

if __name__ == "__main__":
    package_submission()
