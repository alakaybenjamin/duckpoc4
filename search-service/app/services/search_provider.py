from abc import ABC, abstractmethod
from typing import List, Dict, Any
from azure.identity import ClientSecretCredential
from azure.search.documents import SearchClient
from app.core.config import settings

class SearchProvider(ABC):
    """
    Abstract base class for search providers
    """
    @abstractmethod
    async def search(self, search_text: str, search_fields: List[str], select: List[str]) -> List[Dict[str, Any]]:
        """
        Execute a search against the provider
        """
        pass
    
    @classmethod
    def get_provider(cls, provider_type: str = "azure") -> "SearchProvider":
        """
        Factory method to get search provider based on type
        """
        if provider_type.lower() == "azure":
            return AzureSearchProvider()
        else:
            raise ValueError(f"Unsupported search provider type: {provider_type}")

class AzureSearchProvider(SearchProvider):
    """
    Azure AI Search implementation
    """
    def __init__(self):
        # Authenticate using ClientSecretCredential
        self.credential = ClientSecretCredential(
            tenant_id=settings.AZURE_TENANT_ID,
            client_id=settings.AZURE_CLIENT_ID,
            client_secret=settings.AZURE_CLIENT_SECRET
        )
        
        # Create a SearchClient
        self.search_client = SearchClient(
            endpoint=settings.SEARCH_SERVICE_ENDPOINT,
            index_name=settings.INDEX_NAME,
            credential=self.credential
        )
    
    async def search(self, search_text: str, search_fields: List[str], select: List[str]) -> List[Dict[str, Any]]:
        """
        Execute a search against Azure AI Search
        """
        # Execute search using Azure Search
        results = self.search_client.search(
            search_text=search_text,
            search_fields=search_fields,
            select=select
        )
        
        # Convert results to list of dictionaries
        return [dict(result) for result in results] 