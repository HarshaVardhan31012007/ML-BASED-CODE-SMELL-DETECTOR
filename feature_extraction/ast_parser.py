import ast
import os
import sys

class CodeSmellFeatureExtractor(ast.NodeVisitor):
    def __init__(self):
        self.features = {
            "num_functions": 0,
            "num_classes": 0,
            "num_parameters": 0,
            "num_loops": 0,
            "num_conditionals": 0,
            "num_imports": 0,
            "num_returns": 0,
            "num_variables": 0,
            "num_literals": 0,
            "max_nesting_depth": 0,
            "ast_node_count": 0,
            "avg_func_length": 0,
            "max_func_length": 0,
            "avg_class_size": 0,
            "cyclomatic_complexity": 1,
            "num_try_except": 0,
            "num_comprehensions": 0,
            "num_yields": 0,
            "num_asserts": 0,
            "num_with_blocks": 0,
            "num_globals": 0,
            "num_lambda": 0,
            "num_raises": 0,
            
            # Security Features
            "num_dangerous_calls": 0,
            "num_sensitive_literals": 0,
            "num_sql_concat": 0,
            "num_dynamic_open": 0,
            "num_unprotected_routes": 0,
            "has_except_pass": 0,
            
            # Metric Features
            "halstead_volume": 0.0,
            "halstead_difficulty": 0.0,
            "halstead_effort": 0.0,
            "maintainability_index": 0.0,
            
            # New Structural Features
            "total_loc": 0,
            "logic_node_ratio": 0.0,
            "max_complexity_per_function": 0,
            "num_literals": 0,
            "num_string_literals": 0,
            "num_numeric_literals": 0
        }
        self.func_lengths = []
        self.class_sizes = []
        self.func_complexities = []
        self.current_depth = 0
        self.logic_nodes = {ast.If, ast.For, ast.While, ast.Try, ast.With, ast.FunctionDef, ast.ClassDef, ast.BoolOp, ast.Compare}
        self.total_nodes = 0
        self.dangerous_apis = {'eval', 'exec', 'os.system', 'subprocess.run', 'subprocess.Popen'}
        self.sensitive_keywords = {'password', 'secret', 'api_key', 'token', 'passwd', 'credential'}

    def generic_visit(self, node):
        self.features["ast_node_count"] += 1
        self.total_nodes += 1
        if type(node) in self.logic_nodes:
            self.features["logic_node_ratio"] += 1
        super().generic_visit(node)

    def visit_FunctionDef(self, node):
        self.features["num_functions"] += 1
        self.features["num_parameters"] += len(node.args.args)
        self.features["cyclomatic_complexity"] += 1 # Base complexity
        
        # Calculate length
        length = (node.end_lineno - node.lineno) if hasattr(node, 'end_lineno') else 0
        self.func_lengths.append(length)
        self.features["max_func_length"] = max(self.features["max_func_length"], length)
        
        # Track complexity for max
        current_comp = 1
        for sub in ast.walk(node):
            if isinstance(sub, (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler)):
                current_comp += 1
        self.func_complexities.append(current_comp)
        
        # Check for unauthenticated routes (heuristic)
        has_route = False
        has_auth = False
        for decorator in node.decorator_list:
             if isinstance(decorator, ast.Call):
                 name = ""
                 if isinstance(decorator.func, ast.Attribute):
                     name = getattr(decorator.func, "attr", "")
                 elif isinstance(decorator.func, ast.Name):
                     name = getattr(decorator.func, "id", "")
                 
                 if any(kw in name.lower() for kw in ['route', 'post', 'get', 'put', 'delete', 'patch']):
                     has_route = True
                 if any(kw in name.lower() for kw in ['auth', 'login', 'protect', 'permission', 'jwt']):
                     has_auth = True
                     
        if has_route and not has_auth:
            self.features["num_unprotected_routes"] += 1

        self.current_depth += 1
        self.features["max_nesting_depth"] = max(self.features["max_nesting_depth"], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Call(self, node):
        # 1. Dangerous API calls
        call_name = ""
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                call_name = f"{node.func.value.id}.{node.func.attr}"
            else:
                call_name = node.func.attr
        
        if call_name in self.dangerous_apis:
            self.features["num_dangerous_calls"] += 1
            
        # 2. Dynamic file open
        if call_name == 'open' and node.args:
            if not isinstance(node.args[0], (ast.Str, ast.Constant)):
                self.features["num_dynamic_open"] += 1
                
        # 3. SQL injection patterns in execute
        if call_name == 'execute' or 'execute' in call_name:
            for arg in node.args:
                if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                    self.features["num_sql_concat"] += 1
                elif isinstance(arg, ast.JoinedStr): # f-strings
                    self.features["num_sql_concat"] += 1

        self.generic_visit(node)

    def visit_Constant(self, node):
        self.features["num_literals"] += 1
        if isinstance(node.value, str):
            self.features["num_string_literals"] += 1
            if any(kw in node.value.lower() for kw in self.sensitive_keywords):
                if len(node.value) > 6:
                    self.features["num_sensitive_literals"] += 1
        elif isinstance(node.value, (int, float)):
            self.features["num_numeric_literals"] += 1
            
        self.generic_visit(node)

    def visit_Try(self, node):
        self.features["num_try_except"] += 1
        # Improper error handling (except: pass)
        for handler in node.handlers:
            if len(handler.body) == 1 and isinstance(handler.body[0], (ast.Pass, ast.Return, ast.Continue)):
                 # Heuristic for ignored exceptions
                 self.features["has_except_pass"] += 1

        self.current_depth += 1
        self.features["max_nesting_depth"] = max(self.features["max_nesting_depth"], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_ClassDef(self, node):
        self.features["num_classes"] += 1
        # Calculate size (LOC)
        size = (node.end_lineno - node.lineno) if hasattr(node, 'end_lineno') else 0
        self.class_sizes.append(size)
        
        self.current_depth += 1
        self.features["max_nesting_depth"] = max(self.features["max_nesting_depth"], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_For(self, node):
        self.features["num_loops"] += 1
        self.features["cyclomatic_complexity"] += 1
        self.current_depth += 1
        self.features["max_nesting_depth"] = max(self.features["max_nesting_depth"], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_AsyncFor(self, node):
        self.visit_For(node)

    def visit_While(self, node):
        self.features["num_loops"] += 1
        self.current_depth += 1
        self.features["max_nesting_depth"] = max(self.features["max_nesting_depth"], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_If(self, node):
        self.features["num_conditionals"] += 1
        self.features["cyclomatic_complexity"] += 1
        self.current_depth += 1
        self.features["max_nesting_depth"] = max(self.features["max_nesting_depth"], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_Import(self, node):
        self.features["num_imports"] += len(node.names)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.features["num_imports"] += len(node.names)
        self.generic_visit(node)

    def visit_Return(self, node):
        self.features["num_returns"] += 1
        self.generic_visit(node)

    def visit_Assign(self, node):
        self.features["num_variables"] += len(node.targets)
        # Check for sensitive variable names
        for target in node.targets:
            if isinstance(target, ast.Name):
                if any(kw in target.id.lower() for kw in self.sensitive_keywords):
                    if isinstance(node.value, (ast.Constant, ast.Str)):
                         self.features["num_sensitive_literals"] += 1
        self.generic_visit(node)
        
    def visit_AnnAssign(self, node):
        self.features["num_variables"] += 1
        self.generic_visit(node)
        
    def visit_ListComp(self, node):
        self.features["num_comprehensions"] += 1
        self.generic_visit(node)
        
    def visit_DictComp(self, node):
        self.features["num_comprehensions"] += 1
        self.generic_visit(node)
        
    def visit_SetComp(self, node):
        self.features["num_comprehensions"] += 1
        self.generic_visit(node)
        
    def visit_Yield(self, node):
        self.features["num_yields"] += 1
        self.generic_visit(node)
        
    def visit_YieldFrom(self, node):
        self.features["num_yields"] += 1
        self.generic_visit(node)
        
    def visit_Assert(self, node):
        self.features["num_asserts"] += 1
        self.generic_visit(node)
        
    def visit_With(self, node):
        self.features["num_with_blocks"] += 1
        self.current_depth += 1
        self.features["max_nesting_depth"] = max(self.features["max_nesting_depth"], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
        
    def visit_AsyncWith(self, node):
        self.visit_With(node)
        
    def visit_Global(self, node):
        self.features["num_globals"] += len(node.names)
        self.generic_visit(node)
        
    def visit_Lambda(self, node):
        self.features["num_lambda"] += 1
        self.generic_visit(node)
        
    def visit_Raise(self, node):
        self.features["num_raises"] += 1
        self.generic_visit(node)

    def calculate_halstead(self, source_code):
        """Calculates Halstead Metrics and Maintainability Index."""
        import math
        import re

        operators = set([
            'if', 'else', 'for', 'while', 'try', 'except', 'with', 'return', 'raise', 'yield',
            '+', '-', '*', '/', '%', '**', '//', '<<', '>>', '&', '|', '^', '~', '<', '>',
            '<=', '>=', '==', '!=', 'and', 'or', 'not', 'in', 'is', 'lambda', 'assert',
            '=', '+=', '-=', '*=', '/=', '%=', '**=', '//=', '<<=', '>>=', '&=', '|=', '^='
        ])

        # Tokenize roughly to find operands and operators
        tokens = re.findall(r'\w+|[^\w\s]', source_code)
        
        N1, N2 = 0, 0
        n1_set, n2_set = set(), set()
        
        for t in tokens:
            if t in operators:
                N1 += 1
                n1_set.add(t)
            elif re.match(r'^\w+$', t):
                N2 += 1
                n2_set.add(t)
        
        n1, n2 = len(n1_set), len(n2_set)
        n = n1 + n2
        N = N1 + N2
        
        # Finalize averages
        if self.func_lengths:
            val = sum(self.func_lengths) / len(self.func_lengths)
            self.features["avg_func_length"] = float(f"{val:.2f}")
        if self.class_sizes:
            val = sum(self.class_sizes) / len(self.class_sizes)
            self.features["avg_class_size"] = float(f"{val:.2f}")

        # Avoid log(0)
        h_volume = float(N * math.log2(n)) if n > 0 else 0.0
        h_difficulty = float((n1 / 2) * (N2 / n2)) if n2 > 0 else 0.0
        h_effort = float(h_difficulty * h_volume)
        
        # Calculate Maintainability Index (Classic formula)
        # MI = max(0, (171 - 5.2 * ln(V) - 0.23 * (G) - 16.2 * ln(LOC)) * 100 / 171)
        loc = len(source_code.splitlines())
        g = float(self.features["cyclomatic_complexity"])
        
        try:
            v_term = 5.2 * math.log(h_volume) if h_volume > 0 else 0
            loc_term = 16.2 * math.log(loc) if loc > 0 else 0
            mi = (171 - v_term - 0.23 * g - loc_term) * (100.0 / 171.0)
            mi = max(0.0, min(100.0, mi))
        except:
            mi = 50.0

        self.features.update({
            "halstead_volume": float(f"{h_volume:.2f}"),
            "halstead_difficulty": float(f"{h_difficulty:.2f}"),
            "halstead_effort": float(f"{h_effort:.2f}"),
            "maintainability_index": float(f"{mi:.2f}")
        })

def extract_features_from_code(source_code):
    """
    Parses source code into an AST and extracts structural features.
    Returns a dictionary of features. Returns None if parsing fails.
    """
    try:
        tree = ast.parse(source_code)
        extractor = CodeSmellFeatureExtractor()
        extractor.visit(tree)
        
        # Post-processing for advanced metrics
        extractor.calculate_halstead(source_code)
        
        # New Feature Finalization
        extractor.features["total_loc"] = len(source_code.splitlines())
        if extractor.total_nodes > 0:
            extractor.features["logic_node_ratio"] /= extractor.total_nodes
        if extractor.func_complexities:
            extractor.features["max_complexity_per_function"] = max(extractor.func_complexities)
        
        return extractor.features
    except Exception as e:
        return None

def extract_features_of_file_context(filepath, line_no=1):
    """
    Parses the whole file and extracts features for the function or class
    containing the specific line_no. This provides targetted context.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        tree = ast.parse(source)
        
        # Find the function or class defining this line
        context_node = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    if node.lineno <= line_no <= node.end_lineno:
                        # Find the most specific (deepest) node
                        if context_node is None or (node.end_lineno - node.lineno < context_node.end_lineno - context_node.lineno):
                            context_node = node
        
        extractor = CodeSmellFeatureExtractor()
        if context_node:
            extractor.visit(context_node)
        else:
            # Fallback to whole file if no function/class context found
            extractor.visit(tree)
            
        # Ensure post-processing is done
        extractor.calculate_halstead(source)
        extractor.features["total_loc"] = len(source.splitlines())
        if extractor.total_nodes > 0:
            extractor.features["logic_node_ratio"] /= extractor.total_nodes
        if extractor.func_complexities:
            extractor.features["max_complexity_per_function"] = max(extractor.func_complexities)

        return extractor.features
    except Exception:
        return None

def extract_features_from_file(filepath):
    """Reads a file and extracts AST features."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
        return extract_features_from_code(source_code)
    except Exception:
        return None

if __name__ == "__main__":
    # Test block
    sample_code = """
def example_function(a, b):
    import math
    if a > b:
        for i in range(10):
            print(i)
    return a + b
    """
    features = extract_features_from_code(sample_code)
    print("Extracted Features:", features)
