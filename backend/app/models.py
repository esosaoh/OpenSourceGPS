from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict

class RepoAnalysisRequest(BaseModel):
    repo_content: str
    repo_url: str
    feature_description: str
    
class FileInfo(BaseModel):
    path: str
    content_preview: Optional[str] = None
    importance: int  # 1-10 scale of relevance to the feature
    reason: str  # Why this file is relevant
    
class SetupStep(BaseModel):
    step_number: int
    description: str
    code: Optional[str] = None
    
class ImplementationStep(BaseModel):
    step_number: int
    description: str
    file_path: Optional[str] = None
    code_snippet: Optional[str] = None
    
class RepoAnalysisResponse(BaseModel):
    repository_name: str
    feature_summary: str
    setup_instructions: List[SetupStep]
    relevant_files: List[FileInfo]
    implementation_steps: List[ImplementationStep]
    potential_challenges: List[str]