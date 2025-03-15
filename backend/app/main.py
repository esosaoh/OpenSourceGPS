from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
import tiktoken
import traceback
import sys
from gitingest import ingest
from .pack import PackRequest, PackResponse, normalize_github_url, check_repo_access, parse_content, get_largest_files
import concurrent.futures

app = FastAPI(title="Hackathon Project")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Hackathon API"}

@app.post("/api/pack", response_model=PackResponse)
async def pack_repository(request: PackRequest):
    repo_url = request.repo_url
    max_file_size = request.max_file_size
    max_tokens = request.max_tokens
    exclude_patterns = request.exclude_patterns

    normalized_url = normalize_github_url(repo_url)
    if not normalized_url:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")

    can_access, error_message, status_code = check_repo_access(normalized_url)
    if not can_access:
        raise HTTPException(status_code=status_code, detail=error_message)

    try:
        # Use ThreadPoolExecutor to run the ingest function in a separate thread
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(ingest, normalized_url, max_file_size, exclude_patterns)
            summary, tree, content = future.result()  # Wait for the result

        summary_lines = summary.split("\n")
        num_files_analyzed = int(summary_lines[1].split(": ")[1])
        token_str = summary_lines[3].split(": ")[1]
        if token_str.endswith("M"):
            estimated_tokens = float(token_str.replace("M", "")) * 1_000_000
        else:
            estimated_tokens = float(token_str.replace("k", "")) * 1_000

        if estimated_tokens > max_tokens:
            files = parse_content(content)
            largest_files = get_largest_files(files)

            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Token limit exceeded",
                    "files_analyzed": num_files_analyzed,
                    "estimated_tokens": estimated_tokens,
                    "largest_files": largest_files,
                }
            )

        content = f"{tree}\n\n{content}"

        # Return successful response with contents
        return PackResponse(
            files_analyzed=num_files_analyzed,
            estimated_tokens=estimated_tokens,
            content=content,
            largest_files=None 
        )

    except Exception as e:
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
        }
        print("Error in pack_repository:", error_details, file=sys.stderr)
        raise HTTPException(status_code=500, detail=error_details)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
