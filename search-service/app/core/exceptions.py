from fastapi import HTTPException

class SearchError(HTTPException):
    def __init__(self, detail: str = "Search error occurred"):
        super().__init__(status_code=500, detail=detail)

class ConfigurationError(HTTPException):
    def __init__(self, detail: str = "Configuration error"):
        super().__init__(status_code=500, detail=detail)

class SearchProviderError(HTTPException):
    def __init__(self, detail: str = "Search provider error"):
        super().__init__(status_code=500, detail=detail) 