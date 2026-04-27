import base64
import json

from openai import AsyncOpenAI

from core.config import config

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


async def analyze_food_photo(image_bytes: bytes) -> dict:
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Identify the food in this image. Return ONLY a JSON object with: "
                        "'dish_name' (str), 'weight_g' (int, estimated), 'confidence' (str: high/medium/low).",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    print(f"DEBUG: GPT-4o recognized: {result}")
    return result
