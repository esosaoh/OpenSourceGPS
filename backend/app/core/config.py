import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# App settings
MAX_REPO_SIZE_MB = 100  # Maximum repository size to analyze
MAX_FILES_TO_ANALYZE = 200  # Maximum number of files to analyze in detail
CACHE_TTL = 3600  # Cache time-to-live in seconds