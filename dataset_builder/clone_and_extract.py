import os
import shutil
import subprocess
from urllib.parse import urlparse
import sys
import typing

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config # type: ignore


def clone_repository(repo_url, target_dir):
    """Clones a git repository into the target directory."""
    repo_name = os.path.basename(urlparse(repo_url).path).replace(".git", "")
    repo_path = os.path.join(target_dir, repo_name)

    if os.path.exists(repo_path):
        print(f"[*] Repository {repo_name} already cloned.")
        return repo_path

    print(f"[*] Cloning {repo_url} into {repo_path}...")
    try:
        # Using shallow clone to save time and disk space, we only need the code
        subprocess.run(["git", "clone", "--depth", "1", repo_url, repo_path], check=True)
        print(f"[+] Successfully cloned {repo_name}")
        return repo_path
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to clone {repo_url}: {e}")
        return None

def should_ignore(path_parts):
    """Check if any part of the path matches our ignore list."""
    for part in path_parts:
        # Exact matching for common test/doc folders or starts with test_
        if part.lower() in config.IGNORE_PATHS or part.lower().startswith("test_"):
            return True
    return False

def extract_python_files(repo_path, output_dir):
    """
    Extracts all .py files from repo_path and copies them to output_dir.
    Files are prefixed with the original relative path to maintain uniqueness.
    """
    repo_name = os.path.basename(repo_path)
    count = 0

    for root, dirs, files in os.walk(repo_path):
        # Calculate relative path components
        rel_path = os.path.relpath(root, repo_path)
        path_parts = rel_path.split(os.sep) if rel_path != "." else []
        
        # Skip hidden directories like .git
        # Use clear and extend to satisfy the linter instead of slice assignment
        filtered_dirs = [d for d in dirs if not d.startswith('.')]
        dirs.clear()
        dirs.extend(filtered_dirs)

        # Skip if in ignored path
        if should_ignore(path_parts):
            continue

        for file in files:
            if file.endswith(".py"):
                # Skip __init__.py and setup.py as they usually don't contain smells relevant to core logic
                if file in ["__init__.py", "setup.py"]:
                    continue

                source_file = os.path.join(root, file)
                
                # Construct a flat filename: repoName_folder1_folder2_filename.py
                prefix = "_".join(path_parts) if path_parts else ""
                if prefix:
                    safe_name = f"{repo_name}_{prefix}_{file}"
                else:
                    safe_name = f"{repo_name}_{file}"
                
                dest_file = os.path.join(output_dir, safe_name)
                
                try:
                    shutil.copy2(source_file, dest_file)
                    count = int(typing.cast(int, count) + 1)
                except Exception as e:
                    print(f"[-] Error copying {source_file}: {e}")

    print(f"[+] Extracted {count} Python files from {repo_name}")
    return count

def main():
    total_files: int = 0
    print("Starting Dataset Collection Phase Phase 1...")
    
    for repo_url in config.REPOSITORIES:
        repo_path = clone_repository(repo_url, config.REPOS_DIR)
        if repo_path:
            num_files = extract_python_files(repo_path, config.PYTHON_CODE_DIR)
            total_files = int(typing.cast(int, total_files) + num_files)
            
    print(f"\n[=] Dataset collection complete.")
    print(f"[=] Total Python files extracted: {total_files}")
    print(f"[=] Files saved in: {config.PYTHON_CODE_DIR}")

if __name__ == "__main__":
    main()
