from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ServiceInterface(ABC):
    """
    Abstract base class for service interfaces
    """
    @abstractmethod
    async def call_service(
        self, 
        endpoint: str, 
        method: str, 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict:
        """
        Call a service endpoint
        
        Args:
            endpoint: The endpoint to call
            method: The HTTP method to use
            data: Optional request body data
            headers: Optional request headers
        """
        pass 