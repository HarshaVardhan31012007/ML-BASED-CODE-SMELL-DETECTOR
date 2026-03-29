import os
import sys
from fastapi import FastAPI, HTTPException, Request # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from pydantic import BaseModel # type: ignore
import uvicorn # type: ignore

# Add parent directory to path to ensure internal modules are found
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from static_analyzer.pipeline import CodeSmellCompilerModule # type: ignore
except ImportError:
    # Fallback for different execution contexts
    sys.path.append(os.path.join(root_dir, '..'))
    from static_analyzer.pipeline import CodeSmellCompilerModule # type: ignore

app = FastAPI(title="ML-Driven Code Smell Detector")

# Mount static files and templates
os.makedirs("frontend/static", exist_ok=True)
os.makedirs("frontend/templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Initialize analyzer
analyzer = CodeSmellCompilerModule()

class CodeSnippet(BaseModel):
    code: str

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze_snippet(snippet: CodeSnippet):
    """Analyzes a code snippet from the web UI."""
    try:
        # Create a temporary file to use the analyzer's file-based methods
        temp_file = "temp_analysis.py"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(snippet.code)
        
        # Run analysis (already has internal try-excepts for granular failure)
        results = analyzer.analyze(temp_file)
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return JSONResponse(content=results)
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[!] Critical error during analysis:\n{error_detail}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
