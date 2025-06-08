import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
import re

def crawl_naver_blog(url: str) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/113.0.0.0 Safari/537.36"
    }

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch page, status code: {resp.status_code}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # iframe이 있으면 iframe src 추출 후 다시 요청 시도
    iframe = soup.find("iframe", {"name": "mainFrame"})
    if iframe and iframe.has_attr("src"):
        iframe_url = iframe["src"]
        if iframe_url.startswith("/"):
            from urllib.parse import urljoin
            iframe_url = urljoin(url, iframe_url)

        resp = requests.get(iframe_url, headers=headers)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch iframe page, status code: {resp.status_code}")
        soup = BeautifulSoup(resp.text, "html.parser")

    content_container = soup.select_one(".se-main-container") or soup.select_one("#postViewArea")
    if not content_container:
        raise RuntimeError("Failed to find blog content container")

    content = content_container.get_text(separator="\n").strip()

    # 불필요한 빈 줄 줄이기 (연속된 빈 줄 2줄로 축소)
    content = re.sub(r'\n\s*\n+', '\n\n', content)

    # 각 줄별 앞뒤 공백 제거 및 완전 빈 줄 제거
    lines = content.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip() != '']
    content = '\n'.join(cleaned_lines)

    images = content_container.find_all("img")

    print(content)

    return {
        "content": content,
        "image_count": len(images),
        "char_count": len(content)
    }
