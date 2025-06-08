# uvicorn app:app --reload
# .\greensalary\Scripts\Activate.ps1

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from models.contract import ContractRequest
from services.crawler import crawl_naver_blog
from services.gpt import analyze_with_gpt
from services.pdf import create_pdf_report
from services.utils import check_keywords, get_missing_keywords
import os
import uuid
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# 예시: OpenAI API 키 사용
openai_api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# 정적 파일 경로 설정
app.mount("/results", StaticFiles(directory="./results"), name="results")

@app.get("/")
async def root():
    return {"message": "Hello! FastAPI 서버가 정상 작동 중입니다."}

@app.post("/analyze")
def analyze_contract(data: ContractRequest):
    try:
        blog_data = crawl_naver_blog(data.site_url)

        keyword_test = check_keywords(blog_data["content"], data.keywords)
        missing_keywords = get_missing_keywords(blog_data["content"], data.keywords)
        word_count_test = blog_data["char_count"] >= data.media_text
        image_count_test = blog_data["image_count"] >= data.media_image
        gpt_result = analyze_with_gpt(blog_data["content"], data.conditions)

        os.makedirs("./results", exist_ok=True)  # 디렉토리 확인 후 생성
        pdf_filename = f"result_{uuid.uuid4().hex}.pdf"
        pdf_path = os.path.join("./results", pdf_filename)

        create_pdf_report(
            pdf_path,
            data.contract_title,
            data.influencer_name,
            data.site_url,
            keyword_test,
            gpt_result["all_passed"],
            word_count_test,
            image_count_test,
            gpt_result["details"],
            missing_keywords
        )

        # 정적 경로로 PDF 경로 반환
        pdf_url = f"/results/{pdf_filename}"

        return {
            "keywordTest": keyword_test,
            "conditionTest": gpt_result["all_passed"],
            #"conditionDetail": gpt_result["details"],
            "wordCountTest": word_count_test,
            "imageCountTest": image_count_test,
            "pdf_url": pdf_url,  # 정적 경로로 반환
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
