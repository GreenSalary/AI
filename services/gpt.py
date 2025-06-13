from openai import OpenAI
from typing import Dict, Any
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_with_gpt(content: str, conditions: list) -> Dict[str, Any]:
    prompt = f"""
    다음은 계약 조건입니다:
    {chr(10).join(f"- {c}" for c in conditions)}
    
    아래 블로그 본문에서 각 조건이 충족되었는지 판단해 주세요. 
    각 조건당 "Yes" 또는 "No"만 반환해 주세요. 만약 "No"인 경우, 
    해결책을 제시해 주세요. 조건을 충족했다면, 본문에서 조건을 충족한 근거가 되는 문장 1~2개를 인용해 주세요. 
    "No"인 경우에는 해결책도 반드시 제시해주세요. 

    예시:
    조건: [조건 내용] → Yes 또는 No
    근거 문장: "[본문에서 인용된 문장]"

    블로그 본문:
    {content}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[ 
            {"role": "system", "content": "당신은 계약 이행 분석 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )

    result_text = response.choices[0].message.content
    print("GPT Response:", result_text)  # 디버깅용

    lines = result_text.splitlines()
    condition_results = []
    all_passed = True

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("조건:") and "→" in line:
            try:
                condition_part, result_part = line.split("→", 1)
                condition = condition_part.replace("조건:", "").strip()
                result = result_part.strip()
                quote = "없음"

                # 다음 줄에 근거 문장 또는 해결책이 있으면 추출
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith("근거 문장:"):
                        quote = next_line.replace("근거 문장:", "").strip()
                        i += 1  # 다음 줄을 이미 썼으므로 건너뜀
                    elif next_line.startswith("해결책:"):
                        quote = next_line.replace("해결책:", "").strip()
                        i += 1

                condition_results.append({
                    "condition": condition,
                    "result": result,
                    "quote": quote
                
                })

                if result.lower() != "yes":
                    all_passed = False

            except Exception as e:
                print(f"Error parsing line {i}: {line} -> {e}")
        i += 1

    return {
        "all_passed": all_passed,
        "details": condition_results
    }
