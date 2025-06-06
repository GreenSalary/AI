from typing import List

def check_keywords(content: str, keywords: List[str]) -> bool:
    return all(kw.lower() in content.lower() for kw in keywords)

def get_missing_keywords(content: str, keywords: List[str]) -> List[str]:
    content_lower = content.lower()
    return [kw for kw in keywords if kw.lower() not in content_lower]
