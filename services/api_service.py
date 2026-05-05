import requests
import random
import json
from datetime import datetime, timedelta
from collections import deque

# Кэш для API запросов
cache = {}
cache_time = {}

# Хранилище для сгенерированных имен (чтобы избежать повторов)
used_names_history = deque(maxlen=100)  # Помним последние 100 имен


class APIService:
    """Сервис для работы с внешними API"""

    # База имен для генерации (аналог full-name-generator)
    FIRST_NAMES = [
        'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
        'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
        'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
        'Matthew', 'Betty', 'Anthony', 'Margaret', 'Donald', 'Sandra', 'Mark', 'Ashley',
        'Paul', 'Dorothy', 'Steven', 'Kimberly', 'Andrew', 'Emily', 'Kenneth', 'Donna',
        'Alexander', 'Anna', 'Dmitry', 'Olga', 'Maxim', 'Elena', 'Ivan', 'Maria',
        'Alexey', 'Tatiana', 'Vladimir', 'Natalia', 'Sergey', 'Irina', 'Andrey', 'Svetlana',
        'Nikolai', 'Victoria', 'Mikhail', 'Anastasia', 'Pavel', 'Julia', 'Oleg', 'Ekaterina'
    ]

    LAST_NAMES = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
        'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
        'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
        'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
        'Ivanov', 'Petrov', 'Sidorov', 'Smirnov', 'Volkov', 'Kuznetsov', 'Popov', 'Sokolov',
        'Lebedev', 'Kozlov', 'Novikov', 'Morozov', 'Petrova', 'Ivanova', 'Sidorova'
    ]

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
                        'extra_info': f"🍽 Ingredients: {', '.join(ingredients[:3])}",
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
            'extra_info': f"🍽 Ingredients: {recipe['ingredients']}",
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
            {"setup": "Why do programmers prefer dark mode?", "punchline": "Because light attracts bugs! 🐛"},
            {"setup": "What do you call a programmer who is afraid of the dark?", "punchline": "A light-year! 💡"},
            {"setup": "Why did the developer go broke?", "punchline": "Because he used up all his cache! 💰"},
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
                    'title': '💡 Wise Advice',
                    'description': f'"{advice}"',
                    'extra_info': 'Advice for all occasions ✨',
                    'image_url': ''
                }
        except Exception as e:
            print(f"Advice API error: {e}")

        local_advice = [
            "Don't put off until tomorrow what you can do today",
            "Smile - it's free but priceless",
            "Drink more water - it's good for you",
        ]
        return {
            'title': '💡 Simple Advice',
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
                        'title': f"❓ Trivia: {q.get('category', 'General')}",
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
        ]
        q = random.choice(local_questions)
        return {
            'title': f"❓ Trivia: {q['category']}",
            'description': q['question'],
            'correct_answer': q['answer'],
            'difficulty': 'medium',
            'image_url': ''
        }

    @staticmethod
    def get_unique_name():
        """Сгенерировать уникальное полное имя (без повторов)"""
        import random as rnd

        # Генерируем новое имя, проверяя на уникальность
        for attempt in range(50):  # Максимум 50 попыток
            first = rnd.choice(APIService.FIRST_NAMES)
            last = rnd.choice(APIService.LAST_NAMES)
            full_name = f"{first} {last}"

            if full_name not in used_names_history:
                used_names_history.append(full_name)
                return {
                    'first_name': first,
                    'last_name': last,
                    'full_name': full_name
                }

        # Если не удалось найти уникальное имя (почти невозможно)
        # Просто возвращаем случайное имя из базы
        first = random.choice(APIService.FIRST_NAMES)
        last = random.choice(APIService.LAST_NAMES)
        full_name = f"{first} {last}"
        return {
            'first_name': first,
            'last_name': last,
            'full_name': full_name
        }

    @staticmethod
    def get_name_info():
        """Анализ имени: возраст, пол, национальность (с генерацией уникальных имен)"""

        # Получаем уникальное имя из нашей базы
        name_data = APIService.get_unique_name()
        name = name_data['first_name'].lower()

        result = {
            'name': name_data['full_name'],
            'first_name': name_data['first_name'],
            'last_name': name_data['last_name'],
            'age': 'Unknown',
            'gender': 'Unknown',
            'country': 'Unknown',
        }

        # Описания для отображения
        description_lines = [f"📊 Generated unique name: {result['name']}"]

        # 1. Определяем возраст (через API)
        try:
            resp = requests.get(f'https://api.agify.io?name={name}', timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                age = data.get('age')
                if age:
                    result['age'] = f"~{age} years"
                    description_lines.append(f"📈 Estimated age: ~{age} years")
        except Exception as e:
            print(f"Agify error: {e}")
            description_lines.append(f"📈 Estimated age: Data unavailable")

        # 2. Определяем пол
        try:
            resp = requests.get(f'https://api.genderize.io?name={name}', timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                gender = data.get('gender')
                prob = data.get('probability', 0)
                if gender:
                    gender_text = '👨 Male' if gender == 'male' else '👩 Female'
                    prob_percent = int(prob * 100) if prob else 0
                    result['gender'] = f"{gender_text} ({prob_percent}%)"
                    description_lines.append(f"🚻 Gender: {gender_text} (confidence: {prob_percent}%)")
        except Exception as e:
            print(f"Genderize error: {e}")
            description_lines.append(f"🚻 Gender: Data unavailable")

        # 3. Определяем национальность
        try:
            resp = requests.get(f'https://api.nationalize.io?name={name}', timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('country') and len(data['country']) > 0:
                    country_codes = {
                        'RU': '🇷🇺 Russia', 'US': '🇺🇸 USA', 'GB': '🇬🇧 UK',
                        'DE': '🇩🇪 Germany', 'FR': '🇫🇷 France', 'IT': '🇮🇹 Italy',
                        'UA': '🇺🇦 Ukraine', 'BY': '🇧🇾 Belarus', 'KZ': '🇰🇿 Kazakhstan'
                    }
                    country_data = data['country'][0]
                    country_id = country_data.get('country_id', '')
                    country_name = country_codes.get(country_id, country_id)
                    prob = round(country_data.get('probability', 0) * 100, 1)
                    result['country'] = f"{country_name} ({prob}%)"
                    description_lines.append(f"🌍 Most likely country: {country_name} (probability: {prob}%)")
        except Exception as e:
            print(f"Nationalize error: {e}")
            description_lines.append(f"🌍 Country: Data unavailable")

        return {
            'title': f"📊 Name Analysis: {result['first_name']}",
            'description': '\n'.join(description_lines),
            'extra_info': 'ℹ️ Based on statistical data from social networks | Names are generated without repetition',
            'image_url': '',
            'name_data': result
        }

    @staticmethod
    def generate_idea(category='random'):
        """Генерация идеи"""

        # Все категории (убрали random_data)
        all_categories = ['food', 'joke', 'advice', 'trivia', 'name_info']

        if category == 'random':
            category = random.choice(all_categories)

        print(f"Generating idea for category: {category}")

        # Еда
        if category == 'food':
            data = APIService.get_food_idea()
            return {
                'title': data.get('title', '🍕 Cook Something Delicious'),
                'description': data.get('description', 'Try a new recipe!'),
                'category': 'food',
                'image_url': data.get('image_url', ''),
                'extra_info': data.get('extra_info', ''),
            }

        # Шутки
        if category == 'joke':
            data = APIService.get_joke()
            return {
                'title': '😂 Joke of the Day',
                'description': 'Have a laugh!',
                'category': 'joke',
                'joke_setup': data.get('setup', ''),
                'joke_punchline': data.get('punchline', ''),
                'image_url': '',
            }

        # Совет
        if category == 'advice':
            data = APIService.get_advice()
            return {
                'title': data.get('title', '💡 Daily Advice'),
                'description': data.get('description', ''),
                'category': 'advice',
                'extra_info': data.get('extra_info', ''),
                'image_url': '',
            }

        # Викторина
        if category == 'trivia':
            data = APIService.get_trivia_question()
            return {
                'title': data.get('title', '❓ Trivia Question'),
                'description': data.get('description', ''),
                'category': 'trivia',
                'correct_answer': data.get('correct_answer', ''),
                'difficulty': data.get('difficulty', ''),
                'extra_info': f"⭐ Difficulty: {data.get('difficulty', 'medium')}",
                'image_url': '',
            }

        # Анализ имени
        if category == 'name_info':
            data = APIService.get_name_info()
            return {
                'title': data.get('title', '📊 Name Analysis'),
                'description': data.get('description', ''),
                'category': 'name_info',
                'extra_info': data.get('extra_info', ''),
                'image_url': '',
                'name_data': data.get('name_data', {})
            }

        # Запасной вариант
        return {
            'title': '✨ Try Something New',
            'description': 'Do something unusual today!',
            'category': 'random',
            'image_url': ''
        }