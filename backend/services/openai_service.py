from openai import OpenAI
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image_description(prompt_mode, original_dtype, base64_image, crop_dtype, crop_base64_image):
    if prompt_mode == "promptmode1":
        rule = '''You are to describe an enlarged section of an artwork to a low-vision individual who is visually impaired.
        Your description must primarily focus on the subject matter and form of the artwork, strictly excluding background knowledge or subjective interpretation.

        The description should follow these guidelines:

        1. State the sequence and location of the description. (e.g., I will begin the description from the upper-left corner of the artwork.)
        2. Describe the main subjects (e.g., The white, cloth-like object at the six o'clock position is a melting clock.)
        3. Describe the form of the main subjects in detail. (e.g., The form of the clock within the six o'clock position of the work.)
        4. Describe the colors of the work in detail. (e.g., The overall color palette of the work, and the most prominent colors.)

        Only describe the enlarged image. All principles may not be used for brevity. 
        The description should not be presented in bullet points, but rather delivered in a narrative style, as a museum curator would explain it.'''
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
                {"role": "system", "content": "You are a museum curator who provides concise descriptions of artworks."},
                {"role": "user", "content": [
                    {"type": "text", "text" : "Here is the original image of the artwork."},
                    {"type":"image_url", "image_url": {"url":f"data:image/{original_dtype};base64,{base64_image}"}},
                    {"type": "text", "text" : "The following is a magnified portion of the artwork."},
                    {"type":"image_url", "image_url": {"url":f"data:image/{crop_dtype};base64,{crop_base64_image}"}},
                    {"type": "text", "text" : rule}
                ]}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def answer_user_prompt(prompt_mode, original_dtype, base64_image, crop_dtype, crop_base64_image, user_prompt):
    if prompt_mode == "promptmode1":
        rule = '''### USER QUESTION 
        {user_query}
        
        ### TASK
        Answer the given question as brief as possible.
        Consider that the user might be blind or low-vision.
        Exclude background knowledge and subjective interpretations as much as possible, 
        and you may respond that you cannot answer if the information is not objective.
        Describe only the magnified image.
        Use narrative prose, as if you were a museum curator explaining the piece, 
        rather than an outline or fragmented style.
        '''
    else:
        rule = '''### USER QUESTION 
        {user_query}
        
        ### TASK
        Answer the given question as brief as possible.
        Provide a description that allows individuals who are blind or have low vision to experience the mood of the artwork.
        Exclude background knowledge and subjective interpretations as much as possible.
        Describe only the magnified image.
        Use poetic and narrative prose, as if you were a museum curator explaining the piece, 
        rather than an outline or fragmented style.
        '''
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a museum curator who provides concise descriptions of artworks."},
                {"role": "user", "content": [
                    {"type": "text", "text" : "Here is the original image of the artwork."},
                    {"type":"image_url", "image_url": {"url":f"data:image/{original_dtype};base64,{base64_image}"}},
                    {"type": "text", "text" : "The following is a magnified portion of the artwork."},
                    {"type":"image_url", "image_url": {"url":f"data:image/{crop_dtype};base64,{crop_base64_image}"}},
                    {"type": "text", "text" : rule.format(user_query=user_prompt)}
                ]}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def answer_user_prompt_no_original(prompt_mode, crop_dtype, crop_base64_image, user_prompt):
    if prompt_mode == "promptmode1":
        rule = '''### USER QUESTION 
        {user_query}
        
        ### TASK
        Answer the given question as brief as possible.
        Consider that the user might be blind or low-vision.
        Exclude background knowledge and subjective interpretations as much as possible, 
        and you may respond that you cannot answer if the information is not objective.
        Describe only the magnified image.
        Use narrative prose, as if you were a museum curator explaining the piece, 
        rather than an outline or fragmented style.
        '''
    else:
        rule = '''### USER QUESTION 
        {user_query}
        
        ### TASK
        Answer the given question as brief as possible.
        Provide a description that allows individuals who are blind or have low vision to experience the mood of the artwork.
        Exclude background knowledge and subjective interpretations as much as possible.
        Describe only the magnified image.
        Use poetic and narrative prose, as if you were a museum curator explaining the piece, 
        rather than an outline or fragmented style.
        '''
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a museum curator who provides concise descriptions of artworks."},
                {"role": "user", "content": [
                    {"type": "text", "text" : "The following is a magnified portion of the artwork."},
                    {"type":"image_url", "image_url": {"url":f"data:image/{crop_dtype};base64,{crop_base64_image}"}},
                    {"type": "text", "text" : rule.format(user_query=user_prompt)}
                ]}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # rule = '''### user query
    # {user_query}

    # ### task
    # 확대된 예술 작품의 일부분을 저시력자(low-vision)인 시각장애인에게 설명해주려 한다.
    # 가능한 한 간결하게 사용자 질문에 응답하라. 필요 시에만 아래의 원칙을 사용해 응답하라.
    # 배경 지식이나 주관적인 해석을 최대한 배제하고, 작품의 소재와 형태를 위주로 묘사하라.

    # ### description rules
    # 1. 설명의 순서 및 위치를 밝힌다. (예 : 작품의 좌상단에서부터 묘사하겠습니다.)
    # 2. 주요 소재를 묘사한다 (예: 6시 방향에 있는 흰색 천 같은 대상은 녹아내린 시계입니다.)
    # 3. 주요 소재의 형태를 자세히 묘사한다. (예 : 작품 6시 방향 내 시계의 형태)
    # 4. 작품의 색감을 자세히 묘사한다. (예: 작품의 전반적인 색감, 작품에서 두드러지는 색감 등)
    # 확대된 이미지만을 묘사하라. 간결성을 위해 모든 원칙을 사용하지 않을 수 있다. 개조식이 아닌, 미술관의 큐레이터가 설명하듯 묘사하라.'''