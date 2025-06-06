from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List

def create_pdf_report(file_path: str, contract_title: str, influencer_name: str, site_url: str,
                      keyword_test: bool, condition_test: bool, word_count_test: bool, image_count_test: bool,
                      condition_details: list, missing_keywords: List[str]):
    if 'NanumGothic' not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont('NanumGothic', 'NanumGothic-Regular.ttf'))

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()

    for style_name in styles.byName:
        styles[style_name].fontName = 'NanumGothic'

    story = []
    story.append(Paragraph(f"<b>광고 이름</b><br/>{contract_title}", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>인플루언서 이름</b><br/>{influencer_name}", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>URL</b><br/>{site_url}", styles['Normal']))
    story.append(Spacer(1, 24))

    data = [
        ["검사 항목", "충족 여부"],
        ["키워드 포함", "O" if keyword_test else "X"],
        ["세부 조건", "O" if condition_test else "X"],
        ["글자 수", "O" if word_count_test else "X"],
        ["이미지 수", "O" if image_count_test else "X"],
    ]

    table = Table(data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'NanumGothic'),
    ]))

    story.append(table)
    story.append(Spacer(1, 24))

    if not keyword_test and missing_keywords:
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>누락된 키워드</b>", styles['Heading3']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(", ".join(missing_keywords), styles['Normal']))
        story.append(Spacer(1, 12))

    story.append(Paragraph("<b>조건 상세 분석</b>", styles['Heading2']))
    story.append(Spacer(1, 12))

    for idx, cond in enumerate(condition_details, 1):
        cond_text = cond.get("condition", "")
        result = cond.get("result", "")
        symbol = "✅" if result.lower() == "yes" else "❌"
        story.append(Paragraph(f"{idx}. 조건: {cond_text} → {symbol} ({result})", styles['Normal']))
        story.append(Spacer(1, 6))

    doc.build(story)
