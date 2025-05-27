import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SPOONACULAR_API_KEY")

def get_recipes(ingredients):
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ingredients,
        "number": 3,
        "ranking": 1,
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for recipe in data:
        results.append({
            "title": recipe.get("title"),
            "image": recipe.get("image"),
            "id": recipe.get("id")
        })
    return results
