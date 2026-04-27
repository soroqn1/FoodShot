import base64
import json
import re

from openai import AsyncOpenAI

from core.config import config

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


async def analyze_food_photo(image_bytes: bytes, language: str = "en") -> dict | None:
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Identify the food in this image. "
                            f"Reply with ONLY a raw JSON object (no markdown, no code block) with these fields: "
                            f"dish_name (string, in {language} language), "
                            f"dish_name_en (string, always in English), "
                            f"weight_g (integer, estimated grams), "
                            f"confidence (string: high, medium, or low)."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )

    content = response.choices[0].message.content
    if not content:
        return None

    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        return None

    return json.loads(match.group())
