import os
import subprocess
import json
import ast
import re
import sys

import typing
from typing import Any, Dict, List

# Add local python scripts path if not on PATH
scripts_path = os.path.join(os.environ["APPDATA"], "Python", "Python313", "Scripts")
if scripts_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + scripts_path

def run_bandit(target_path):
    """
    Runs Bandit security linter on the target path.
    Returns a list of vulnerability records.
    """
    try:
        # Run bandit with JSON output
        # -r: recursive
        # -f json: format
        # Use full module path to be safer
        python_exe = sys.executable
        result = subprocess.run(
            [python_exe, "-m", "bandit", "-r", target_path, "-f", "json"],
            capture_output=True, text=True, check=False
        )
        
        if not result.stdout.strip():
            if result.stderr:
                print(f"[!] Bandit stderr: {result.stderr.strip()}")
            return []
            
        try:
            # Ensure output is a string and handle potential decoding issues
            stdout_str = str(result.stdout) if result.stdout else ""
            data = json.loads(stdout_str)
        except json.JSONDecodeError as je:
            # Explicitly cast to string and check length for safe reporting
            err_msg: str = str(stdout_str)
            # Use type: ignore for slicing if the linter is being stubborn about SupportsIndex
            truncated_stdout = err_msg if len(err_msg) < 200 else err_msg[:200]  # type: ignore
            print(f"[!] Failed to parse Bandit JSON: {je}. Output was: {truncated_stdout}...")
            return []

        vulnerabilities = []
        
        for issue in data.get("results", []):
            vulnerabilities.append({
                "file": issue.get("filename"),
                "line": issue.get("line_number"),
                "issue_text": issue.get("issue_text"),
                "issue_severity": issue.get("issue_severity"),
                "issue_confidence": issue.get("issue_confidence"),
                "test_id": issue.get("test_id")
            })
        return vulnerabilities
    except Exception as e:
        print(f"[-] Bandit check failed: {e}")
        return []

def scan_for_secrets(filepath):
    """Simple regex based check for hardcoded secrets/passwords."""
    secret_patterns = {
        "Hardcoded Password": r"(password|passwd|pwd|secret|key|token)\s*=\s*['\"][\w\d]{6,}['\"]",
        "AWS Key": r"AKIA[0-9A-Z]{16}",
        "Generic API Key": r"[a-zA-Z0-9]{32,}"
    }
    
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                for name, pattern in secret_patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        findings.append({
                            "file": filepath,
                            "line": i,
                            "issue_text": f"Potential {name} detected",
                            "issue_severity": "HIGH",
                            "issue_confidence": "MEDIUM"
                        })
    except Exception:
        pass
    return findings

def scan_for_structural_smells(filepath):
    """AST-based scan for structural patterns like deep nesting and magic values."""
    smells = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code)
        
        # Add parent references
        parents: dict = {}
        for p in ast.walk(tree):
            for c in ast.iter_child_nodes(p):
                parents[c] = p

        for node in ast.walk(tree):
            # 1. Deep Nesting
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                depth: int = 0
                curr = node
                while curr is not None and parents.get(curr) is not None:
                    if isinstance(curr, (ast.If, ast.For, ast.While, ast.Try)):
                        depth = int(typing.cast(int, depth) + 1)
                    curr = parents.get(curr)
                
                if depth > 4:
                    smells.append({
                        "file": filepath,
                        "line": getattr(node, 'lineno', 0),
                        "issue_text": f"Deeply nested logic detected (depth: {depth})",
                        "issue_severity": "MEDIUM",
                        "issue_confidence": "HIGH"
                    })
            
            # 2. Magic Values (in logic and assignments)
            if isinstance(node, ast.Constant):
                # Check for numbers and strings (excluding common defaults)
                val = node.value
                is_magic = False
                if isinstance(val, (int, float)) and val not in [0, 1, -1]:
                    is_magic = True
                elif isinstance(val, str) and val.strip() not in ["", "utf-8", "ascii"]:
                    # Heuristic: avoid flagging docstrings or very short strings
                    if len(val) > 1 and not (val.startswith('__') and val.endswith('__')):
                        is_magic = True
                
                if is_magic:
                    parent_node = parents.get(node)
                    # Detect in comparisons, binary ops, and assignments
                    if isinstance(parent_node, (ast.Compare, ast.BinOp, ast.Assign, ast.AnnAssign)):
                        # If it's an assignment, check if it's to an uppercase constant (which is okay)
                        is_constant_def = False
                        if isinstance(parent_node, (ast.Assign, ast.AnnAssign)):
                            targets = getattr(parent_node, 'targets', [getattr(parent_node, 'target', None)])
                            for target in targets:
                                if isinstance(target, ast.Name) and target.id.isupper():
                                    is_constant_def = True
                                    break
                        
                        if not is_constant_def:
                            type_str = "number" if isinstance(val, (int, float)) else "string"
                            smells.append({
                                "file": filepath,
                                "line": getattr(node, 'lineno', 0),
                                "issue_text": f"Magic {type_str} '{val}' detected",
                                "issue_severity": "LOW",
                                "issue_confidence": "HIGH"
                            })
    except Exception:
        pass
    return smells

def security_scan(target_path):
    """Combines automated tools and manual structural checks."""
    print(f"[*] Starting security scan on: {target_path}")
    
    # Tool-based check
    bandit_results = run_bandit(target_path)
    
    # Pattern-based check
    pattern_findings = []
    if os.path.isfile(target_path):
        pattern_findings.extend(scan_for_secrets(target_path))
        pattern_findings.extend(scan_for_structural_smells(target_path))
    elif os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".py"):
                    full_p = os.path.join(root, file)
                    pattern_findings.extend(scan_for_secrets(full_p))
                    pattern_findings.extend(scan_for_structural_smells(full_p))
                    
    all_results = bandit_results + pattern_findings
    print(f"[+] Security scan complete. Found {len(all_results)} issues.")
    return all_results

if __name__ == "__main__":
    # Test on the current directory
    results = security_scan(".")
    if isinstance(results, list):
        count = 0
        for res in results:
            if count >= 5: break
            print(f"[{res['issue_severity']}] {res['file']}:{res['line']} - {res['issue_text']}")
            count += 1
