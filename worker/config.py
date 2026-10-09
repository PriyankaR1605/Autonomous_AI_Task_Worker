import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

class Settings:
    # Model configuration
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini/gemini-3.5-flash-lite")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Primary Cloud Deployment Link
    MAIN_APP_URL: str = "https://autonomous-ai-task-worker.onrender.com"
    
    # Public Base URL relative to cloud deployment
    # Always defaults to https://autonomous-ai-task-worker.onrender.com unless explicitly overridden
    PUBLIC_BASE_URL: str = (
        os.getenv("PUBLIC_BASE_URL") or 
        os.getenv("RENDER_EXTERNAL_URL") or 
        MAIN_APP_URL
    ).rstrip("/")

    # Mock ERP Internal Service configuration (used by internal background worker & Playwright inside container)
    MOCK_ERP_HOST: str = os.getenv("MOCK_ERP_HOST", "127.0.0.1")
    MOCK_ERP_PORT: int = int(os.getenv("MOCK_ERP_PORT", "8000"))
    MOCK_ERP_BASE_URL: str = os.getenv("MOCK_ERP_BASE_URL") or f"http://{MOCK_ERP_HOST}:{MOCK_ERP_PORT}"
    
    ERP_ADMIN_USER: str = os.getenv("ERP_ADMIN_USER", "admin")
    ERP_ADMIN_PASS: str = os.getenv("ERP_ADMIN_PASS", "company_secure_pass")

    # Agent thresholds & behavior
    HEADLESS_BROWSER: bool = os.getenv("HEADLESS_BROWSER", "false").lower() in ("true", "1", "yes")
    MAX_AGENT_STEPS: int = int(os.getenv("MAX_AGENT_STEPS", "15"))
    HIGH_RISK_AMOUNT_THRESHOLD: float = float(os.getenv("HIGH_RISK_AMOUNT_THRESHOLD", "3000.00"))
    STEP_DELAY_SECONDS: float = float(os.getenv("STEP_DELAY_SECONDS", "2.0"))

    # File paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(__file__))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    DOCS_DIR: str = os.path.join(DATA_DIR, "company_docs")
    INVOICES_DIR: str = os.path.join(DATA_DIR, "sample_invoices")
    STORAGE_DIR: str = os.path.join(DATA_DIR, "storage")
    TABLES_DIR: str = os.path.join(DATA_DIR, "enterprise_tables")
    SCREENSHOTS_DIR: str = os.path.join(STORAGE_DIR, "screenshots")

    def get_public_url(self, path: str = "") -> str:
        """Returns the public web URL for a route, relative to the main deployment link."""
        clean_path = ("/" + path.lstrip("/")) if path else ""
        return f"{self.PUBLIC_BASE_URL}{clean_path}"

    def get_portal_url(self, path: str = "dashboard") -> str:
        """Returns the URL to the Enterprise Portal relative to the main deployment link."""
        clean_path = ("/" + path.lstrip("/")) if path else ""
        return f"{self.PUBLIC_BASE_URL}{clean_path}"

    def get_relative_url(self, path: str = "dashboard") -> str:
        """Returns pure relative path for browser navigation."""
        return ("/" + path.lstrip("/")) if path else "/"

settings = Settings()

# Ensure runtime directories exist
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(settings.SCREENSHOTS_DIR, exist_ok=True)
if hasattr(settings, 'DOCS_DIR'):
    os.makedirs(settings.DOCS_DIR, exist_ok=True)
