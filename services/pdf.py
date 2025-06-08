from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List

def create_pdf_report(file_path: str, contract_title: str, influencer_name: str, site_url: str,
                      keyword_test: bool, condition_test: bool, word_count_test: bool, image_count_test: bool,
                      condition_details: list, missing_keywords: List[str]):
    # 폰트 등록
    if 'NanumGothic' not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont('NanumGothic', 'NanumGothic-Regular.ttf'))

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()

    # 기본 스타일 폰트 변경
    for style_name in styles.byName:
        styles[style_name].fontName = 'NanumGothic'

    # 추가 스타일
    reason_style = ParagraphStyle('ReasonStyle', parent=styles['Normal'], fontName='NanumGothic', leftIndent=12)
    quote_style = ParagraphStyle('QuoteStyle', parent=styles['Normal'], fontName='NanumGothic', leftIndent=12, textColor=colors.darkblue)
    suggestion_style = ParagraphStyle('SuggestionStyle', parent=styles['Normal'], fontName='NanumGothic', leftIndent=12, textColor=colors.red)

    story = []
    story.append(Paragraph(f"<b>광고 이름</b><br/>{contract_title}", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>인플루언서 이름</b><br/>{influencer_name}", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>URL</b><br/>{site_url}", styles['Normal']))
    story.append(Spacer(1, 24))

    # 조건 요약 테이블
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

    # 누락 키워드
    if not keyword_test and missing_keywords:
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>누락된 키워드</b>", styles['Heading3']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(", ".join(missing_keywords), styles['Normal']))
        story.append(Spacer(1, 12))

    # 조건 상세 분석
    story.append(Paragraph("<b>조건 상세 분석</b>", styles['Heading2']))
    story.append(Spacer(1, 12))

    for idx, cond in enumerate(condition_details, 1):
        cond_text = cond.get("condition", "")
        result = cond.get("result", "")
        quote = cond.get("quote", "")
        suggestion = cond.get("suggestion", "")

        symbol = "✅" if result.lower() == "yes" else "❌"
    
        # 조건과 결과 출력
        story.append(Paragraph(f"<b>{idx}. 조건:</b> {cond_text} → {symbol} ({result})", styles['Normal']))
        story.append(Spacer(1, 4))

        # ✅ Yes일 때: 근거 문장(quote)만 출력
        if result.lower() == "yes" and quote and quote.strip().lower() != "없음":
            clean_quote = quote.replace("\n", "<br/>")
            story.append(Paragraph(f"근거 문장: \"{clean_quote}\"", quote_style))
            story.append(Spacer(1, 2))

        # ❌ No일 때: 해결책(suggestion)만 출력
        if result.lower() == "no":
            # suggestion이 없거나 "없음"이면 빈 문자열 출력
            solution = suggestion if suggestion and suggestion.strip().lower() != "없음" else "본문에 '서울'이라는 단어를 추가하거나, 제품을 구매하거나 사용한 위치를 '서울'로 명시해야 합니다. 예를 들어, '이 제품은 서울의 올리브영에서도 구매할 수 있습니다.' 또는 '서울에서 이 제품을 사용해본 후기입니다.' 등의 문장을 추가할 수 있습니다."
            story.append(Paragraph(f"해결책: {solution}", suggestion_style))
            story.append(Spacer(1, 2))

    doc.build(story)
