import json
import logging
from typing import Dict, List, Optional, Union
import aiohttp
import asyncio
from urllib.parse import urljoin

from .exceptions import Hysteria2Error, Hysteria2AuthError, Hysteria2ConnectionError
from .models import TrafficStats, OnlineStatus

logger = logging.getLogger(__name__)


class Hysteria2Client:
    """Asynchronous client for the Hysteria2 API."""

    def __init__(self, base_url: str, secret: str = None, timeout: float = 10):
        """
        Initialize the Hysteria2 API client.

        Args:
            base_url: The base URL of the Hysteria2 API, including protocol and port
                      (e.g., 'http://127.0.0.1:25413')
            secret: The authentication secret for the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.secret = secret
        self.timeout = timeout
        self._session = None
        self._headers = {'Authorization': secret} if secret else {}
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self._headers)
        return self._session
        
    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()
            
    async def __aenter__(self):
        """Context manager enter."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()

    async def get_traffic_stats(self, clear: bool = False) -> Dict[str, TrafficStats]:
        """
        Get traffic statistics for all clients.

        Args:
            clear: Whether to clear statistics after retrieval

        Returns:
            Dictionary mapping client IDs to their traffic statistics
        """
        endpoint = '/traffic'
        if clear:
            endpoint += '?clear=1'
            
        try:
            response = await self._make_request('GET', endpoint)
            return {client_id: TrafficStats.from_dict(stats) 
                   for client_id, stats in response.items()}
        except Exception as e:
            logger.error(f"Failed to get traffic statistics: {e}")
            raise

    async def get_online_clients(self) -> Dict[str, OnlineStatus]:
        """
        Get online status for all clients.

        Returns:
            Dictionary mapping client IDs to their online status
        """
        try:
            response = await self._make_request('GET', '/online')
            return {client_id: OnlineStatus.from_int(connections) 
                   for client_id, connections in response.items()}
        except Exception as e:
            logger.error(f"Failed to get online clients: {e}")
            raise

    async def kick_clients(self, client_ids: List[str]) -> bool:
        """
        Kick clients by their IDs.

        Args:
            client_ids: List of client IDs to kick

        Returns:
            True if successful, raises an exception otherwise
        """
        try:
            await self._make_request('POST', '/kick', json_data=client_ids)
            return True
        except Exception as e:
            logger.error(f"Failed to kick clients {client_ids}: {e}")
            raise

    async def _make_request(self, method: str, endpoint: str, json_data: Optional[Union[Dict, List]] = None) -> Dict:
        """
        Make a request to the Hysteria2 API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            json_data: JSON data to send in the request body

        Returns:
            Parsed JSON response as a dictionary

        Raises:
            Hysteria2AuthError: If authentication fails
            Hysteria2ConnectionError: If there's a connection error
            Hysteria2Error: For other API errors
        """
        url = urljoin(self.base_url, endpoint)
        session = await self._get_session()
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            if method == 'GET':
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 401:
                        raise Hysteria2AuthError(f"Authentication failed: {await response.text()}")
                    
                    response.raise_for_status()
                    
                    if response.content_length == 0:
                        return {}
                    
                    return await response.json()
                    
            elif method == 'POST':
                async with session.post(url, json=json_data, timeout=timeout) as response:
                    if response.status == 401:
                        raise Hysteria2AuthError(f"Authentication failed: {await response.text()}")
                    
                    response.raise_for_status()
                    
                    if response.content_length == 0:
                        return {}
                    
                    return await response.json()
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
        except aiohttp.ClientConnectorError as e:
            raise Hysteria2ConnectionError(f"Connection error: {e}")
        except aiohttp.ClientResponseError as e:
            raise Hysteria2Error(f"HTTP error {e.status}: {e.message}")
        except aiohttp.ClientError as e:
            raise Hysteria2Error(f"Request error: {e}")
        except asyncio.TimeoutError:
            raise Hysteria2ConnectionError(f"Request timed out")
        except json.JSONDecodeError as e:
            raise Hysteria2Error(f"Invalid JSON response: {e}")


# Synchronous wrapper around the async client for backward compatibility
class SyncHysteria2Client:
    """
    Synchronous wrapper around the asynchronous client.
    This provides a compatibility layer for code that doesn't use async/await.
    """
    
    def __init__(self, base_url: str, secret: str = None, timeout: float = 10):
        """Initialize the synchronous client wrapper."""
        self.base_url = base_url
        self.secret = secret
        self.timeout = timeout
        self._async_client = Hysteria2Client(base_url, secret, timeout)
        
    def _run_async(self, coro):
        """Run an async coroutine in a new event loop."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If there is no event loop in this thread, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(coro)
        
    def get_traffic_stats(self, clear: bool = False) -> Dict[str, TrafficStats]:
        """Synchronous version of get_traffic_stats."""
        return self._run_async(self._async_client.get_traffic_stats(clear))
    
    def get_online_clients(self) -> Dict[str, OnlineStatus]:
        """Synchronous version of get_online_clients."""
        return self._run_async(self._async_client.get_online_clients())
    
    def kick_clients(self, client_ids: List[str]) -> bool:
        """Synchronous version of kick_clients."""
        return self._run_async(self._async_client.kick_clients(client_ids))
    
    def __enter__(self):
        """Context manager enter."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._run_async(self._async_client.close())