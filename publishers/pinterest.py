import logging
from typing import Optional
from typess import PublishResult, PinterestVariant
from config import config
from utils.http import http_request

logger = logging.getLogger(__name__)

async def post_to_pinterest(variant: PinterestVariant, media_url: Optional[str] = None) -> PublishResult:
    """Post content to Pinterest."""
    if not all([config.PINTEREST_ACCESS_TOKEN, config.PINTEREST_BOARD_ID]):
        return PublishResult(
            status="failed",
            error="Pinterest API credentials not configured"
        )
    
    if not media_url:
        return PublishResult(
            status="failed",
            error="Pinterest requires an image"
        )
    
    try:
        headers = {
            "Authorization": f"Bearer {config.PINTEREST_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        pin_data = {
            "title": variant["title"][:100],
            "description": variant["description"][:500],
            "board_id": config.PINTEREST_BOARD_ID,
            "media_source": {
                "source_type": "image_url",
                "url": media_url
            }
        }
        
        response = await http_request(
            "https://api.pinterest.com/v5/pins",
            method="POST",
            headers=headers,
            json=pin_data
        )
        
        if response.status_code == 201:
            response_data = response.json()
            pin_id = response_data.get("id")
            
            return PublishResult(
                status="posted",
                caption=variant["description"],
                media=[media_url],
                postId=pin_id,
                permalink=response_data.get("url", f"https://pinterest.com/pin/{pin_id}")
            )
        else:
            error_msg = f"Pinterest API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return PublishResult(
                status="failed",
                error=error_msg
            )
            
    except Exception as e:
        logger.error(f"Pinterest posting failed: {e}")
        return PublishResult(
            status="failed",
            error=str(e)
        )