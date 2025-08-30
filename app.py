import logging
import hmac
import hashlib
import base64
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse

from config import config
from typess import IncomingJob, Platforms, CallbackPayload
from llm import generate_variants
from images import choose_or_create_image

# Import publishers
from publishers.twitter import post_to_twitter
from publishers.linkedin import post_to_linkedin
from publishers.facebook import post_to_facebook
from publishers.pinterest import post_to_pinterest
from publishers.tumblr import post_to_tumblr

# Configure logging
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Social Media Publisher",
    description="Auto-publish WordPress content to social media platforms",
    version="1.0.0"
)

def verify_signature(body: bytes, signature: str) -> bool:
    """Verify HMAC signature of incoming webhook."""
    if not config.WP_WEBHOOK_SECRET:
        logger.error("Webhook secret not configured")
        return False
        
    expected_signature = base64.b64encode(
        hmac.new(
            config.WP_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).digest()
    ).decode()
    
    return hmac.compare_digest(expected_signature, signature)

@app.post("/job")
async def handle_job(request: Request):
    """Handle incoming job from WordPress."""
    # Get and verify signature
    signature = request.headers.get("x-ocsp-signature", "")
    body = await request.body()
    
    if not verify_signature(body, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Parse job data
    try:
        job: IncomingJob = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON: {e}"
        )
    
    logger.info(f"Processing job {job['runId']} for post {job['post']['id']}")
    
    # Generate platform-specific content variants
    try:
        variants = await generate_variants(
            job["post"]["title"],
            job["post"]["url"],
            job["post"]["excerpt"],
            job["post"]["contentHtml"]
        )
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Content generation failed: {e}"}
        )
    
    # Select or generate image
    try:
        media_url = await choose_or_create_image(
            job["post"]["featuredImage"],
            variants["imageIdea"]
        )
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        media_url = None
    
    # Post to each platform
    results = {}
    
    # Twitter
    try:
        if job["dryRun"]:
            results["twitter"] = {
                "status": "skipped",
                "caption": variants["twitter"]
            }
        else:
            results["twitter"] = await post_to_twitter(
                variants["twitter"], 
                media_url
            )
    except Exception as e:
        logger.error(f"Twitter posting failed: {e}")
        results["twitter"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # LinkedIn
    try:
        if job["dryRun"]:
            results["linkedin"] = {
                "status": "skipped",
                "caption": variants["linkedin"]
            }
        else:
            results["linkedin"] = await post_to_linkedin(
                variants["linkedin"], 
                media_url
            )
    except Exception as e:
        logger.error(f"LinkedIn posting failed: {e}")
        results["linkedin"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # Facebook
    try:
        if job["dryRun"]:
            results["facebook"] = {
                "status": "skipped",
                "caption": variants["facebook"]
            }
        else:
            results["facebook"] = await post_to_facebook(
                variants["facebook"], 
                media_url
            )
    except Exception as e:
        logger.error(f"Facebook posting failed: {e}")
        results["facebook"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # Pinterest
    try:
        if job["dryRun"]:
            results["pinterest"] = {
                "status": "skipped",
                "caption": variants["pinterest"]["description"]
            }
        else:
            results["pinterest"] = await post_to_pinterest(
                variants["pinterest"], 
                media_url
            )
    except Exception as e:
        logger.error(f"Pinterest posting failed: {e}")
        results["pinterest"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # Tumblr
    try:
        if job["dryRun"]:
            results["tumblr"] = {
                "status": "skipped",
                "caption": variants["tumblr"]["bodyHtml"]
            }
        else:
            results["tumblr"] = await post_to_tumblr(
                variants["tumblr"], 
                media_url
            )
    except Exception as e:
        logger.error(f"Tumblr posting failed: {e}")
        results["tumblr"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # Send callback to WordPress
    callback_payload: CallbackPayload = {
        "postId": job["post"]["id"],
        "results": results
    }
    
    try:
        from utils.http import http_request
        
        # Sign the callback payload
        callback_body = JSONResponse(callback_payload).body
        callback_signature = base64.b64encode(
            hmac.new(
                config.WP_WEBHOOK_SECRET.encode(),
                callback_body,
                hashlib.sha256
            ).digest()
        ).decode()
        
        # Send callback
        response = await http_request(
            job["callbackUrl"],
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-OCSP-Signature": callback_signature
            },
            data=callback_body
        )
        
        if response.status_code >= 400:
            logger.error(f"Callback failed: {response.status_code} - {response.text}")
        
    except Exception as e:
        logger.error(f"Callback failed: {e}")
    
    return {"status": "processed", "results": results}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=config.DEBUG
    )