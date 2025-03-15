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
    return genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')


def clean_json_string(json_text: str) -> str:
    if "```json" in json_text:
        json_text = json_text.split("```json")[1].split("```")[0].strip()
    elif "```" in json_text:
        json_text = json_text.split("```")[1].split("```")[0].strip()
            
    # Remove any other markdown formatting or stray characters
    json_text = json_text.strip()
    
    try:
        json.loads(json_text)
        return json_text
    except json.JSONDecodeError as e:
        error_position = e.pos
        
        if "Unterminated string" in str(e):
            lines = json_text.split('\n')
            fixed_lines = []
            fixing = False
            quote_char = None
            
            for line in lines:
                if not fixing and ('"' in line or "'" in line) and line.count('"') % 2 != 0:
                    fixing = True
                    quote_char = '"' if line.count('"') % 2 != 0 else "'"
                    fixed_lines.append(line + quote_char)  # Add closing quote
                elif fixing:
                    fixing = False
                    fixed_lines.append(quote_char + line)  # Add opening quote
                else:
                    fixed_lines.append(line)
            
            json_text = '\n'.join(fixed_lines)
        
        try:
            json.loads(json_text)
            return json_text
        except:
            in_string = False
            quote_char = None
            result = []
            
            for char in json_text:
                if char in ['"', "'"]:
                    if not in_string:
                        in_string = True
                        quote_char = char
                    elif char == quote_char:
                        in_string = False
                        quote_char = None
                
                if in_string and char == '\n':
                    result.append(' ')
                else:
                    result.append(char)
            
            return ''.join(result)

@retry(exceptions = Exception, tries =2,  delay=2, backoff=2)
def extract_feature_keywords(feature_description: str) -> List[str]:
    """
    Extract relevant keywords from the feature description to help filter files.
    """
    model = get_gemini_model()
    
    prompt = f"""
    You are a code expert helping to identify relevant files for implementing a feature.
    
    Extract 5-7 key technical keywords or code identifiers from this feature description.
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
    
    while i < len(lines) and not lines[i].startswith("File:"):
        i += 1
    
    while i < len(lines):
        line = lines[i]
        
        if line.startswith("File:"):
            if current_file:
                files[current_file] = '\n'.join(current_content)
                current_content = []
            
            current_file = line.replace("File:", "").strip()
            i += 1
            
            if i < len(lines) and lines[i].startswith("====="):
                i += 1
        elif line.startswith("=====") and i+1 < len(lines) and lines[i+1].startswith("File:"):
            if current_file:
                files[current_file] = '\n'.join(current_content)
                current_content = []
            i += 1
        else:
            current_content.append(line)
            i += 1
            
    if current_file:
        files[current_file] = '\n'.join(current_content)
        
    return files

async def analyze_file_relevance(file_path: str, file_content: str, feature_description: str) -> Optional[FileInfo]:
    """
    Analyze a file's relevance to the feature being implemented.
    Returns a FileInfo object with relevance score and reason.
    """
    model = get_gemini_model()
    
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
        
        relevance_score = max(0, min(1, result.get("relevance_score", 0)))
        importance = max(1, min(10, result.get("importance", 1)))
        
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
    
    relevant_files.sort(key=lambda x: x.importance, reverse=True)
    
    top_files = relevant_files[:10]

    files_info = ""
    for i, file in enumerate(top_files, 1):
        files_info += f"File {i}: {file.path}\n"
        files_info += f"Importance: {file.importance}/10\n"
        files_info += f"Reason: {file.reason}\n\n"
        if i <= 5:  
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
    
    IMPORTANT: Ensure all JSON fields are properly escaped, especially code snippets containing quotes.
    """
    
    try:
        response = model.generate_content(prompt)
        
        # Extract JSON from the response
        json_text = clean_json_string(response.text.strip())
        
        try:
            plan = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"JSON text causing error: {json_text[:500]}...")
            
            fallback_plan = {
                "feature_summary": f"Implementation plan for {feature_description}",
                "setup_instructions": [],
                "implementation_steps": [],
                "potential_challenges": []
            }
            
            if '"feature_summary"' in json_text:
                try:
                    summary_start = json_text.find('"feature_summary"')
                    summary_content_start = json_text.find(':', summary_start) + 1
                    summary_content_end = json_text.find('",', summary_content_start)
                    if summary_content_end > summary_content_start:
                        fallback_plan["feature_summary"] = json_text[summary_content_start:summary_content_end].strip(' "')
                except:
                    pass
            
            for i, file in enumerate(top_files[:5], 1):
                fallback_plan["implementation_steps"].append({
                    "step_number": i,
                    "description": f"Review and modify {file.path}",
                    "file_path": file.path,
                    "code_snippet": "# Implement feature here"
                })
                
            fallback_plan["setup_instructions"].append({
                "step_number": 1,
                "description": "Clone the repository",
                "code": f"git clone {repo_name}.git"
            })
                
            fallback_plan["potential_challenges"].append("Response formatting issues encountered during analysis")
            
            plan = fallback_plan
        
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
                    "code_snippet": "# Review this file for implementation details"
                }
            ]
            
        if "potential_challenges" not in plan:
            plan["potential_challenges"] = ["Implementation may require additional context"]
        
        setup_steps = []
        for step in plan["setup_instructions"]:
            try:
                setup_steps.append(SetupStep(**step))
            except Exception as step_error:
                logger.error(f"Error processing setup step: {step_error}")
                setup_steps.append(SetupStep(
                    step_number=len(setup_steps) + 1,
                    description=str(step.get("description", "Setup step")),
                    code=str(step.get("code", "# Code here"))
                ))
        
        implementation_steps = []
        for step in plan["implementation_steps"]:
            try:
                if "step_number" not in step:
                    step["step_number"] = len(implementation_steps) + 1
                if "description" not in step:
                    step["description"] = "Implementation step"
                if "file_path" not in step or step["file_path"] is None:
                    step["file_path"] = top_files[0].path if top_files else "main.py"
                if "code_snippet" not in step or step["code_snippet"] is None:
                    step["code_snippet"] = "# Implementation code here"
                    
                implementation_steps.append(ImplementationStep(**step))
            except Exception as step_error:
                logger.error(f"Error processing implementation step: {step_error}")
                implementation_steps.append(ImplementationStep(
                    step_number=len(implementation_steps) + 1,
                    description=str(step.get("description", "Implementation step")),
                    file_path=str(step.get("file_path", top_files[0].path if top_files else "main.py")),
                    code_snippet=str(step.get("code_snippet", "# Code here"))
                ))
        
        return {
            "feature_summary": plan["feature_summary"],
            "setup_instructions": setup_steps,
            "implementation_steps": implementation_steps,
            "potential_challenges": plan["potential_challenges"]
        }
    except Exception as e:
        logger.error(f"Error generating implementation plan: {e}", exc_info=True)
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
        repo_parts = repo_url.rstrip('/').split('/')
        repo_name = '/'.join(repo_parts[-2:])
        
        files = parse_repo_content(repo_content)
        
        keywords = extract_feature_keywords(feature_description)
        logger.info(f"Extracted keywords: {keywords}")
        
        analysis_tasks = []
        for file_path, file_content in files.items():
            if any(keyword.lower() in file_path.lower() or 
                   keyword.lower() in file_content.lower()[:1000] 
                   for keyword in keywords):
                task = analyze_file_relevance(file_path, file_content, feature_description)
                analysis_tasks.append(task)
        
        chunk_size = 5  
        all_relevant_files = []
        
        for i in range(0, len(analysis_tasks), chunk_size):
            chunk = analysis_tasks[i:i+chunk_size]
            chunk_results = await asyncio.gather(*chunk, return_exceptions=True)
            
            for result in chunk_results:
                if isinstance(result, Exception):
                    logger.error(f"Analysis failed: {result}")
                    continue
                if result is not None:
                    all_relevant_files.append(result)
        
        all_relevant_files.sort(key=lambda x: x.importance, reverse=True)
        
        plan = await generate_implementation_plan(
            repo_name=repo_name,
            feature_description=feature_description,
            relevant_files=all_relevant_files
        )

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