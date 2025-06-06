import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from typing import Dict, Any

def crawl_naver_blog(url: str) -> Dict[str, Any]:
    # Render에서 설정한 CHROME_BIN 환경 변수를 참조
    os.environ["CHROME_BIN"] = os.getenv("CHROME_BIN", "/usr/bin/chromium")

    options = Options()
    options.add_argument("--headless")  # UI 없이 실행
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = webdriver.chrome.service.Service(ChromeDriverManager().install())
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
