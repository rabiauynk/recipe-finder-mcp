#!/usr/bin/env python3
"""
Recipe Finder MCP Server
Kullanıcının verdiği malzemelere göre yemek tarifi önerir (Spoonacular API)
"""

import asyncio
import os
import sys
from typing import Any, Sequence

import requests
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (EmbeddedResource, ImageContent, Resource, TextContent,
                       Tool)

# Spoonacular API base URL
SPOONACULAR_BASE_URL = "https://api.spoonacular.com/recipes"

# Initialize the MCP server
server = Server("recipe-finder-mcp")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="find_recipes_by_ingredients",
            description="Malzemelere göre yemek tarifleri bulur",
            inputSchema={
                "type": "object",
                "properties": {
                    "ingredients": {
                        "type": "string",
                        "description": "Malzemeleri virgül ile ayırarak yazın (örnek: yumurta,domates,peynir)"
                    },
                    "number": {
                        "type": "integer",
                        "description": "Kaç tane tarif istiyorsunuz (varsayılan: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["ingredients"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    if name == "find_recipes_by_ingredients":
        return await find_recipes_by_ingredients(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def find_recipes_by_ingredients(arguments: dict[str, Any]) -> list[TextContent]:
    """Find recipes based on ingredients using Spoonacular API."""
    ingredients = arguments.get("ingredients", "")
    number = arguments.get("number", 5)

    # Get API key from environment
    api_key = os.getenv("SPOONACULAR_API_KEY")
    if not api_key:
        return [TextContent(
            type="text",
            text="Hata: SPOONACULAR_API_KEY environment variable bulunamadı. Lütfen API anahtarınızı ayarlayın."
        )]

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
            return [TextContent(
                type="text",
                text=f"'{ingredients}' malzemeleri ile hiç tarif bulunamadı. Farklı malzemeler deneyin."
            )]

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

        return [TextContent(type="text", text=result_text)]

    except requests.exceptions.RequestException as e:
        return [TextContent(
            type="text",
            text=f"API isteği sırasında hata oluştu: {str(e)}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Beklenmeyen hata: {str(e)}"
        )]

async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="recipe-finder-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
