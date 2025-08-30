import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Server settings
    PORT = int(os.getenv("PORT", 8080))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    WP_WEBHOOK_SECRET = os.getenv("WP_WEBHOOK_SECRET")
    
    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-1106-preview")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
    
    # Image Generation
    IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai")
    IMAGE_API_KEY = os.getenv("IMAGE_API_KEY")
    IMAGE_MODEL = os.getenv("IMAGE_MODEL", "dall-e-3")
    
    # Social Media API Keys (should use proper secret management in production)
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
    
    LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
    FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
    
    PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")
    PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")
    
    TUMBLR_CONSUMER_KEY = os.getenv("TUMBLR_CONSUMER_KEY")
    TUMBLR_CONSUMER_SECRET = os.getenv("TUMBLR_CONSUMER_SECRET")
    TUMBLR_OAUTH_TOKEN = os.getenv("TUMBLR_OAUTH_TOKEN")
    TUMBLR_OAUTH_SECRET = os.getenv("TUMBLR_OAUTH_SECRET")

config = Config()