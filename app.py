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
import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.mount("/results", StaticFiles(directory="./results"), name="results")
app.mount("/images", StaticFiles(directory="./images"), name="images")  

@app.get("/")
async def root():
    return {"message": "Hello! FastAPI 서버가 정상 작동 중입니다."}

def convert_pdf_to_images(pdf_path: str, output_folder: str):
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        
        image_filename = f"page_{uuid.uuid4().hex}.png"
        image_path = os.path.join(output_folder, image_filename)
        pix.save(image_path)
        image_paths.append(image_path)
    
    return image_paths

@app.post("/analyze")
def analyze_contract(data: ContractRequest):
    try:
        blog_data = crawl_naver_blog(data.site_url)

        keyword_test = check_keywords(blog_data["content"], data.keywords)
        missing_keywords = get_missing_keywords(blog_data["content"], data.keywords)
        word_count_test = blog_data["char_count"] >= data.media_text
        image_count_test = blog_data["image_count"] >= data.media_image
        gpt_result = analyze_with_gpt(blog_data["content"], data.conditions)

        os.makedirs("./results", exist_ok=True) 
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
        
        os.makedirs("./images", exist_ok=True)
        image_paths = convert_pdf_to_images(pdf_path, "./images")
        image_urls = [f"/images/{os.path.basename(image_path)}" for image_path in image_paths]

        return {
            "keywordTest": keyword_test,
            "conditionTest": gpt_result["all_passed"],
            "wordCountTest": word_count_test,
            "imageCountTest": image_count_test,
            "pdf_url": f"/results/{pdf_filename}",  # PDF 경로
            "image_urls": image_urls  # 이미지 경로 반환
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
