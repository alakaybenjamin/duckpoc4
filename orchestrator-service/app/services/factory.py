from app.core.config import settings
from .http_service import HttpService
from .search_service import SearchService
from .user_history_service import UserHistoryService

def get_search_service() -> SearchService:
    """
    Get the search service client
    """
    service = HttpService(settings.SEARCH_SERVICE_URL)
    return SearchService(service)

def get_user_history_service() -> UserHistoryService:
    """
    Get the user history service client
    """
    service = HttpService(settings.USER_HISTORY_SERVICE_URL)
    return UserHistoryService(service) 