# app.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from models.contract import ContractRequest
from services.crawler import crawl_naver_blog
from services.gpt import analyze_with_gpt
from services.pdf import create_pdf_report
from services.utils import check_keywords, get_missing_keywords
import os
import uuid
import fitz  # PyMuPDF
from dotenv import load_dotenv
import shutil

load_dotenv()
app = FastAPI()

app.mount("/results", StaticFiles(directory="./results"), name="results")
app.mount("/images", StaticFiles(directory="./images"), name="images") 

UPLOAD_FOLDER = "./uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.mount("/uploaded_images", StaticFiles(directory=UPLOAD_FOLDER), name="uploaded_images")


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

        os.makedirs("./images", exist_ok=True) 
        image_paths = convert_pdf_to_images(pdf_path, "./images")

        # 이미지들 업로드하고 URL 받기
        pdf_images_url = []
        api_image_upload_url = os.getenv("API_IMAGE_UPLOAD_URL")

        for image_path in image_paths:
            with open(image_path, "rb") as f:
                files = {
                    "image": (os.path.basename(image_path), f, "image/png")
                }
                res = requests.post(api_image_upload_url, files=files)
                res.raise_for_status()
                image_url = res.json()["imageUrl"]
                pdf_images_url.append(image_url)
        
        return {
            "keywordTest": keyword_test,
            "conditionTest": gpt_result["all_passed"],
            "wordCountTest": word_count_test,
            "imageCountTest": image_count_test,
            "pdf_url": f"/results/{pdf_filename}",  
            "image_urls": pdf_images_url  
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/image")
async def upload_image(image: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_FOLDER, image.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/uploaded_images/{image.filename}"
        return JSONResponse(content={"imageUrl": image_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
