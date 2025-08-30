import logging
from typing import Optional
from typess import PublishResult
from config import config
from utils.http import http_request

logger = logging.getLogger(__name__)

async def post_to_facebook(caption: str, media_url: Optional[str] = None) -> PublishResult:
    """Post content to Facebook."""
    if not all([config.FACEBOOK_PAGE_ACCESS_TOKEN, config.FACEBOOK_PAGE_ID]):
        return PublishResult(
            status="failed",
            error="Facebook API credentials not configured"
        )
    
    try:
        if media_url:
            # Post with image
            url = f"https://graph.facebook.com/v19.0/{config.FACEBOOK_PAGE_ID}/photos"
            data = {
                "message": caption,
                "url": media_url,  # Facebook can download from URL
                "access_token": config.FACEBOOK_PAGE_ACCESS_TOKEN
            }
        else:
            # Post without image
            url = f"https://graph.facebook.com/v19.0/{config.FACEBOOK_PAGE_ID}/feed"
            data = {
                "message": caption,
                "access_token": config.FACEBOOK_PAGE_ACCESS_TOKEN
            }
        
        response = await http_request(
            url,
            method="POST",
            data=data
        )
        
        if response.status_code == 200:
            response_data = response.json()
            post_id = response_data.get("id") or response_data.get("post_id")
            
            return PublishResult(
                status="posted",
                caption=caption,
                media=[media_url] if media_url else None,
                postId=post_id,
                permalink=f"https://facebook.com/{post_id}"
            )
        else:
            error_msg = f"Facebook API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return PublishResult(
                status="failed",
                error=error_msg
            )
            
    except Exception as e:
        logger.error(f"Facebook posting failed: {e}")
        return PublishResult(
            status="failed",
            error=str(e)
        )