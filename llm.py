import json
import logging
from typing import Dict, Any
from typess import LLMOutput
from config import config

logger = logging.getLogger(__name__)

async def generate_variants(
    title: str, 
    url: str, 
    excerpt: str, 
    html: str
) -> LLMOutput:
    """
    Generate platform-specific content variants using LLM.
    """
    system_prompt = """You format social media copy. Return strict JSON matching this schema:
{
  "twitter": "string (<= 280 chars, 1-2 relevant hashtags)",
  "linkedin": "string (professional tone, 1-2 sentences + link)",
  "facebook": "string (friendly tone, can be longer)",
  "pinterest": {"title": "string (<= 100 chars)", "description": "string (100-300 chars)"},
  "tumblr": {"title": "string", "bodyHtml": "string (can include HTML)", "tags": ["string"]},
  "imageIdea": "string (prompt for image generation)"
}

Rules:
- Twitter: <= 280 chars, include 1-2 relevant hashtags, can use 1 emoji max
- LinkedIn: Professional tone, value-forward, 1-2 sentences + link, no emojis
- Facebook: Friendly tone, can be longer, up to 2 emojis
- Pinterest: Description should be 100-300 chars, include 3 discovery keywords at end
- Tumblr: Can include HTML formatting, relevant tags
- Use the provided article URL exactly once per platform
- Avoid clickbait, maintain authentic voice"""
    
    user_content = f"""Article:
Title: {title}
URL: {url}
Excerpt: {excerpt}
Content: {html[:6000]}  # Truncate very long content"""

    try:
        if config.LLM_PROVIDER == "openai":
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=config.LLM_API_KEY)
            
            response = await client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=config.LLM_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Validate the structure
            return LLMOutput(
                twitter=result["twitter"],
                linkedin=result["linkedin"],
                facebook=result["facebook"],
                pinterest=result["pinterest"],
                tumblr=result["tumblr"],
                imageIdea=result["imageIdea"]
            )
            
        else:
            # Add support for other LLM providers (Anthropic, Cohere, etc.)
            raise ValueError(f"Unsupported LLM provider: {config.LLM_PROVIDER}")
            
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        # Fallback to simple generation
        return generate_fallback_variants(title, url, excerpt)

def generate_fallback_variants(title: str, url: str, excerpt: str) -> LLMOutput:
    """Fallback content generation if LLM fails."""
    truncated_excerpt = excerpt[:100] + "..." if len(excerpt) > 100 else excerpt
    
    return LLMOutput(
        twitter=f"{title[:200]}... {url}",
        linkedin=f"{title}\n\n{truncated_excerpt}\n\nRead more: {url}",
        facebook=f"Check out our new post: {title}\n\n{truncated_excerpt}\n\n{url}",
        pinterest={"title": title[:100], "description": f"{truncated_excerpt} | Read more: {url}"},
        tumblr={"title": title, "bodyHtml": f"<p>{truncated_excerpt}</p><p><a href='{url}'>Read more</a></p>", "tags": ["blog", "article"]},
        imageIdea=f"Visual representation of: {title}"
    )