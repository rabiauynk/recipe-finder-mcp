from flask import Flask, request, jsonify
from recipe import get_recipes

app = Flask(__name__)

@app.route('/recipes', methods=['GET'])
def recipes():
    ingredients = request.args.get('ingredients', '')
    if not ingredients:
        return jsonify({"error": "Malzeme girilmedi"}), 400

    try:
        result = get_recipes(ingredients)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
