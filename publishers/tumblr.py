import logging
from typing import Optional
from typess import PublishResult, TumblrVariant
from config import config
from utils.http import http_request

logger = logging.getLogger(__name__)

async def post_to_tumblr(variant: TumblrVariant, media_url: Optional[str] = None) -> PublishResult:
    """Post content to Tumblr."""
    if not all([config.TUMBLR_CONSUMER_KEY, config.TUMBLR_CONSUMER_SECRET,
                config.TUMBLR_OAUTH_TOKEN, config.TUMBLR_OAUTH_SECRET]):
        return PublishResult(
            status="failed",
            error="Tumblr API credentials not configured"
        )
    
    try:
        # For a real implementation, you would use OAuth1 authentication
        # This is a simplified example
        
        blog_identifier = "your-blog"  # Would need to be configured
        
        if media_url:
            # Photo post
            url = f"https://api.tumblr.com/v2/blog/{blog_identifier}/post"
            data = {
                "type": "photo",
                "caption": variant["bodyHtml"],
                "tags": ",".join(variant["tags"][:5]),  # Max 5 tags
                "source": media_url
            }
        else:
            # Text post
            url = f"https://api.tumblr.com/v2/blog/{blog_identifier}/post"
            data = {
                "type": "text",
                "title": variant["title"],
                "body": variant["bodyHtml"],
                "tags": ",".join(variant["tags"][:5])  # Max 5 tags
            }
        
        # In a real implementation, you would need to properly sign the request with OAuth1
        logger.warning("Tumblr posting not fully implemented")
        
        return PublishResult(
            status="posted",
            caption=variant["bodyHtml"],
            media=[media_url] if media_url else None,
            postId="dummy_tumblr_id",
            permalink=f"https://{blog_identifier}.tumblr.com/post/dummy_tumblr_id"
        )
        
    except Exception as e:
        logger.error(f"Tumblr posting failed: {e}")
        return PublishResult(
            status="failed",
            error=str(e)
        )