from openai import OpenAI
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image_description(prompt_mode, original_dtype, base64_image, crop_dtype, crop_base64_image):
    if prompt_mode == "promptmode1":
        rule = '''확대된 예술 작품의 일부분을 저시력자(low-vision)인 시각장애인에게 설명해주려 한다.
        배경 지식이나 주관적인 해석을 최대한 배제하고, 작품의 소재와 형태를 위주로 묘사하라.
        1. 설명의 순서 및 위치를 밝힌다. (예 : 작품의 좌상단에서부터 묘사하겠습니다.)
        2. 주요 소재를 묘사한다 (예: 6시 방향에 있는 흰색 천 같은 대상은 녹아내린 시계입니다.)
        3. 주요 소재의 형태를 자세히 묘사한다. (예 : 작품 6시 방향 내 시계의 형태)
        4. 작품의 색감을 자세히 묘사한다. (예: 작품의 전반적인 색감, 작품에서 두드러지는 색감 등)
        확대된 이미지만을 묘사하라. 간결성을 위해 모든 원칙을 사용하지 않을 수 있다. 개조식이 아닌, 미술관의 큐레이터가 설명하듯 묘사하라.'''
    else: 
        rule = '''저시력자(low-vision)인 시각장애인이 작품의 분위기를 알 수 있도록, 확대된 예술 작품의 일부를 시로 표현해주려고 한다.
        배경 지식이나 주관적인 해석을 최대한 배제하고, 확대된 이미지만을 묘사하라. 
        ### Rules
        1. 설명의 순서 및 위치를 밝힌다.
        2. 주요 소재, 색감을 자세히 묘사한다.
        3. 시(poem)처럼 표현한다.
        ### Example
        작품의 배경은 가을빛으로 물든 주황빛의 들판입니다. 작품 한가운데에는 따뜻한 느낌을 주는 빨간 지붕의 집이 포근한 안식처처럼 자리하고 있습니다.
        하얀 벽과 작은 창문은 소박하지만 아늑한 느낌을 주며, 고요한 가을날의 평화로움이 가득 담겨 있습니다.
        '''

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 미술품을 간결하게 묘사해주는 미술관 큐레이터입니다."},
                {"role": "user", "content": [
                    {"type": "text", "text" : "다음 작품은 확대되기 전 예술 작품의 이미지이다."},
                    {"type":"image_url", "image_url": {"url":f"data:image/{original_dtype};base64,{base64_image}"}},
                    {"type": "text", "text" : "다음은 확대된 예술 작품의 일부이다."},
                    {"type":"image_url", "image_url": {"url":f"data:image/{crop_dtype};base64,{crop_base64_image}"}},
                    {"type": "text", "text" : rule}
                ]}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def answer_user_prompt(original_dtype, base64_image, crop_dtype, crop_base64_image, user_prompt):
    rule = '''### user query
    {user_query}

    ### task
    확대된 예술 작품의 일부분을 저시력자(low-vision)인 시각장애인에게 설명해주려 한다.
    가능한 한 간결하게 사용자 질문에 응답하라. 필요 시에만 아래의 원칙을 사용해 응답하라.
    배경 지식이나 주관적인 해석을 최대한 배제하고, 작품의 소재와 형태를 위주로 묘사하라.

    ### description rules
    1. 설명의 순서 및 위치를 밝힌다. (예 : 작품의 좌상단에서부터 묘사하겠습니다.)
    2. 주요 소재를 묘사한다 (예: 6시 방향에 있는 흰색 천 같은 대상은 녹아내린 시계입니다.)
    3. 주요 소재의 형태를 자세히 묘사한다. (예 : 작품 6시 방향 내 시계의 형태)
    4. 작품의 색감을 자세히 묘사한다. (예: 작품의 전반적인 색감, 작품에서 두드러지는 색감 등)
    확대된 이미지만을 묘사하라. 간결성을 위해 모든 원칙을 사용하지 않을 수 있다. 개조식이 아닌, 미술관의 큐레이터가 설명하듯 묘사하라.'''

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 미술품을 간결하게 묘사해주는 미술관 큐레이터입니다."},
                {"role": "user", "content": [
                    {"type": "text", "text" : "다음 작품은 확대되기 전 예술 작품의 이미지이다."},
                    {"type":"image_url", "image_url": {"url":f"data:image/{original_dtype};base64,{base64_image}"}},
                    {"type": "text", "text" : "다음은 확대된 예술 작품의 일부이다."},
                    {"type":"image_url", "image_url": {"url":f"data:image/{crop_dtype};base64,{crop_base64_image}"}},
                    {"type": "text", "text" : rule.format(user_query=user_prompt)}
                ]}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))