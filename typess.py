from typing import TypedDict, List, Optional, Literal
from datetime import datetime

Platforms = Literal["twitter", "linkedin", "facebook", "pinterest", "tumblr"]

class PostData(TypedDict):
    id: int
    title: str
    url: str
    excerpt: str
    contentHtml: str
    featuredImage: Optional[str]

class IncomingJob(TypedDict):
    runId: str
    dryRun: bool
    ts: str
    callbackUrl: str
    post: PostData

class PublishResult(TypedDict):
    status: Literal["posted", "failed", "skipped", "pending"]
    caption: Optional[str]
    media: Optional[List[str]]
    postId: Optional[str]
    permalink: Optional[str]
    error: Optional[str]

class PinterestVariant(TypedDict):
    title: str
    description: str

class TumblrVariant(TypedDict):
    title: str
    bodyHtml: str
    tags: List[str]

class LLMOutput(TypedDict):
    twitter: str
    linkedin: str
    facebook: str
    pinterest: PinterestVariant
    tumblr: TumblrVariant
    imageIdea: str

class CallbackPayload(TypedDict):
    postId: int
    results: dict[Platforms, PublishResult]