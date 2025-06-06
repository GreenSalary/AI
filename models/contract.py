from pydantic import BaseModel
from typing import List

class ContractRequest(BaseModel):
    contract_title: str
    influencer_name: str
    site_url: str
    image_url: str
    keywords: List[str]
    conditions: List[str]
    media_text: int
    media_image: int
