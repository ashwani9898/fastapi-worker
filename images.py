import logging
from typing import Optional
from config import config
from utils.http import http_request

logger = logging.getLogger(__name__)

async def choose_or_create_image(
    featured_image: Optional[str], 
    image_idea: Optional[str] = None
) -> Optional[str]:
    """
    Select or generate an image for social media posting.
    Priority: 1. Featured image, 2. Generate new image, 3. None
    """
    # 1. Use featured image if available
    if featured_image:
        logger.info(f"Using featured image: {featured_image}")
        return featured_image
    
    # 2. Generate image if we have an idea and API configured
    if image_idea and config.IMAGE_API_KEY:
        try:
            if config.IMAGE_PROVIDER == "openai":
                from openai import AsyncOpenAI
                
                client = AsyncOpenAI(api_key=config.IMAGE_API_KEY)
                
                response = await client.images.generate(
                    model=config.IMAGE_MODEL,
                    prompt=image_idea[:1000],  # Truncate very long prompts
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                
                image_url = response.data[0].url
                logger.info(f"Generated image: {image_url}")
                return image_url
                
            # Add other image providers here (Stable Diffusion, Midjourney, etc.)
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
    
    # 3. No image available
    return None