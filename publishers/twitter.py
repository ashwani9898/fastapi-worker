import logging
from typing import List, Optional
from typess import PublishResult
from config import config
from utils.http import http_request

logger = logging.getLogger(__name__)

async def upload_media_to_twitter(media_url: str) -> Optional[str]:
    """Upload media to Twitter and return media_id."""
    if not all([config.TWITTER_API_KEY, config.TWITTER_API_SECRET, 
                config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_SECRET]):
        logger.error("Twitter API credentials not configured")
        return None
    
    try:
        # In a real implementation, you would use the Twitter API v2
        # with proper OAuth 1.0a authentication to upload media
        # This is a simplified example
        
        # Step 1: Download the image
        response = await http_request(media_url, "GET")
        if response.status_code != 200:
            logger.error(f"Failed to download image: {response.status_code}")
            return None
            
        media_data = response.content
        
        # Step 2: Upload to Twitter (pseudo-code)
        # media_id = twitter_api.media_upload(media_data)
        # return media_id
        
        logger.warning("Twitter media upload not fully implemented")
        return "dummy_media_id"
        
    except Exception as e:
        logger.error(f"Twitter media upload failed: {e}")
        return None

async def post_to_twitter(caption: str, media_url: Optional[str] = None) -> PublishResult:
    """Post content to Twitter/X."""
    if not all([config.TWITTER_API_KEY, config.TWITTER_API_SECRET, 
                config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_SECRET]):
        return PublishResult(
            status="failed",
            error="Twitter API credentials not configured"
        )
    
    try:
        # Upload media if provided
        media_id = None
        if media_url:
            media_id = await upload_media_to_twitter(media_url)
        
        # Prepare tweet payload
        tweet_data = {"text": caption[:280]}
        if media_id:
            tweet_data["media"] = {"media_ids": [media_id]}
        
        # Post tweet (pseudo-code)
        # response = twitter_api.create_tweet(**tweet_data)
        # tweet_id = response.data["id"]
        
        logger.warning("Twitter posting not fully implemented")
        
        return PublishResult(
            status="posted",
            caption=caption,
            media=[media_url] if media_url else None,
            postId="dummy_tweet_id",
            permalink="https://twitter.com/user/status/dummy_tweet_id"
        )
        
    except Exception as e:
        logger.error(f"Twitter posting failed: {e}")
        return PublishResult(
            status="failed",
            error=str(e)
        )