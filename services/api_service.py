import requests
import random
import json
from datetime import datetime, timedelta

# Кэш для API запросов
cache = {}
cache_time = {}


class APIService:
    """Сервис для работы с внешними API"""

    @staticmethod
    def get_food_idea():
        """Получить случайный рецепт с MealDB"""
        try:
            response = requests.get('https://www.themealdb.com/api/json/v1/1/random.php', timeout=8)
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
                        'title': meal.get('strMeal', 'Delicious Dish'),
                        'description': f"Cuisine: {meal.get('strArea', 'Various')} | Category: {meal.get('strCategory', 'Various')}",
                        'extra_info': f"Ingredients: {', '.join(ingredients[:3])}",
                        'image_url': meal.get('strMealThumb', '')
                    }
        except Exception as e:
            print(f"MealDB error: {e}")

        local_recipes = [
            {"title": "Pasta Carbonara", "description": "Italian cuisine",
             "ingredients": "Spaghetti, eggs, parmesan, bacon"},
            {"title": "Chicken Caesar", "description": "International cuisine",
             "ingredients": "Chicken, lettuce, parmesan, croutons"},
            {"title": "Borscht", "description": "Russian cuisine", "ingredients": "Beets, cabbage, potatoes, meat"},
        ]
        recipe = random.choice(local_recipes)
        return {
            'title': recipe['title'],
            'description': recipe['description'],
            'extra_info': f"Ingredients: {recipe['ingredients']}",
            'image_url': ''
        }

    @staticmethod
    def get_joke():
        """Получить случайную шутку"""
        try:
            response = requests.get('https://official-joke-api.appspot.com/random_joke', timeout=8)
            if response.status_code == 200:
                data = response.json()
                return {
                    'setup': data.get('setup', ''),
                    'punchline': data.get('punchline', '')
                }
        except Exception as e:
            print(f"Joke API error: {e}")

        jokes = [
            {"setup": "Why do programmers prefer dark mode?", "punchline": "Because light attracts bugs"},
            {"setup": "What do you call a programmer who is afraid of the dark?", "punchline": "A light-year"},
            {"setup": "Why did the developer go broke?", "punchline": "Because he used up all his cache"},
            {"setup": "What's a programmer's favorite hangout place?", "punchline": "The Foo Bar"},
            {"setup": "Why do programmers always mix up Halloween and Christmas?",
             "punchline": "Because Oct 31 = Dec 25"},
        ]
        return random.choice(jokes)

    @staticmethod
    def get_advice():
        """Получить случайный совет"""
        try:
            response = requests.get('https://api.adviceslip.com/advice', timeout=8)
            if response.status_code == 200:
                data = response.json()
                advice = data.get('slip', {}).get('advice', '')
                return {
                    'title': 'Wise Advice',
                    'description': f'"{advice}"',
                    'extra_info': 'Advice for all occasions',
                    'image_url': ''
                }
        except Exception as e:
            print(f"Advice API error: {e}")

        local_advice = [
            "Don't put off until tomorrow what you can do today",
            "Smile - it's free but priceless",
            "Drink more water - it's good for you",
            "Take a break when you need it",
            "Believe in yourself",
        ]
        return {
            'title': 'Simple Advice',
            'description': f'"{random.choice(local_advice)}"',
            'extra_info': 'Advice of the day',
            'image_url': ''
        }

    @staticmethod
    def get_trivia_question():
        """Получить случайный вопрос для викторины"""
        try:
            response = requests.get('https://opentdb.com/api.php?amount=1', timeout=8)
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    q = data['results'][0]
                    import html
                    return {
                        'title': f"Trivia: {q.get('category', 'General')}",
                        'description': html.unescape(q.get('question', '')),
                        'correct_answer': html.unescape(q.get('correct_answer', '')),
                        'difficulty': q.get('difficulty', 'medium'),
                        'image_url': ''
                    }
        except Exception as e:
            print(f"Trivia API error: {e}")

        local_questions = [
            {"question": "How many colors are in a rainbow?", "answer": "7", "category": "Science"},
            {"question": "Who wrote 'War and Peace'?", "answer": "Leo Tolstoy", "category": "Literature"},
            {"question": "What is the capital of France?", "answer": "Paris", "category": "Geography"},
        ]
        q = random.choice(local_questions)
        return {
            'title': f"Trivia: {q['category']}",
            'description': q['question'],
            'correct_answer': q['answer'],
            'difficulty': 'medium',
            'image_url': ''
        }

    @staticmethod
    def get_name_info():
        """Анализ имени: возраст, пол, национальность"""
        popular_names = ['alexander', 'anna', 'maxim', 'elena', 'dmitry', 'olga', 'ivan', 'maria']
        name = random.choice(popular_names)

        result = {
            'name': name.capitalize(),
            'age': 'Unknown',
            'gender': 'Unknown',
            'country': 'Unknown',
        }

        description_lines = [f"Analyzing name: {result['name']}"]

        # 1. Определяем возраст
        try:
            resp = requests.get(f'https://api.agify.io?name={name}', timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                age = data.get('age')
                if age:
                    result['age'] = f"~{age} years"
                    description_lines.append(f"Estimated age: ~{age} years")
        except Exception as e:
            print(f"Agify error: {e}")
            description_lines.append(f"Estimated age: Data unavailable")

        # 2. Определяем пол
        try:
            resp = requests.get(f'https://api.genderize.io?name={name}', timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                gender = data.get('gender')
                prob = data.get('probability', 0)
                if gender:
                    gender_text = 'Male' if gender == 'male' else 'Female'
                    prob_percent = int(prob * 100) if prob else 0
                    result['gender'] = f"{gender_text} ({prob_percent}%)"
                    description_lines.append(f"Gender: {gender_text} (confidence: {prob_percent}%)")
        except Exception as e:
            print(f"Genderize error: {e}")
            description_lines.append(f"Gender: Data unavailable")

        # 3. Определяем национальность
        try:
            resp = requests.get(f'https://api.nationalize.io?name={name}', timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('country') and len(data['country']) > 0:
                    country_codes = {
                        'RU': 'Russia', 'US': 'USA', 'GB': 'United Kingdom',
                        'DE': 'Germany', 'FR': 'France', 'IT': 'Italy',
                        'UA': 'Ukraine', 'BY': 'Belarus', 'KZ': 'Kazakhstan'
                    }
                    country_data = data['country'][0]
                    country_id = country_data.get('country_id', '')
                    country_name = country_codes.get(country_id, country_id)
                    prob = round(country_data.get('probability', 0) * 100, 1)
                    result['country'] = f"{country_name} ({prob}%)"
                    description_lines.append(f"Most likely country: {country_name} (probability: {prob}%)")
        except Exception as e:
            print(f"Nationalize error: {e}")
            description_lines.append(f"Country: Data unavailable")

        return {
            'title': f"Name Analysis: {result['name']}",
            'description': '\n'.join(description_lines),
            'extra_info': 'Based on statistical data from social networks',
            'image_url': '',
            'name_data': result
        }

    @staticmethod
    def generate_idea(category='random'):
        """Генерация идеи"""

        all_categories = ['food', 'joke', 'advice', 'trivia', 'name_info']

        if category == 'random':
            category = random.choice(all_categories)

        print(f"Generating idea for category: {category}")

        # Еда
        if category == 'food':
            data = APIService.get_food_idea()
            return {
                'title': data.get('title', 'Cook Something Delicious'),
                'description': data.get('description', 'Try a new recipe'),
                'category': 'food',
                'image_url': data.get('image_url', ''),
                'extra_info': data.get('extra_info', ''),
            }

        # Шутки
        if category == 'joke':
            data = APIService.get_joke()
            return {
                'title': 'Joke of the Day',
                'description': 'Have a laugh',
                'category': 'joke',
                'joke_setup': data.get('setup', ''),
                'joke_punchline': data.get('punchline', ''),
                'image_url': '',
            }

        # Совет
        if category == 'advice':
            data = APIService.get_advice()
            return {
                'title': data.get('title', 'Daily Advice'),
                'description': data.get('description', ''),
                'category': 'advice',
                'extra_info': data.get('extra_info', ''),
                'image_url': '',
            }

        # Викторина
        if category == 'trivia':
            data = APIService.get_trivia_question()
            return {
                'title': data.get('title', 'Trivia Question'),
                'description': data.get('description', ''),
                'category': 'trivia',
                'correct_answer': data.get('correct_answer', ''),
                'difficulty': data.get('difficulty', ''),
                'extra_info': f"Difficulty: {data.get('difficulty', 'medium')}",
                'image_url': '',
            }

        # Анализ имени
        if category == 'name_info':
            data = APIService.get_name_info()
            return {
                'title': data.get('title', 'Name Analysis'),
                'description': data.get('description', ''),
                'category': 'name_info',
                'extra_info': data.get('extra_info', ''),
                'image_url': '',
                'name_data': data.get('name_data', {})
            }

        # Запасной вариант
        return {
            'title': 'Try Something New',
            'description': 'Do something unusual today',
            'category': 'random',
            'image_url': ''
        }