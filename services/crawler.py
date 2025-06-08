from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from typing import Dict, Any

def crawl_naver_blog(url: str) -> Dict[str, Any]:
    options = Options()

    # Headless 크롬 설정 (Docker/Render 환경 대응)
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 직접 ChromeDriver 경로 지정 (Dockerfile에 설치된 위치 기준)
    driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options=options)

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
