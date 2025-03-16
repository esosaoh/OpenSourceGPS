from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import tiktoken
import traceback
import sys
from gitingest import ingest
from .pack import PackRequest, PackResponse, normalize_github_url, check_repo_access, parse_content, get_largest_files
import concurrent.futures
from json import JSONDecodeError

from .models import RepoAnalysisRequest, RepoAnalysisResponse, ProcessRequest
from .services.health_service import get_health_status
from .services.ai_service import analyze_repository

app = FastAPI(title="gitmentor")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gitmentor.co", "https://9f5d-208-98-222-98.ngrok-free.app", "*"],
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
    

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return await get_health_status()

@app.post("/analyze", response_model=RepoAnalysisResponse)
async def analyze_repo(request: RepoAnalysisRequest):
    """
    Analyze a GitHub repository and generate implementation steps for a specific feature.
    
    - **repo_url**: GitHub repository URL
    - **feature_description**: Description of the feature to implement
    """
    try:
        # Ensure the request contains valid data
        if not request.repo_url or not request.feature_description:
            raise HTTPException(status_code=400, detail="repo_url and feature_description are required.")

        # Call the analyze_repository function
        result = await analyze_repository(request.repo_content, request.repo_url, request.feature_description)

        # Ensure the result is not None and matches the expected response model
        if result is None:
            raise HTTPException(status_code=500, detail="Analysis returned no result.")

        return result

    except JSONDecodeError as e:
        # Handle JSON decoding errors specifically
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid JSON format.",
                "details": str(e)
            }
        )
    except Exception as e:
        # General exception handling
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
        }
        print("Error in analyze_repo:", error_details, file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "An unexpected error occurred",
                "details": error_details
            }
        )
    
@app.options("/api/process")
async def options_process():
    return {"message": "Preflight request accepted"}

@app.post("/api/process", response_model=RepoAnalysisResponse)
async def process_request(request: ProcessRequest):
    """
    Enhanced Pack Request endpoint that first calls /api/pack and then /analyze.
    
    - **repo_url**: GitHub repository URL
    - **feature_description**: Description of the feature to implement
    """
    # Step 1: Call the /api/pack endpoint
    pack_request = PackRequest(
        repo_url=request.repo_url
    )

    try:
        pack_response = await pack_repository(pack_request)
        repo_content = pack_response.content  # Get the content from the pack response

        # Step 2: Call the /analyze endpoint
        analyze_request = RepoAnalysisRequest(
            repo_url=request.repo_url,
            feature_description=request.feature_description,
            repo_content=repo_content
        )

        analysis_response = await analyze_repo(analyze_request)
        return analysis_response

    except HTTPException as e:
        # Re-raise HTTP exceptions to return appropriate error responses
        raise e
    except Exception as e:
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
        }
        print("Error in epr_request:", error_details, file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "An unexpected error occurred during the EPR request",
                "details": error_details
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
