import requests

def get_location_from_caption(caption):
    mapping = {
        "large white building": "Taj Mahal, Agra, India",
        "the statue of liberty": "Statue of Liberty, New York, USA",
        "eiffel tower": "Eiffel Tower, Paris, France",
        "big ben": "Big Ben, London, UK",
        "golden gate bridge": "Golden Gate Bridge, San Francisco, USA",
        "india gate": "India Gate, New Delhi, India",
        "gateway of india": "Gateway of India, Mumbai, India",
        "charminar": "Charminar, Hyderabad, India",
        "lotus temple": "Lotus Temple, Delhi, India",
        "white house": "White House, Washington DC, USA"
    }

    caption_clean = caption.lower().strip()
    for k, v in mapping.items():
        if k in caption_clean:
            caption = v
            break

    url = f"https://nominatim.openstreetmap.org/search?q={caption}&format=json&limit=1"
    headers = {"User-Agent": "TravelFoodApp/1.0"}  # Nominatim requires a custom User-Agent

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                return {
                    "name": caption.title(),
                    "lat": data[0]['lat'],
                    "lon": data[0]['lon'],
                    "address": data[0].get('display_name', 'Unknown location')
                }
        return None
    except Exception as e:
        print("Location API error:", e)
        return None

def get_activities(lat, lon):
    query = f"""
    [out:json];
    node(around:1000,{lat},{lon})["tourism"];
    out;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.post(url, data={"data": query})
        return [
            act.get("tags", {}).get("name", "Unknown Activity")
            for act in response.json().get("elements", [])[:10]
        ]
    except Exception as e:
        print("Activities API error:", e)
        return []

def get_food_nutrition(food_name, api_key):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if 'foods' in data and data['foods']:
            food = data['foods'][0]
            nutrients = {
                nutrient["nutrientName"]: nutrient["value"]
                for nutrient in food.get("foodNutrients", [])
            }
            return {
                "description": food.get('description'),
                "category": food.get('foodCategory'),
                "nutrients": nutrients
            }
    except Exception as e:
        print("Food API error:", e)
    return None
