from dotenv import load_dotenv
import os

load_dotenv()  # загружает переменные из .env

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Настройка Bot с таймаутом (для версии 13.15)
request = Request(connect_timeout=20, read_timeout=30)
bot = Bot(token=TOKEN, request=request)

used_titles = set()
NY_TZ = pytz.timezone("America/New_York")

# --- Получение случайного рецепта с картинкой ThemealDB ---
def get_recipe():
    try:
        data = requests.get("https://www.themealdb.com/api/json/v1/1/random.php", timeout=10).json()["meals"][0]
        title = data["strMeal"]
        instructions = data["strInstructions"]
        ingredients = []
        for i in range(1, 21):
            ing = data[f"strIngredient{i}"]
            meas = data[f"strMeasure{i}"]
            if ing and ing.strip():
                ingredients.append(f"{meas.strip()} {ing.strip()}")
        image = data.get("strMealThumb", None)
        return title, instructions, ingredients, image
    except Exception as e:
        print("ERROR GET RECIPE:", e)
        return None, None, [], None

# --- Формирование текста поста ---
def generate_post(title, instructions, ingredients):
    hooks = ["🔥 Eat this to burn fat!", "💪 High protein fat-loss meal", "🥗 Clean eating recipe", "✨ Easy healthy meal"]
    tips = ["👉 Tip: Add more protein to burn fat faster", "👉 Tip: Drink water before meals", "👉 Tip: Avoid sugar for better results", "👉 Tip: Eat slowly to reduce calories"]

    text = f"""
{random.choice(hooks)}

🍽 *{title}*

🥑 *Ingredients:*
""" + "\n".join([f"• {i}" for i in ingredients[:7]]) + f"""

👨‍🍳 *Instructions:*
{instructions[:350]}...

{random.choice(tips)}

💬 Save & share!
"""
    return text

# --- Хештеги ---
def get_tags():
    tags = ["#fitness", "#weightloss", "#healthyfood", "#diet", "#fitmeals", "#fatloss"]
    return " ".join(random.sample(tags, 4))

# --- Продающий пост ---
def get_promo():
    promos = [
        "🔥 Want a full 7-day weight loss plan?\n👉 Download here: YOUR_LINK ($9)",
        "💪 Get my 1000 calorie meal plan\n👉 Link: YOUR_LINK",
        "🥗 Full fat-loss program👇\n👉 YOUR_LINK"
    ]
    return random.choice(promos)

# --- Функции отправки с повторными попытками ---
def safe_send_photo(chat_id, photo, caption):
    retries = 3
    for i in range(retries):
        try:
            bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, parse_mode="Markdown")
            return True
        except Exception as e:
            print(f"Retry {i+1}/{retries} failed:", e)
            time.sleep(5)
    print("Failed to send photo after retries")
    return False

def safe_send_message(chat_id, text):
    retries = 3
    for i in range(retries):
        try:
            bot.send_message(chat_id=chat_id, text=text)
            return True
        except Exception as e:
            print(f"Retry {i+1}/{retries} failed:", e)
            time.sleep(5)
    print("Failed to send message after retries")
    return False

# --- Постинг рецепта ---
def post_recipe():
    try:
        title, instructions, ingredients, image = get_recipe()
        if not title or title in used_titles:
            return
        used_titles.add(title)

        text = generate_post(title, instructions, ingredients)
        tags = get_tags()
        caption = text + "\n\n" + tags

        if image:
            safe_send_photo(chat_id=CHANNEL_ID, photo=image, caption=caption)
        else:
            safe_send_message(chat_id=CHANNEL_ID, text=caption)

        print(f"[{datetime.now(NY_TZ).strftime('%Y-%m-%d %H:%M:%S')}] Posted: {title}")

    except Exception as e:
        print("ERROR POST RECIPE:", e)

# --- Продающий пост ---
def post_promo():
    try:
        text = get_promo()
        safe_send_message(chat_id=CHANNEL_ID, text=text)
        print(f"[{datetime.now(NY_TZ).strftime('%Y-%m-%d %H:%M:%S')}] Promo posted")
    except Exception as e:
        print("ERROR POST PROMO:", e)

# --- Таймзона Нью-Йорк расписание ---
schedule.every().day.at("10:37").do(post_recipe)
schedule.every().day.at("13:00").do(post_recipe)
schedule.every().day.at("16:00").do(post_recipe)
schedule.every().day.at("20:00").do(post_promo)

# --- Тестовый пост сразу при старте ---
post_recipe()

print("🚀 BOT STARTED - TimeZone NY")

while True:
    schedule.run_pending()
    time.sleep(30)