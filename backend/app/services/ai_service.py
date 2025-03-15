import json
import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from retry import retry

import google.generativeai as genai

from app.core.config import GEMINI_API_KEY
from app.models import FileInfo, SetupStep, ImplementationStep, RepoAnalysisResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_model():
    """Get the Gemini Pro model for text generation."""
    return genai.GenerativeModel('gemini-2.0-flash-lite')


def clean_json_string(json_text: str) -> str:
    """Clean a JSON string from a model response."""
    if "```json" in json_text:
        json_text = json_text.split("```json")[1].split("```")[0].strip()
    elif "```" in json_text:
        json_text = json_text.split("```")[1].split("```")[0].strip()
            
    # Remove any other markdown formatting or stray characters
    json_text = json_text.strip()
    
    return json_text

@retry(exceptions = Exception, tries =2,  delay=2, backoff=2)
def extract_feature_keywords(feature_description: str) -> List[str]:
    """
    Extract relevant keywords from the feature description to help filter files.
    """
    model = get_gemini_model()
    
    prompt = f"""
    You are a code expert helping to identify relevant files for implementing a feature.
    
    Extract 10-20 key technical keywords or code identifiers from this feature description.
    These will be used to search for relevant files in a codebase.
    Focus on component names, functions, UI elements, variable names, and technical concepts.
    
    Feature description: {feature_description}
    
    Return the keywords as a JSON array of strings. Example: ["button", "onClick", "color", "styles", "theme"]

    Response format: Only include the raw JSON array with no explanations or additional text.
    """
    
    response = model.generate_content(prompt)
    try:
        # Extract JSON array from the response
        keywords_text = clean_json_string(response.text.strip())
        keywords = json.loads(keywords_text)
        
        # Ensure all keywords are reasonable search terms
        filtered_keywords = [k for k in keywords if len(k) >= 3 and len(k) <= 30]
        
        return filtered_keywords
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        # Fallback to basic keyword extraction
        words = feature_description.lower().split()
        return [w for w in words if len(w) > 3][:10]

def parse_repo_content(repo_content: str) -> Dict[str, str]:
    """
    Parse the repository content string from gitingest into individual files.
    
    Returns:
        Dict[str, str]: Dictionary with file paths as keys and file contents as values
    """
    files = {}
    current_file = None
    current_content = []
    
    lines = repo_content.split('\n')
    i = 0
    
    # Skip past directory structure section
    while i < len(lines) and not lines[i].startswith("File:"):
        i += 1
    
    while i < len(lines):
        line = lines[i]
        
        if line.startswith("File:"):
            # Save previous file if exists
            if current_file:
                files[current_file] = '\n'.join(current_content)
                current_content = []
            
            # Extract new file path
            current_file = line.replace("File:", "").strip()
            i += 1
            
            # Skip the separator line
            if i < len(lines) and lines[i].startswith("====="):
                i += 1
        elif line.startswith("=====") and i+1 < len(lines) and lines[i+1].startswith("File:"):
            # Save the current file and start a new one
            if current_file:
                files[current_file] = '\n'.join(current_content)
                current_content = []
            i += 1
        else:
            # Add line to current file content
            current_content.append(line)
            i += 1
            
    # Add the last file
    if current_file:
        files[current_file] = '\n'.join(current_content)
        
    return files

async def analyze_file_relevance(file_path: str, file_content: str, feature_description: str) -> Optional[FileInfo]:
    """
    Analyze a file's relevance to the feature being implemented.
    Returns a FileInfo object with relevance score and reason.
    """
    model = get_gemini_model()
    
    # Limit content size to avoid token limits
    max_content_length = 7000000
    content_preview = file_content[:max_content_length] + "\n... (content truncated)" if len(file_content) > max_content_length else file_content

    prompt = f"""
    You are a code expert analyzing which files need to be modified to implement a feature.
    
    Evaluate this file's relevance to implementing the following feature:
    
    Feature: {feature_description}
    
    File path: {file_path}
    
    File content preview:
    ```
    {content_preview}
    ```
    
    Return a JSON object with:
    - relevance_score: number between 0 and 1 indicating semantic relevance
    - importance: number from 1-10 (10 = most relevant, would definitely need modification)
    - reason: brief explanation why this file matters for the feature (or doesn't)
    
    Example: {{"relevance_score":0.9,"importance": 8, "reason": "This file contains the button component that needs color modifications"}}

    Response format: Only include the raw JSON object with no explanations or additional text.
    """
    
    try:
        response = model.generate_content(prompt)
        result_text = clean_json_string(response.text)
        result = json.loads(result_text)
        
        # Ensure scores are within bounds
        relevance_score = max(0, min(1, result.get("relevance_score", 0)))
        importance = max(1, min(10, result.get("importance", 1)))
        
        # Only consider files with good semantic relevance
        if relevance_score >= 0.5:
            return FileInfo(
                path=file_path,
                content_preview=content_preview[:500] + "..." if len(content_preview) > 500 else content_preview,
                importance=importance,
                reason=result.get("reason", "Relevance determined through semantic analysis")
            )
        return None
    except Exception as e:
        logger.exception(f"Error analyzing file relevance for {file_path}")
        return None

async def generate_implementation_plan(
    repo_name: str,
    feature_description: str,
    relevant_files: List[FileInfo]
) -> Dict[str, Any]:
    """
    Generate a comprehensive implementation plan for the feature.
    """
    model = get_gemini_model()
    
    # Sort by importance
    relevant_files.sort(key=lambda x: x.importance, reverse=True)
    
    # Use top files for plan generation
    top_files = relevant_files[:10]
    
    # Prepare files info for plan generation
    files_info = ""
    for i, file in enumerate(top_files, 1):
        files_info += f"File {i}: {file.path}\n"
        files_info += f"Importance: {file.importance}/10\n"
        files_info += f"Reason: {file.reason}\n\n"
        if i <= 5:  # Include content previews only for the top 5 files
            files_info += f"Preview:\n```\n{file.content_preview[:1000]}...\n```\n\n"
    
    prompt = f"""
    You are an expert software developer creating a detailed implementation plan for a feature.
    
    Repository: {repo_name}
    Feature to implement: {feature_description}
    
    Based on the analysis of the repository structure, here are the most relevant files:
    
    {files_info}
    
    Create a comprehensive implementation plan with these components:
    
    1. A brief summary of the implementation approach
    2. Setup instructions (environment setup, dependencies)
    3. Step-by-step implementation instructions (which files to modify and how)
    4. Potential challenges and how to address them
    
    Return your response as a JSON object with this structure:
    {{
      "feature_summary": "Brief summary of the approach",
      "setup_instructions": [
        {{"step_number": 1, "description": "Step description", "code": "Any setup code needed"}}
      ],
      "implementation_steps": [
        {{"step_number": 1, "description": "Detailed step", "file_path": "path/to/file", "code_snippet": "Example code change"}}
      ],
      "potential_challenges": ["Challenge 1", "Challenge 2"]
    }}
    
    Be specific and practical. Focus on concrete steps a developer would take to implement this feature.
    """
    
    try:
        response = model.generate_content(prompt)
        
        # Extract JSON from the response
        json_text = clean_json_string(response.text.strip())
        plan = json.loads(json_text)
        
        # Validate and ensure all required fields exist
        if "feature_summary" not in plan:
            plan["feature_summary"] = f"Implementation plan for {feature_description}"
            
        if "setup_instructions" not in plan or not plan["setup_instructions"]:
            plan["setup_instructions"] = [
                {"step_number": 1, "description": "Clone the repository", "code": f"git clone {repo_name}.git"}
            ]
            
        if "implementation_steps" not in plan or not plan["implementation_steps"]:
            plan["implementation_steps"] = [
                {
                    "step_number": 1, 
                    "description": f"Review {top_files[0].path if top_files else 'relevant files'}",
                    "file_path": top_files[0].path if top_files else None,
                    "code_snippet": None
                }
            ]
            
        if "potential_challenges" not in plan:
            plan["potential_challenges"] = ["Implementation may require additional context"]
        
        # Convert dictionaries to proper objects
        setup_steps = [SetupStep(**step) for step in plan["setup_instructions"]]
        
        # Ensure implementation steps have all required fields
        implementation_steps = []
        for step in plan["implementation_steps"]:
            if "step_number" not in step:
                step["step_number"] = len(implementation_steps) + 1
            if "description" not in step:
                step["description"] = "Implementation step"
            implementation_steps.append(ImplementationStep(**step))
        
        return {
            "feature_summary": plan["feature_summary"],
            "setup_instructions": setup_steps,
            "implementation_steps": implementation_steps,
            "potential_challenges": plan["potential_challenges"]
        }
    except Exception as e:
        logger.error(f"Error generating implementation plan: {e}", exc_info=True)
        # Return a fallback plan
        return {
            "feature_summary": f"Implementation plan for {feature_description}",
            "setup_instructions": [
                SetupStep(step_number=1, description="Clone the repository", code=f"git clone {repo_name}.git")
            ],
            "implementation_steps": [
                ImplementationStep(
                    step_number=1, 
                    description="Review the most relevant files first",
                    file_path=relevant_files[0].path if relevant_files else None,
                    code_snippet="# Review this file for implementation details"
                )
            ],
            "potential_challenges": ["API limitations prevented detailed analysis"]
        }

async def analyze_repository(repo_content: str, repo_url: str, feature_description: str) -> RepoAnalysisResponse:
    """
    Analyze repository content and generate implementation plan for a feature.
    
    Args:
        repo_content: String content of the repository from gitingest
        repo_url: URL of the GitHub repository
        feature_description: Description of the feature to implement
        
    Returns:
        RepoAnalysisResponse: Analysis results and implementation plan
    """
    try:
        # Extract repository name from URL
        repo_parts = repo_url.rstrip('/').split('/')
        repo_name = '/'.join(repo_parts[-2:])
        
        # Parse repository content into individual files
        files = parse_repo_content(repo_content)
        
        # Extract keywords from feature description
        keywords = extract_feature_keywords(feature_description)
        logger.info(f"Extracted keywords: {keywords}")
        
        # Create tasks for analyzing file relevance
        analysis_tasks = []
        for file_path, file_content in files.items():
            # Simple keyword-based pre-filtering to reduce API calls
            if any(keyword.lower() in file_path.lower() or 
                   keyword.lower() in file_content.lower()[:1000] 
                   for keyword in keywords):
                task = analyze_file_relevance(file_path, file_content, feature_description)
                analysis_tasks.append(task)
        
        # Run analyses concurrently (with a reasonable limit)
        chunk_size = 5  # Process files in chunks to avoid overwhelming the API
        all_relevant_files = []
        
        for i in range(0, len(analysis_tasks), chunk_size):
            chunk = analysis_tasks[i:i+chunk_size]
            chunk_results = await asyncio.gather(*chunk, return_exceptions=True)
            
            # Filter out None results and exceptions
            for result in chunk_results:
                if isinstance(result, Exception):
                    logger.error(f"Analysis failed: {result}")
                    continue
                if result is not None:
                    all_relevant_files.append(result)
        
        # Sort by importance
        all_relevant_files.sort(key=lambda x: x.importance, reverse=True)
        
        # Generate implementation plan
        plan = await generate_implementation_plan(
            repo_name=repo_name,
            feature_description=feature_description,
            relevant_files=all_relevant_files
        )
        
        # Create and return the response
        return RepoAnalysisResponse(
            repository_name=repo_name,
            feature_summary=plan["feature_summary"],
            setup_instructions=plan["setup_instructions"],
            relevant_files=all_relevant_files[:15],  # Limit to top 15 most relevant files
            implementation_steps=plan["implementation_steps"],
            potential_challenges=plan["potential_challenges"]
        )
    
    except Exception as e:
        logger.exception(f"Error in analyze_repository: {e}")
        raise