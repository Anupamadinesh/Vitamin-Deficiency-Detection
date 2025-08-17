from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from app import mysql

tools_bp = Blueprint('tools', __name__)

@tools_bp.route('/diet', methods=['GET', 'POST'])
def diet_recommendation():
    food_vitamin_map = {
        "milk": ["Vitamin D", "Calcium", "Vitamin B12"],
        "spinach": ["Vitamin A", "Iron", "Vitamin K"],
        "rice": ["Carbohydrates", "Iron"],
        "egg": ["Vitamin D", "Vitamin B12", "Protein"],
        "banana": ["Vitamin B6", "Potassium", "Vitamin C"],
        "carrot": ["Vitamin A"],
        "potato": ["Vitamin C", "Vitamin B6"],
        "dal": ["Protein", "Iron", "Vitamin B1"],
        "chicken": ["Vitamin B6", "Vitamin B12", "Protein"],
        "fish": ["Vitamin D", "Omega-3", "Vitamin B12"],
        "tofu": ["Calcium", "Iron", "Vitamin B1"],
        "tomato": ["Vitamin C", "Vitamin A"],
        "paneer": ["Calcium", "Vitamin B12", "Protein"],
        "mushroom": ["Vitamin D", "Vitamin B2"],
        "almonds": ["Vitamin E", "Magnesium"],
        "sunflower seeds": ["Vitamin E", "Vitamin B1"],
        "oranges": ["Vitamin C"],
        "sweet potato": ["Vitamin A", "Vitamin C"],
        "beetroot": ["Iron", "Folate"],
        "yogurt": ["Calcium", "Probiotics", "Vitamin B12"],
        "butter": ["Vitamin A", "Fat"],
        "cheese": ["Calcium", "Protein", "Vitamin A"],
        "radish": ["Vitamin C", "Fiber"],
        "cucumber": ["Vitamin K", "Hydration"],
        "pomegranate": ["Vitamin C", "Antioxidants"],
        "walnuts": ["Omega-3", "Magnesium"],
        "cashews": ["Zinc", "Magnesium"],
        "dates": ["Iron", "Potassium"],
        "raisins": ["Iron", "Antioxidants"],
        "apple": ["Vitamin C", "Fiber"],
        "papaya": ["Vitamin A", "Vitamin C"],
        "guava": ["Vitamin C", "Fiber"],
        "avocado": ["Vitamin E", "Potassium"],
        "jackfruit": ["Vitamin C", "Vitamin B6"],
        "mango": ["Vitamin A", "Vitamin C"],
        "grapes": ["Vitamin C", "Antioxidants"],
        "watermelon": ["Hydration", "Vitamin A"],
        "millet": ["Magnesium", "Iron"],
        "oats": ["Fiber", "Magnesium"],
        "soyabean": ["Protein", "Iron"],
        "peas": ["Protein", "Vitamin C"],
        "wheat": ["Vitamin B1", "Fiber"]
    }

    vitamin_suggestions = {
        "Vitamin A": ["Carrots", "Sweet potatoes", "Spinach", "Mango"],
        "Vitamin B1": ["Dal", "Whole grains", "Sunflower seeds", "Tofu"],
        "Vitamin B6": ["Bananas", "Chicken", "Potatoes", "Jackfruit"],
        "Vitamin B12": ["Milk", "Eggs", "Fish", "Yogurt", "Paneer"],
        "Vitamin C": ["Oranges", "Tomatoes", "Potatoes", "Spinach", "Guava", "Papaya", "Pomegranate"],
        "Vitamin D": ["Sunlight", "Mushrooms", "Milk", "Eggs", "Fish"],
        "Vitamin E": ["Almonds", "Sunflower seeds", "Spinach", "Avocado"],
        "Vitamin K": ["Spinach", "Broccoli", "Cucumber"],
        "Iron": ["Spinach", "Beetroot", "Dal", "Raisins", "Soyabean"],
        "Calcium": ["Milk", "Yogurt", "Tofu", "Paneer", "Cheese"],
        "Zinc": ["Nuts", "Seeds", "Whole grains", "Cashews"],
        "Folate": ["Beetroot", "Leafy greens"],
        "Omega-3": ["Fish", "Flaxseeds", "Walnuts"],
        "Magnesium": ["Almonds", "Oats", "Walnuts", "Cashews"],
        "Protein": ["Eggs", "Dal", "Chicken", "Soyabean", "Paneer", "Tofu"],
        "Fiber": ["Apple", "Wheat", "Guava", "Radish"],
        "Potassium": ["Bananas", "Avocados", "Dates"],
        "Antioxidants": ["Pomegranate", "Raisins", "Grapes"],
        "Hydration": ["Cucumber", "Watermelon"]
    }

    all_vitamins = set(vitamin_suggestions.keys())
    selected_vitamins = set()
    result = None
    suggestions = {}

    if request.method == 'POST':
        selected_foods = request.form.getlist('foods')
        lifestyle = request.form.getlist('lifestyle')
   
        for food in selected_foods:
            selected_vitamins.update(food_vitamin_map.get(food.lower(), []))

        # Adjust recommendations based on lifestyle
        if "indoor" in lifestyle:
            all_vitamins.add("Vitamin D")
        if "vegetarian" in lifestyle:
            all_vitamins.add("Vitamin B12")
        if "vegan" in lifestyle:
            all_vitamins.update(["Vitamin B12", "Vitamin D", "Iron"])
        if "pregnant" in lifestyle:
            all_vitamins.update(["Folate", "Iron", "Calcium"])
        if "athlete" in lifestyle:
            all_vitamins.update(["Protein", "Vitamin B1", "Magnesium"])
        if "elderly" in lifestyle:
            all_vitamins.update(["Vitamin D", "Vitamin B12", "Calcium"])

        missing_vitamins = list(all_vitamins - selected_vitamins)
        result = missing_vitamins

        for vitamin in result:
            suggestions[vitamin] = vitamin_suggestions.get(vitamin, [])

    return render_template(
        'diet.html',
        food_list=food_vitamin_map.keys(),
        result=result,
        suggestions=suggestions
    )
