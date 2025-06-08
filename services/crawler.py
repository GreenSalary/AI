from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import shutil
from typing import Dict, Any

def crawl_naver_blog(url: str) -> Dict[str, Any]:
    options = Options()

    # Chrome binary 경로 자동 탐색 (google-chrome-stable 또는 google-chrome)
    chrome_path = shutil.which("google-chrome-stable") or shutil.which("google-chrome")
    if not chrome_path:
        raise RuntimeError("Chrome binary not found in PATH.")

    options.binary_location = chrome_path
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # ChromeDriver 경로 명시 (Dockerfile에서 /usr/local/bin/chromedriver로 설치됨)
    service = Service("/usr/local/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(3)
        driver.switch_to.frame("mainFrame")
        time.sleep(1)

        try:
            content_container = driver.find_element(By.CSS_SELECTOR, ".se-main-container")
        except:
            content_container = driver.find_element(By.CSS_SELECTOR, "#postViewArea")

        content = content_container.text
        images = content_container.find_elements(By.TAG_NAME, "img")

        return {
            "content": content,
            "image_count": len(images),
            "char_count": len(content)
        }

    except Exception as e:
        raise RuntimeError(f"Crawling error: {e}")

    finally:
        driver.quit()
