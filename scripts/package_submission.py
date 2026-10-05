import os
import zipfile
import shutil
from pathlib import Path

def package_submission():
    root_dir = Path(__file__).resolve().parent.parent
    agent_yaml = root_dir / "agent.yaml"
    
    if not agent_yaml.exists():
        raise FileNotFoundError("agent.yaml must exist at the archive root")

    staging_dir = root_dir / "staging_submission"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()

    # Allowed directories and files
    allowed_files = ["agent.yaml", "requirements.txt"]
    allowed_dirs = ["configs", "prompts"]

    print("Packaging submission...")
    
    try:
        for f in allowed_files:
            src = root_dir / f
            if src.exists():
                shutil.copy2(src, staging_dir / f)
                print(f"Included file: {f}")
        
        for d in allowed_dirs:
            src = root_dir / d
            if src.exists():
                shutil.copytree(src, staging_dir / d)
                print(f"Included directory: {d}")

        zip_path = root_dir / "submission.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(staging_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(staging_dir)
                    zf.write(file_path, arcname)
                    
        zip_size = zip_path.stat().st_size
        print(f"Successfully generated submission.zip. Size: {zip_size} bytes.")
        
    finally:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)

if __name__ == "__main__":
    package_submission()
