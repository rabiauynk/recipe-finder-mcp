#!/usr/bin/env python3
"""
Recipe Finder MCP Server
Kullanıcının verdiği malzemelere göre yemek tarifi önerir (Spoonacular API)
"""

import os

import requests
from mcp.server.fastmcp import FastMCP

# Spoonacular API base URL
SPOONACULAR_BASE_URL = "https://api.spoonacular.com/recipes"

# Initialize the FastMCP server
mcp = FastMCP("recipe-finder-mcp")

@mcp.resource("status://server")
def get_server_status() -> str:
    """Server durumu ve API anahtarı kontrolü"""
    api_key = os.getenv("SPOONACULAR_API_KEY")
    if api_key:
        # Mask the API key for security
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        return f"✅ Server aktif\n🔑 API Key: {masked_key}\n🍳 Tarif arama servisi hazır!"
    else:
        return "❌ API anahtarı bulunamadı\n🔧 SPOONACULAR_API_KEY environment variable ayarlanmalı"

@mcp.tool()
def find_recipes_by_ingredients(ingredients: str, number: int = 5) -> str:
    """
    Malzemelere göre yemek tarifleri bulur

    Args:
        ingredients: Malzemeleri virgül ile ayırarak yazın (örnek: yumurta,domates,peynir)
        number: Kaç tane tarif istiyorsunuz (varsayılan: 5, maksimum: 20)

    Returns:
        Bulunan tariflerin listesi
    """
    # Validate number parameter
    if number < 1:
        number = 1
    elif number > 20:
        number = 20

    # Get API key from environment
    api_key = os.getenv("SPOONACULAR_API_KEY")
    if not api_key:
        return "❌ Hata: SPOONACULAR_API_KEY environment variable bulunamadı. Lütfen API anahtarınızı ayarlayın."

    try:
        # Make request to Spoonacular API
        url = f"{SPOONACULAR_BASE_URL}/findByIngredients"
        params = {
            "ingredients": ingredients,
            "number": number,
            "apiKey": api_key,
            "ranking": 1,  # Maximize used ingredients
            "ignorePantry": True
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        recipes = response.json()

        if not recipes:
            return f"🔍 '{ingredients}' malzemeleri ile hiç tarif bulunamadı. Farklı malzemeler deneyin."

        # Format the response
        result_text = f"🍳 **{ingredients}** malzemeleri ile bulduğum tarifler:\n\n"

        for i, recipe in enumerate(recipes, 1):
            title = recipe.get("title", "Bilinmeyen Tarif")
            used_ingredients = recipe.get("usedIngredientCount", 0)
            missed_ingredients = recipe.get("missedIngredientCount", 0)
            recipe_id = recipe.get("id", "")

            result_text += f"**{i}. {title}**\n"
            result_text += f"   • Kullanılan malzemeler: {used_ingredients}\n"
            result_text += f"   • Eksik malzemeler: {missed_ingredients}\n"

            if recipe_id:
                result_text += f"   • Detaylı tarif için ID: {recipe_id}\n"

            result_text += "\n"

        result_text += "\n💡 **İpucu:** Daha iyi sonuçlar için daha fazla malzeme ekleyin!"

        return result_text

    except requests.exceptions.RequestException as e:
        return f"🚫 API isteği sırasında hata oluştu: {str(e)}"
    except Exception as e:
        return f"⚠️ Beklenmeyen hata: {str(e)}"

if __name__ == "__main__":
    mcp.run()
