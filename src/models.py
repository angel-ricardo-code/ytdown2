from pydantic import BaseModel
from typing import List, Optional


class VideoFormat(BaseModel):
    format_id: str
    ext: Optional[str]
    url: Optional[str]
    mimeType: Optional[str]
    bitrate: Optional[int]
    width: Optional[int]
    height: Optional[int]
    quality: Optional[str]
    acodec: Optional[str]
    vcodec: Optional[str]
    filesize: Optional[int]


class VideoInfo(BaseModel):
    video_id: str
    title: str
    uploader: Optional[str]
    duration: Optional[int]
    formats: List[VideoFormat]
