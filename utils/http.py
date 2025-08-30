import httpx
import asyncio
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

async def http_request(
    url: str, 
    method: str = "GET", 
    headers: Dict[str, str] = None, 
    json: Any = None,
    data: Any = None,
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> httpx.Response:
    """
    Make an HTTP request with retry logic for transient errors.
    """
    headers = headers or {}
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    data=data,
                    timeout=timeout
                )
                
                # Retry on server errors and rate limits
                if response.status_code >= 500 or response.status_code == 429:
                    raise httpx.HTTPError(f"Server error: {response.status_code}")
                    
                return response
                
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            retry_count += 1
            if retry_count > max_retries:
                logger.error(f"HTTP request failed after {max_retries} retries: {e}")
                raise
                
            logger.warning(f"HTTP request failed (attempt {retry_count}/{max_retries}), retrying in {retry_delay}s: {e}")
            await asyncio.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff