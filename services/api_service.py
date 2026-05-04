import requests
import random
import json


class APIService:
    """Сервис для работы с внешними API - рабочие аналоги"""

    @staticmethod
    def get_bored_activity():
        """Получить случайную активность - альтернативный API"""
        # Встроенные идеи на случай недоступности API
        local_activities = [
            {"activity": "Научиться играть на гитаре", "type": "music", "participants": 1},
            {"activity": "Сходить на прогулку в парк", "type": "outdoor", "participants": 1},
            {"activity": "Приготовить ужин для друзей", "type": "cooking", "participants": 3},
            {"activity": "Посмотреть документальный фильм", "type": "education", "participants": 1},
            {"activity": "Написать рассказ", "type": "creative", "participants": 1},
            {"activity": "Позвонить старым друзьям", "type": "social", "participants": 2},
            {"activity": "Сделать уборку в комнате", "type": "housework", "participants": 1},
            {"activity": "Начать учить новый язык", "type": "education", "participants": 1},
            {"activity": "Сходить в спортзал", "type": "sports", "participants": 1},
            {"activity": "Почитать книгу", "type": "relaxation", "participants": 1},
        ]

        # Пробуем API
        try:
            # Используем альтернативный API (работает в России)
            response = requests.get('https://www.boredapi.com/api/activity/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('activity', ''),
                    'description': data.get('type', 'general'),
                    'participants': data.get('participants', 1)
                }
        except Exception as e:
            print(f"Bored API недоступен, используем локальные данные: {e}")

        # Возвращаем случайную локальную активность
        activity = random.choice(local_activities)
        return {
            'title': activity['activity'],
            'description': activity['type'],
            'participants': activity['participants']
        }

    @staticmethod
    def get_joke_by_category(category='activity'):
        """Получить шутку - альтернативные источники"""

        # База шуток на все случаи
        jokes_db = {
            'activity': [
                "Почему программисты не любят природу? Слишком много багов! 🐛",
                "Как назвать программиста, который боится темноты? Световой год! 💡",
                "Сколько программистов нужно, чтобы заменить лампочку? Ни одного, это аппаратная проблема! 🔧",
                "Почему программисты путают Хэллоуин с Рождеством? Потому что 31 Oct = 25 Dec! 🎃"
            ],
            'food': [
                "Почему повара любят готовить пасту? Потому что это всегда 'аль денте'! 🍝",
                "Какой любимый день у пиццы? Не 'понедельник', а 'пицца-дельник'! 🍕",
                "Почему суши всегда спокойны? Потому что они в соевом равновесии! 🍣",
                "Что сказал один пельмень другому? 'Ты просто замороженный, а я горячий!' 🥟"
            ],
            'movie': [
                "Почему фильмы ужасов снимают быстро? Потому что время — это самый страшный ужас! 🎬",
                "Какой любимый фильм у математиков? 'Геометрическая свадьба'! 📐",
                "Почему актёры всегда злые? Потому что у них плохие роли! 🎭"
            ],
            'place': [
                "Почему путешественники никогда не теряются? Потому что они всегда находят приключения! 🧭",
                "Как называется любимое место программиста? Ctrl + Alt + Delete! 💻",
                "Почему в горах всегда холодно? Потому что там высокие требования! 🏔️"
            ],
            'joke': [
                "Почему смех — это лучшее лекарство? Потому что он не имеет побочных эффектов! 😂",
                "Что говорит один анекдот другому? 'Ты меня убиваешь!' 💀",
                "Почему клоуны всегда грустные? Потому что их работа — это цирк! 🎪"
            ]
        }

        # Пробуем JokeAPI
        try:
            joke_categories = {'activity': 'Programming', 'food': 'Food', 'movie': 'Movie', 'place': 'Travel',
                               'joke': 'Misc'}
            api_category = joke_categories.get(category, 'Any')

            response = requests.get(f'https://v2.jokeapi.dev/joke/{api_category}?safe-mode', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('type') == 'twopart':
                    return f"{data.get('setup', '')} — {data.get('delivery', '')}"
                elif data.get('joke'):
                    return data.get('joke')
        except Exception as e:
            print(f"JokeAPI недоступен, используем локальные шутки: {e}")

        # Возвращаем случайную шутку из базы
        category_jokes = jokes_db.get(category, jokes_db['activity'])
        return random.choice(category_jokes)

    @staticmethod
    def get_image_by_category(category):
        """Получить изображение по категории - используем прямые ссылки на изображения"""

        # Прямые ссылки на изображения с Pexels (CDN)
        images_db = {
            'activity': [
                'https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg?auto=compress&cs=tinysrgb&w=800',
                'https://images.pexels.com/photos/1181467/pexels-photo-1181467.jpeg?auto=compress&cs=tinysrgb&w=800',
                'https://images.pexels.com/photos/1151418/pexels-photo-1151418.jpeg?auto=compress&cs=tinysrgb&w=800',
            ],
            'food': [
                'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=800',
                'https://images.pexels.com/photos/1279330/pexels-photo-1279330.jpeg?auto=compress&cs=tinysrgb&w=800',
                'https://images.pexels.com/photos/958545/pexels-photo-958545.jpeg?auto=compress&cs=tinysrgb&w=800',
            ],
            'movie': [
                'https://images.pexels.com/photos/7991248/pexels-photo-7991248.jpeg?auto=compress&cs=tinysrgb&w=800',
                'https://images.pexels.com/photos/3062545/pexels-photo-3062545.jpeg?auto=compress&cs=tinysrgb&w=800',
                'https://images.pexels.com/photos/7991246/pexels-photo-7991246.jpeg?auto=compress&cs=tinysrgb&w=800',
            ],
            'place': [
                'https://images.pexels.com/photos/258117/pexels-photo-258117.jpeg?auto=compress&cs=tinysrgb&w=800',
                'https://images.pexels.com/photos/532826/pexels-photo-532826.jpeg?auto=compress&cs=tinysrgb&w=800',
                'https://images.pexels.com/photos/2082103/pexels-photo-2082103.jpeg?auto=compress&cs=tinysrgb&w=800',
            ],
            'joke': [
                'https://images.pexels.com/photos/5428844/pexels-photo-5428844.jpeg?auto=compress&cs=tinysrgb&w=800',
                'https://images.pexels.com/photos/5182446/pexels-photo-5182446.jpeg?auto=compress&cs=tinysrgb&w=800',
                'https://images.pexels.com/photos/5198230/pexels-photo-5198230.jpeg?auto=compress&cs=tinysrgb&w=800',
            ]
        }

        images = images_db.get(category, images_db['activity'])
        return random.choice(images)

    @staticmethod
    def generate_idea(category='random'):
        """Генерация полной идеи с использованием API"""

        # Если random - выбираем случайную категорию
        if category == 'random':
            categories = ['activity', 'food', 'movie', 'place', 'joke']
            category = random.choice(categories)

        # Получаем активность
        bored_data = APIService.get_bored_activity()

        if category == 'activity' and bored_data:
            title = bored_data['title']
            description = f"Тип: {bored_data['description']} | Для {bored_data['participants']} {'человека' if bored_data['participants'] > 1 else 'человека'}"
        else:
            # Идеи по категориям
            ideas = {
                'food': ("Приготовить новое блюдо", "Попробуйте новый рецепт сегодня!"),
                'movie': ("Посмотреть фильм", "Устройте кинопросмотр с попкорном!"),
                'place': ("Посетить новое место", "Откройте для себя что-то новое в городе!"),
                'joke': ("Посмотреть комедию", "Хороший смех продлевает жизнь!")
            }
            title, description = ideas.get(category, ("Сделать что-то новое", "Попробуйте что-то необычное!"))

        # Получаем шутку
        joke = APIService.get_joke_by_category(category)

        # Получаем изображение
        image_url = APIService.get_image_by_category(category)

        return {
            'title': title,
            'description': description,
            'category': category,
            'joke': joke,
            'image_url': image_url
        }