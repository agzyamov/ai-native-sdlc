"""
Configuration loader for Azure Function environment variables.
"""
import os


class Config:
    """Environment configuration with defaults."""
    
    def __init__(self):
        # GitHub configuration
        self.github_owner = os.getenv("GITHUB_OWNER", "")
        self.github_repo = os.getenv("GITHUB_REPO", "")
        self.github_workflow_filename = os.getenv("GITHUB_WORKFLOW_FILENAME", "spec-kit-specify.yml")
        self.gh_workflow_dispatch_pat = os.getenv("GH_WORKFLOW_DISPATCH_PAT", "")
        
        # Azure DevOps configuration
        self.ado_org_url = os.getenv("ADO_ORG_URL", "")
        self.ado_project = os.getenv("ADO_PROJECT", "")
        self.ado_work_item_pat = os.getenv("ADO_WORK_ITEM_PAT", "")
        self.spec_column_name = os.getenv("SPEC_COLUMN_NAME", "Specification – Doing")
        self.ai_user_match = os.getenv("AI_USER_MATCH", "AI Teammate")
        
        # Application configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.function_timeout_seconds = int(os.getenv("FUNCTION_TIMEOUT_SECONDS", "30"))
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate required configuration is present.
        
        Returns:
            Tuple of (is_valid, missing_vars)
        """
        missing = []
        required_vars = [
            ("GITHUB_OWNER", self.github_owner),
            ("GITHUB_REPO", self.github_repo),
            ("GH_WORKFLOW_DISPATCH_PAT", self.gh_workflow_dispatch_pat),
        ]
        
        for var_name, var_value in required_vars:
            if not var_value:
                missing.append(var_name)
        
        return len(missing) == 0, missing


def get_config() -> Config:
    """Get configuration instance."""
    return Config()
