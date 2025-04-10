import json
import logging
from typing import Dict, List, Optional, Union
import requests
from urllib.parse import urljoin

from .exceptions import Hysteria2Error, Hysteria2AuthError, Hysteria2ConnectionError
from .models import TrafficStats, OnlineStatus

logger = logging.getLogger(__name__)


class Hysteria2Client:
    """Client for the Hysteria2 API."""

    def __init__(self, base_url: str, secret: str = None, timeout: int = 10):
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
        self._session = requests.Session()
        if secret:
            self._session.headers.update({'Authorization': secret})

    def get_traffic_stats(self, clear: bool = False) -> Dict[str, TrafficStats]:
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
            response = self._make_request('GET', endpoint)
            return {client_id: TrafficStats.from_dict(stats) 
                   for client_id, stats in response.items()}
        except Exception as e:
            logger.error(f"Failed to get traffic statistics: {e}")
            raise

    def get_online_clients(self) -> Dict[str, OnlineStatus]:
        """
        Get online status for all clients.

        Returns:
            Dictionary mapping client IDs to their online status
        """
        try:
            response = self._make_request('GET', '/online')
            return {client_id: OnlineStatus.from_int(connections) 
                   for client_id, connections in response.items()}
        except Exception as e:
            logger.error(f"Failed to get online clients: {e}")
            raise

    def kick_clients(self, client_ids: List[str]) -> bool:
        """
        Kick clients by their IDs.

        Args:
            client_ids: List of client IDs to kick

        Returns:
            True if successful, raises an exception otherwise
        """
        try:
            self._make_request('POST', '/kick', json_data=client_ids)
            return True
        except Exception as e:
            logger.error(f"Failed to kick clients {client_ids}: {e}")
            raise

    def _make_request(self, method: str, endpoint: str, json_data: Optional[Union[Dict, List]] = None) -> Dict:
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
        
        try:
            if method == 'GET':
                response = self._session.get(url, timeout=self.timeout)
            elif method == 'POST':
                response = self._session.post(url, json=json_data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code == 401:
                raise Hysteria2AuthError(f"Authentication failed: {response.text}")
            
            response.raise_for_status()
            
            if not response.text:
                return {}
            
            return response.json()
            
        except requests.exceptions.ConnectionError as e:
            raise Hysteria2ConnectionError(f"Connection error: {e}")
        except requests.exceptions.Timeout as e:
            raise Hysteria2ConnectionError(f"Request timed out: {e}")
        except requests.exceptions.RequestException as e:
            raise Hysteria2Error(f"Request error: {e}")
        except json.JSONDecodeError as e:
            raise Hysteria2Error(f"Invalid JSON response: {e}")