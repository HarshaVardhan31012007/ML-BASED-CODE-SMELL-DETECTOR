import os
import json
import subprocess
import ast
import sys
import re
import multiprocessing
import warnings

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config # type: ignore

# Add local python scripts path if not on PATH
scripts_path = os.path.join(os.environ.get("APPDATA", ""), "Python", "Python313", "Scripts")
if scripts_path and scripts_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + scripts_path

class DeadCodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.defined = set()
        self.used = set()
        
    def visit_FunctionDef(self, node):
        self.defined.add(node.name)
        self.generic_visit(node)
        
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used.add(node.id)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.used.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.used.add(node.func.attr)
        self.generic_visit(node)

class RuleBasedLabeler(ast.NodeVisitor):
    def __init__(self, source_lines):
        self.source_lines = source_lines
        self.smells = []
        self.current_function = None
        self.current_class = None
        self.hashes = {} # For Duplicate Code
        
    def visit_FunctionDef(self, node):
        # 9. Long Methods (> 50 lines per expert spec)
        length = node.end_lineno - node.lineno
        if length > 50:
            self.smells.append({
                "line": node.lineno,
                "smell_type": config.SMELL_CATEGORIES["LONG_METHOD"],
                "message": f"Method '{node.name}' exceeds 50 lines ({length})",
                "severity": "Warning"
            })
            
        # 10. Duplicate Code (AST-based hashing)
        node_str = ast.dump(node)
        node_hash = hash(node_str)
        if node_hash in self.hashes:
            self.smells.append({
                "line": node.lineno,
                "smell_type": config.SMELL_CATEGORIES["DUPLICATE_CODE"],
                "message": f"Duplicate logic found in method '{node.name}'",
                "severity": "Warning"
            })
        self.hashes[node_hash] = node.name

        # 6. Missing Authentication (Routes without login decorators)
        is_route = any(isinstance(d, ast.Call) and getattr(d.func, 'attr', '') == 'route' for d in node.decorator_list)
        if is_route:
            has_auth = any(
                (isinstance(d, ast.Name) and "login" in d.id.lower()) or
                (isinstance(d, ast.Call) and "login" in getattr(d.func, 'id', '').lower())
                for d in node.decorator_list
            )
            if not has_auth:
                self.smells.append({
                    "line": node.lineno,
                    "smell_type": config.SMELL_CATEGORIES["MISSING_AUTH"],
                    "message": f"Route '{node.name}' might be missing authentication",
                    "severity": "Error"
                })

        self.current_function = node
        self.generic_visit(node)
        self.current_function = None

    def visit_ClassDef(self, node):
        # 11. God Class (> 20 methods)
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > 20:
            self.smells.append({
                "line": node.lineno,
                "smell_type": config.SMELL_CATEGORIES["GOD_CLASS"],
                "message": f"God Class '{node.name}' has {len(methods)} methods",
                "severity": "Warning"
            })
        self.generic_visit(node)

    def visit_Try(self, node):
        # 7. Improper Error Handling
        for handler in node.handlers:
            if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                self.smells.append({
                    "line": handler.lineno,
                    "smell_type": config.SMELL_CATEGORIES["IMPROPER_ERROR_HANDLING"],
                    "message": "Empty except: pass block",
                    "severity": "Warning"
                })
        self.generic_visit(node)

    def visit_Call(self, node):
        # 4. Unsafe API Usage
        if isinstance(node.func, ast.Name) and node.func.id in ['eval', 'exec']:
            self.smells.append({
                "line": node.lineno,
                "smell_type": config.SMELL_CATEGORIES["UNSAFE_API"],
                "message": f"Unsafe API '{node.func.id}' used",
                "severity": "Error"
            })
        
        # 2/5. Unvalidated Input / Missing Sanitization
        is_request = False
        if isinstance(node.func, ast.Attribute):
            if "request" in ast.dump(node.func):
                is_request = True
        
        # Sinks: execute, pipe, open, eval
        sink_methods = ['execute', 'popen', 'system', 'open', 'eval', 'exec', 'cursor.execute']
        method_name = ""
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            method_name = node.func.id

        if str(method_name) in sink_methods:
             for arg in node.args:
                 # Check for string concatenation or f-strings in sinks
                 if isinstance(arg, (ast.BinOp, ast.JoinedStr)):
                     self.smells.append({
                        "line": getattr(node, 'lineno', 0),
                        "smell_type": config.SMELL_CATEGORIES["SQL_INJECTION"] if "execute" in str(method_name) else config.SMELL_CATEGORIES["MISSING_SANITIZATION"],
                        "message": f"Potential unsanitized input in {method_name}()",
                        "severity": "Error"
                    })

        # 8. Insecure File Handling
        if method_name == 'open' or method_name == 'chmod':
            # Check for overly permissive modes
            for keyword in node.keywords:
                if keyword.arg == 'mode' and isinstance(keyword.value, ast.Constant):
                    if 'w' in str(keyword.value.value) and '+' in str(keyword.value.value):
                         self.smells.append({
                            "line": node.lineno,
                            "smell_type": config.SMELL_CATEGORIES["INSECURE_FILE_HANDLING"],
                            "message": "Permissive file opening mode detected",
                            "severity": "Warning"
                        })
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                if node.args[1].value == 0o777:
                    self.smells.append({
                        "line": node.lineno,
                        "smell_type": config.SMELL_CATEGORIES["INSECURE_FILE_HANDLING"],
                        "message": "Insecure file permissions (777) detected",
                        "severity": "Error"
                    })

        self.generic_visit(node)

    def visit_Constant(self, node):
        # 13. Magic Strings & Numbers
        if isinstance(node.value, (int, float, str)) and node.value not in [0, 1, -1, "", None, True, False]:
            self.smells.append({
                "line": node.lineno,
                "smell_type": config.SMELL_CATEGORIES["MAGIC_VALUE"],
                "message": f"Magic value '{node.value}'",
                "severity": "Warning"
            })
        self.generic_visit(node)

def run_bandit(filepath):
    """Run Bandit to detect security smells."""
    try:
        # Try running as module first (avoid path issues)
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", "-q", filepath],
            capture_output=True, text=True, check=False
        )
        if result.returncode != 0 and not result.stdout.strip():
            # Fallback to direct call
            result = subprocess.run(
                ["bandit", "-f", "json", "-q", filepath],
                capture_output=True, text=True, check=False
            )
        
        if not result.stdout.strip():
            return []
        data = json.loads(result.stdout)
        smells = []
        for issue in data.get("results", []):
            mapped_type = config.SMELL_CATEGORIES["UNSAFE_API"]
            if "SQL" in issue["issue_text"]:
                mapped_type = config.SMELL_CATEGORIES["SQL_INJECTION"]
            elif "credential" in issue["issue_text"].lower() or "password" in issue["issue_text"].lower():
                mapped_type = config.SMELL_CATEGORIES["HARDCODED_CREDENTIALS"]
            
            smells.append({
                "line": issue["line_number"],
                "smell_type": mapped_type,
                "message": issue["issue_text"],
                "severity": issue["issue_severity"]
            })
        return smells
    except:
        return []

def scan_for_magic_values(source_code):
    """Regex based detection for magic strings and numbers."""
    smells = []
    # Match assignment of literal to non-uppercase variable
    # or literal in binary op
    lines = source_code.splitlines()
    for i, line in enumerate(lines, 1):
        if re.search(r'[^A-Z_0-9\s]\s*=\s*(["\'].+?["\']|\d+)', line):
            if not any(kw in line for kw in ['return', 'if', 'while', 'print']):
                 smells.append({
                    "line": i,
                    "smell_type": config.SMELL_CATEGORIES["MAGIC_VALUE"],
                    "message": "Potential magic string or number",
                    "severity": "Warning"
                })
    return smells

def label_file(filepath):
    """Analyze a single file and return structured dataset records."""
    # Suppress syntax warnings from data-level issues in analyzed files
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
            f.seek(0)
            source_lines = f.readlines()
            
        tree = ast.parse(source_code)
        
        # Add parent references for context-aware labeling (Fixed implementation)
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                setattr(child, 'parent_node', node)
                
        labeler = RuleBasedLabeler(source_lines)
        
        # Specific check for nesting level (Refined logic)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                max_d = 0
                for sub in ast.walk(node):
                    if isinstance(sub, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                        d = 0
                        curr = sub
                        while curr != node:
                            if isinstance(curr, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                                d += 1
                            
                            parent = getattr(curr, 'parent_node', None)
                            if parent:
                                curr = parent
                            else:
                                break
                        max_d = max(max_d, d)
                if max_d > 3:
                    labeler.smells.append({
                        "line": getattr(node, 'lineno', 0),
                        "smell_type": config.SMELL_CATEGORIES["DEEP_NESTING"],
                        "message": f"Method '{getattr(node, 'name', 'unknown')}' nesting depth: {max_d}",
                        "severity": "Warning"
                    })

        # Dead Code Detection
        dead_visitor = DeadCodeVisitor()
        dead_visitor.visit(tree)
        unused = dead_visitor.defined - dead_visitor.used
        for item in unused:
             # Basic check to avoid flagging standard dunder methods or common overrides
             if not item.startswith('__'):
                 labeler.smells.append({
                    "line": 1, # Placeholder for module level or first def
                    "smell_type": config.SMELL_CATEGORIES["DEAD_CODE"],
                    "message": f"Potential dead code: '{item}' is defined but not used",
                    "severity": "Warning"
                })

        labeler.visit(tree)
        bandit_smells = run_bandit(filepath)
        magic_smells = scan_for_magic_values(source_code)
        
        all_smells = labeler.smells + bandit_smells + magic_smells
        
        dataset_records = []
        for smell in all_smells:
            # Ensure line is int
            l_num = int(smell.get("line", 1))
            line_idx = l_num - 1
            start_line = max(0, line_idx - 5)
            end_line = min(len(source_lines), line_idx + 6)
            
            # Use explicit list slicing for compatibility
            snippet_lines = [source_lines[i] for i in range(start_line, end_line)]
            code_snippet = "".join(snippet_lines)
            
            record = {
                "file_path": os.path.basename(filepath),
                "code_snippet": code_snippet.strip(),
                "smell_type": smell["smell_type"],
                "severity": smell["severity"],
                "line": l_num
            }
            dataset_records.append(record)
            
        if not all_smells:
            # Use manual slicing to ensure compatibility with all list types
            snippet_lines = [source_lines[i] for i in range(min(10, len(source_lines)))]
            record = {
                "file_path": os.path.basename(filepath),
                "code_snippet": "".join(snippet_lines).strip(),
                "smell_type": config.SMELL_CATEGORIES["CLEAN"],
                "severity": "None",
                "line": 0
            }
            dataset_records.append(record)
            
        return dataset_records
    except Exception as e:
        return []

def main():
    print("[*] Starting Phase 2: Production-Grade Code Smell Labeling...")
    all_records = []
    
    if not os.path.exists(config.PYTHON_CODE_DIR):
        print("[-] Python code directory not found. Run 'setup' first.")
        return

    files = [os.path.join(config.PYTHON_CODE_DIR, f) for f in os.listdir(config.PYTHON_CODE_DIR) if f.endswith('.py')]
    if not files:
        print("[-] No files to label.")
        return

    print(f"[*] Found {len(files)} files to process.")
    
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        for records in pool.imap_unordered(label_file, files):
            all_records.extend(records)
            if len(all_records) % 100 == 0:
                print(f"[*] Collected {len(all_records)} smell instances...")

    output_path = os.path.join(config.METADATA_DIR, "labeled_dataset.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, indent=4)
        
    print(f"[+] Labeling complete. Total records: {len(all_records)}")

if __name__ == "__main__":
    main()
