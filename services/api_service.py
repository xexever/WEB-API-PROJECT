import requests
import random
import json
from functools import lru_cache
from datetime import datetime, timedelta

# Кэш для API запросов
cache = {}
cache_time = {}


def cached_api_call(cache_key, ttl=3600):
    """Декоратор для кэширования API запросов"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            now = datetime.now()
            if cache_key in cache and cache_key in cache_time:
                if now - cache_time[cache_key] < timedelta(seconds=ttl):
                    return cache[cache_key]

            result = func(*args, **kwargs)
            cache[cache_key] = result
            cache_time[cache_key] = now
            return result

        return wrapper

    return decorator


class APIService:
    """Сервис для работы с внешними API"""

    @staticmethod
    def get_food_idea():
        """Получить случайный рецепт с MealDB"""
        try:
            # Уменьшаем таймаут до 3 секунд
            response = requests.get('https://www.themealdb.com/api/json/v1/1/random.php', timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get('meals') and len(data['meals']) > 0:
                    meal = data['meals'][0]
                    ingredients = []
                    for i in range(1, 6):
                        ingredient = meal.get(f'strIngredient{i}')
                        measure = meal.get(f'strMeasure{i}')
                        if ingredient and ingredient.strip():
                            ingredients.append(f"{measure} {ingredient}".strip())

                    return {
                        'title': meal.get('strMeal', 'Вкусное блюдо'),
                        'description': f"Кухня: {meal.get('strArea', 'Разная')} | Категория: {meal.get('strCategory', 'Разное')}",
                        'extra_info': f"🍽 Ингредиенты: {', '.join(ingredients[:3])}",
                        'image_url': meal.get('strMealThumb', '')
                    }
        except Exception as e:
            print(f"MealDB ошибка: {e}")

        # Быстрые локальные рецепты (без задержки)
        local_recipes = [
            {"title": "Паста Карбонара", "description": "Итальянская кухня",
             "ingredients": "Спагетти, яйца, пармезан, бекон"},
            {"title": "Цезарь с курицей", "description": "Международная кухня",
             "ingredients": "Курица, салат, пармезан, сухарики"},
            {"title": "Борщ", "description": "Русская кухня", "ingredients": "Свекла, капуста, картофель, мясо"},
        ]
        recipe = random.choice(local_recipes)
        return {
            'title': recipe['title'],
            'description': recipe['description'],
            'extra_info': f"🍽 Ингредиенты: {recipe['ingredients']}",
            'image_url': ''
        }

    @staticmethod
    def get_joke():
        """Получить случайную шутку"""
        try:
            response = requests.get('https://official-joke-api.appspot.com/random_joke', timeout=3)
            if response.status_code == 200:
                data = response.json()
                return {
                    'setup': data.get('setup', ''),
                    'punchline': data.get('punchline', '')
                }
        except Exception as e:
            print(f"Joke API ошибка: {e}")

        # Локальные шутки (быстро)
        jokes = [
            {"setup": "Почему программисты не любят природу?", "punchline": "Слишком много багов! 🐛"},
            {"setup": "Как называют программиста, который боится темноты?", "punchline": "Световой год! 💡"},
            {"setup": "Почему программисты путают Хэллоуин с Рождеством?",
             "punchline": "Потому что 31 Oct = 25 Dec! 🎃"},
            {"setup": "Что сказал один сервер другому?", "punchline": "У тебя задержки! 📡"},
            {"setup": "Сколько программистов нужно, чтобы заменить лампочку?",
             "punchline": "Ни одного, это аппаратная проблема! 🔧"},
        ]
        return random.choice(jokes)

    @staticmethod
    def generate_idea(category='random'):
        """Генерация идеи (быстрая, с локальными данными)"""

        # Если random - выбираем случайную категорию
        if category == 'random':
            categories = ['food', 'joke']
            category = random.choice(categories)

        # Еда
        if category == 'food':
            data = APIService.get_food_idea()
            return {
                'title': data.get('title', 'Приготовить что-то вкусное'),
                'description': data.get('description', 'Попробуйте новый рецепт!'),
                'category': 'food',
                'image_url': data.get('image_url', ''),
                'extra_info': data.get('extra_info', ''),
                'joke': ''
            }

        # Шутки
        elif category == 'joke':
            data = APIService.get_joke()
            return {
                'title': '😂 Шутка дня',
                'description': 'Поднимите себе настроение!',
                'category': 'joke',
                'joke_setup': data.get('setup', ''),
                'joke_punchline': data.get('punchline', ''),
                'image_url': '',
                'extra_info': ''
            }

        # Запасной вариант
        return {
            'title': 'Сделать что-то новое',
            'description': 'Попробуйте что-то необычное сегодня!',
            'category': 'random',
            'image_url': ''
        }