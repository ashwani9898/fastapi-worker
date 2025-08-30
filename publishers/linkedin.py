import logging
from typing import Optional
from typess import PublishResult
from config import config
from utils.http import http_request

logger = logging.getLogger(__name__)

async def post_to_linkedin(caption: str, media_url: Optional[str] = None) -> PublishResult:
    """Post content to LinkedIn."""
    if not config.LINKEDIN_ACCESS_TOKEN:
        return PublishResult(
            status="failed",
            error="LinkedIn access token not configured"
        )
    
    try:
        # LinkedIn API requires a specific format for UGC posts
        # This is a simplified example
        
        headers = {
            "Authorization": f"Bearer {config.LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Prepare the post content
        post_data = {
            "author": f"urn:li:person:{config.LINKEDIN_USER_ID}",  # Would need to be configured
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": caption
                    },
                    "shareMediaCategory": "NONE" if not media_url else "IMAGE",
                    "media": [{
                        "status": "READY",
                        "description": {
                            "text": caption[:200]  # Truncated description
                        },
                        "media": media_url,
                        "title": {
                            "text": "Post Image"
                        }
                    }] if media_url else []
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Make the API request
        response = await http_request(
            "https://api.linkedin.com/v2/ugcPosts",
            method="POST",
            headers=headers,
            json=post_data
        )
        
        if response.status_code == 201:
            response_data = response.json()
            post_id = response_data.get("id")
            
            return PublishResult(
                status="posted",
                caption=caption,
                media=[media_url] if media_url else None,
                postId=post_id,
                permalink=f"https://www.linkedin.com/feed/update/{post_id}"
            )
        else:
            error_msg = f"LinkedIn API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return PublishResult(
                status="failed",
                error=error_msg
            )
            
    except Exception as e:
        logger.error(f"LinkedIn posting failed: {e}")
        return PublishResult(
            status="failed",
            error=str(e)
        )