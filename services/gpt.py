from openai import OpenAI
from typing import Dict, Any
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_with_gpt(content: str, conditions: list) -> Dict[str, Any]:
    prompt = f"""
    다음은 계약 조건입니다:
    {chr(10).join(f"- {c}" for c in conditions)}

    아래 블로그 본문에서 각 조건이 충족되었는지 판단해 주세요. 
    각 조건당 "Yes" 또는 "No"만 반환해 주세요. 다음 예시처럼:

    조건: [조건 내용] → Yes 또는 No
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 계약 이행 분석 전문가입니다."},
            {"role": "user", "content": prompt + "\n\n블로그 본문:\n" + content}
        ],
        temperature=0,
    )
    result_text = response.choices[0].message.content

    condition_results = []
    all_yes = True
    for line in result_text.splitlines():
        if "→" in line:
            try:
                cond_text, res = line.split("→")
                cond_text = cond_text.replace("조건:", "").strip()
                res = res.strip()
                condition_results.append({
                    "condition": cond_text,
                    "result": res
                })
                if res.lower() != "yes":
                    all_yes = False
            except:
                pass

    return {
        "all_passed": all_yes,
        "details": condition_results
    }
