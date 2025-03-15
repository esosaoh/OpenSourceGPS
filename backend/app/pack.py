from pydantic import BaseModel
from typing import List, Optional
import requests
import tiktoken

tokenizer = tiktoken.get_encoding("cl100k_base")

# Models
class PackRequest(BaseModel):
    repo_url: str
    max_file_size: Optional[int] = 10485760  # Default 10MB
    max_tokens: Optional[int] = 1000000  # Default 1m tokens
    exclude_patterns: Optional[List[str]] = []

class PackResponse(BaseModel):
    files_analyzed: int
    estimated_tokens: float
    content: Optional[str]
    largest_files: Optional[List[dict]]

def normalize_github_url(url):
    """Convert various GitHub URL formats to a consistent format."""
    if not url:
        return None

    if url.endswith(".git"):
        url = url[:-4]

    if url.endswith("/"):
        url = url[:-1]

    if not url.startswith(("https://github.com/", "http://github.com/")):
        return None

    return url

def check_repo_access(repo_url):
    # Convert github.com URL to API URL
    if "github.com" in repo_url:
        api_url = repo_url.replace("github.com", "api.github.com/repos")
        try:
            response = requests.get(api_url)
            if response.status_code == 404:
                return False, "Repository not found", 404
            elif response.status_code == 403:
                return (
                    False,
                    "Repository is not accessible. Make sure it is public",
                    403,
                )
            elif not response.ok:
                return (
                    False,
                    f"GitHub API error: {response.status_code}",
                    response.status_code,
                )
            return True, None, 200
        except requests.RequestException as e:
            return False, f"Error checking repository: {str(e)}", 500
    return True, None, 200

def parse_content(content):
    files = {}
    current_file = None
    current_content = []

    for line in content.split("\n"):
        if line.startswith("=" * 48):
            if current_file and current_content:
                files[current_file] = "\n".join(current_content)
            current_content = []
        elif line.startswith("File: "):
            current_file = line[6:] 
        else:
            current_content.append(line)

    # Add the last file if there is one
    if current_file and current_content:
        files[current_file] = "\n".join(current_content)

    return files

def get_largest_files(files, n=10):
    largest_files = sorted(
        [(path, len(tokenizer.encode(content))) for path, content in files.items()],
        key=lambda x: x[1],
        reverse=True,
    )[:n]
    return [{"path": path, "tokens": tokens} for path, tokens in largest_files] 