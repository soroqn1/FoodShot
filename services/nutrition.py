import httpx

from core.config import config


async def get_nutrition_data(query: str, weight_g: int) -> dict:
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"api_key": config.USDA_API_KEY, "query": query, "pageSize": 1}

    async with httpx.AsyncClient() as client:
        print(f"DEBUG: Searching nutrition for: {query}")
        response = await client.get(url, params=params)
        data = response.json()

    if not data.get("foods"):
        return None

    food = data["foods"][0]
    nutrients = {n["nutrientName"]: n["value"] for n in food.get("foodNutrients", [])}

    ratio = weight_g / 100

    return {
        "carbs": nutrients.get("Carbohydrate, by difference", 0) * ratio,
        "protein": nutrients.get("Protein", 0) * ratio,
        "fat": nutrients.get("Total lipid (fat)", 0) * ratio,
        "kcal": nutrients.get("Energy", 0) * ratio,
    }
