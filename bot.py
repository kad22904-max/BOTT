import telebot
import time
import random
import json
import os
from datetime import datetime

TOKEN = "8505372036:AAEf3B8QrqRKKJxo8B7OkrGNX41s2MCMx3Y"

bot = telebot.TeleBot(TOKEN)

USER_FILE = "users.json"

# ===== ЗАГРУЗКА/СОХРАНЕНИЕ ДАННЫХ =====
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

user_data = load_users()
captcha_data = {}

# ===== ГЕНЕРАЦИЯ KPI ДАННЫХ =====
def get_kpi_data():
    return {
        "sales": {
            "new_clients": random.randint(5, 50),
            "revenue": random.randint(100000, 5000000),
            "average_check": random.randint(500, 5000),
            "deals": random.randint(10, 100),
            "conversion": round(random.uniform(5, 30), 1)
        },
        "marketing": {
            "cpl": random.randint(50, 500),
            "leads": random.randint(50, 500),
            "roi": round(random.uniform(50, 300), 1),
            "ad_spend": random.randint(10000, 200000),
            "ctr": round(random.uniform(0.5, 5), 2)
        },
        "scam": {
            "total_scammed": random.randint(1, 50),
            "total_earned": round(random.uniform(10, 5000), 2),
            "avg_per_scam": round(random.uniform(5, 200), 2),
            "success_rate": round(random.uniform(60, 95), 1)
        }
    }

# ===== ГЕНЕРАЦИЯ КАПТЧИ =====
def generate_captcha():
    emojis = ["🍎", "🍌", "🍇", "🍉", "🍓", "🍒", "🍑", "🍊", "🍋", "🍍", "🥝", "🥑", "🍆", "🥕", "🌽", "🍩", "🍪", "🎂", "🧁", "🍫", "🍬", "🍭", "🍮"]
    chosen = random.sample(emojis, 6)
    target = random.choice(chosen)
    return chosen, target

def captcha_markup(correct, target):
    random.shuffle(correct)
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    for emoji in correct:
        markup.add(telebot.types.InlineKeyboardButton(emoji, callback_data=f"captcha_{emoji}_{target}"))
    return markup

# ===== ГЛАВНОЕ МЕНЮ =====
def main_menu():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("📊 KPI", callback_data="kpi_main"),
        telebot.types.InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        telebot.types.InlineKeyboardButton("💰 Баланс", callback_data="balance"),
        telebot.types.InlineKeyboardButton("💸 Выплаты", callback_data="withdraw_menu"),
        telebot.types.InlineKeyboardButton("📄 Шаблоны", callback_data="shablon"),
        telebot.types.InlineKeyboardButton("🍾 Буты", callback_data="buty"),
        telebot.types.InlineKeyboardButton("⚙️ Управление", callback_data="manage"),
        telebot.types.InlineKeyboardButton("🛠 Настройки", callback_data="settings"),
        telebot.types.InlineKeyboardButton("ℹ️ О проекте", callback_data="projects"),
        telebot.types.InlineKeyboardButton("🛒 Маркет", callback_data="market"),
        telebot.types.InlineKeyboardButton("💸 ОТС - выплаты", callback_data="outcome"),
        telebot.types.InlineKeyboardButton("📊 Трафик", callback_data="traffic"),
        telebot.types.InlineKeyboardButton("🎁 Подарок", callback_data="gift")
    )
    return markup

# ===== МЕНЮ ВЫПЛАТ =====
def withdraw_menu_markup():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("💸 Создать выплату", callback_data="withdraw_create"),
        telebot.types.InlineKeyboardButton("📋 История выплат", callback_data="withdraw_history"),
        telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back")
    )
    return markup

# ===== МЕНЮ KPI =====
def kpi_menu():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("💼 Продажи", callback_data="kpi_sales"),
        telebot.types.InlineKeyboardButton("📢 Маркетинг", callback_data="kpi_marketing"),
        telebot.types.InlineKeyboardButton("🎯 Скам KPI", callback_data="kpi_scam"),
        telebot.types.InlineKeyboardButton("🔄 Обновить", callback_data="kpi_refresh"),
        telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back")
    )
    return markup

# ===== КНОПКА НАЗАД =====
def back_button():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back"))
    return markup

# ===== КОМАНДА /start =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.chat.id)

    if user_id not in user_data:
        user_data[user_id] = {
            "captcha_passed": False,
            "mentor": None,
            "captcha_attempts": 0,
            "balance": 0.0,
            "total_earned": 0.0,
            "total_scammed": 0,
            "kpi_data": get_kpi_data(),
            "withdraws": []
        }
        save_users(user_data)

    if not user_data[user_id]["captcha_passed"]:
        emojis, target = generate_captcha()
        captcha_data[user_id] = (emojis, target)
        bot.send_message(
            user_id,
            f"🔐 Пройди каптчу для входа\n\n"
            f"Нажми на эмодзи: {target}\n\n" + " ".join(emojis),
            reply_markup=captcha_markup(emojis, target),
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            user_id,
            "🌟 ГЛАВНОЕ МЕНЮ\n\n"
            "👋 Добро пожаловать в панель управления!\n"
            "Выберите нужный раздел ниже:",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

# ===== ОБРАБОТЧИК КАПТЧИ =====
@bot.callback_query_handler(func=lambda call: call.data.startswith("captcha_"))
def handle_captcha(call):
    user_id = str(call.message.chat.id)
    parts = call.data.split("_")
    selected = parts[1]
    target = parts[2]
    data = captcha_data.get(user_id, (None, None))

    if data == (None, None):
        bot.answer_callback_query(call.id, "❌ Каптча устарела. Напиши /start заново.")
        return

    if user_data[user_id]["captcha_attempts"] >= 3:
        bot.answer_callback_query(call.id, "❌ Вы исчерпали 3 попытки. Напишите /start заново.")
        return

    if selected == target:
        user_data[user_id]["captcha_passed"] = True
        save_users(user_data)
        captcha_data.pop(user_id, None)
        bot.answer_callback_query(call.id, "✅ Каптча пройдена!")

        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(
            user_id,
            "🎉 Поздравляем, вы приняты в тиму!\n\n"
            "🔗 Вот ссылка для вступления:\n"
            "https://t.me/+0R4r9osfhvI1ZTNi",
            parse_mode="Markdown"
        )
        bot.send_message(
            user_id,
            "🌟 ГЛАВНОЕ МЕНЮ\n\n"
            "👋 Добро пожаловать в панель управления!\n"
            "Выберите нужный раздел ниже:",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
    else:
        user_data[user_id]["captcha_attempts"] += 1
        save_users(user_data)
        remaining = 3 - user_data[user_id]["captcha_attempts"]
        bot.answer_callback_query(call.id, f"❌ Неверно! Осталось попыток: {remaining}")

        emojis, new_target = generate_captcha()
        captcha_data[user_id] = (emojis, new_target)
        bot.edit_message_text(
            f"🔐 Пройди каптчу для входа\n\n"
            f"Нажми на эмодзи: {new_target}\n\n" + " ".join(emojis),
            user_id,
            call.message.message_id,
            reply_markup=captcha_markup(emojis, new_target),
            parse_mode="Markdown"
        )

# ===== ОСНОВНОЙ ОБРАБОТЧИК КНОПОК =====
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.message.chat.id)

    if user_id not in user_data or not user_data[user_id]["captcha_passed"]:
        bot.answer_callback_query(call.id, "Сначала пройди каптчу через /start")
        return

    # ===== ПРОФИЛЬ С СТАТИСТИКОЙ =====
    if call.data == "profile":
        user = user_data[user_id]
        scam_status = "🟢 Профи" if user.get('total_scammed', 0) > 10 else "🟡 Начинающий" if user.get('total_scammed', 0) > 3 else "🔴 Новичок"
        text = f"""👤 *ТВОЙ ПРОФИЛЬ*

📌 *Имя:* {message.from_user.first_name if hasattr(message, 'from_user') else 'Пользователь'}
🆔 *ID:* {user_id}

📊 *СТАТИСТИКА СКАМА:*
🎯 *Заскамлено:* {user.get('total_scammed', 0)} чел.
💰 *Заработано:* {user.get('total_earned', 0):.2f} TON
💎 *Баланс:* {user.get('balance', 0):.2f} TON

📈 *Статус:* {scam_status}

📅 *В команде:* {random.randint(1, 30)} дней"""
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    # ===== БАЛАНС =====
    elif call.data == "balance":
        user = user_data[user_id]
        text = f"""💰 *ТВОЙ БАЛАНС*

💎 *Баланс:* {user.get('balance', 0):.2f} TON
💰 *Всего заработано:* {user.get('total_earned', 0):.2f} TON
🎯 *Заскамлено:* {user.get('total_scammed', 0)} чел.

📊 *Средний чек:* {user.get('total_earned', 0) / user.get('total_scammed', 1):.2f} TON

💡 Минимальная выплата: 10 TON"""
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    # ===== ВЫПЛАТЫ =====
    elif call.data == "withdraw_menu":
        bot.edit_message_text(
            f"💸 *СИСТЕМА ВЫПЛАТ*\n\n"
            f"💎 Твой баланс: {user_data[user_id].get('balance', 0):.2f} TON\n\n"
            f"💰 Минимальная выплата: 10 TON\n"
            f"📋 Выбери действие:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=withdraw_menu_markup(),
            parse_mode="Markdown"
        )

    elif call.data == "withdraw_create":
        user = user_data[user_id]
        balance = user.get('balance', 0)
        
        if balance < 10:
            bot.answer_callback_query(call.id, "❌ Недостаточно средств! Минимум 10 TON")
            return
        
        amount = min(balance, 100)
        withdraw_id = f"WD{random.randint(1000, 9999)}"
        
        if "withdraws" not in user:
            user["withdraws"] = []
        
        user["withdraws"].append({
            "id": withdraw_id,
            "amount": amount,
            "status": "⏳ Ожидает",
            "date": datetime.now().strftime('%d.%m.%Y %H:%M')
        })
        
        user["balance"] -= amount
        save_users(user_data)
        
        bot.edit_message_text(
            f"✅ *ЗАЯВКА НА ВЫПЛАТУ СОЗДАНА!*\n\n"
            f"🆔 Номер: {withdraw_id}\n"
            f"💰 Сумма: {amount:.2f} TON\n"
            f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            f"⏳ Ожидайте подтверждения от администратора.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    elif call.data == "withdraw_history":
        user = user_data[user_id]
        withdraws = user.get("withdraws", [])
        
        if not withdraws:
            text = "📋 *ИСТОРИЯ ВЫПЛАТ*\n\nУ вас пока нет выплат."
        else:
            text = "📋 *ИСТОРИЯ ВЫПЛАТ*\n\n"
            for w in withdraws[-5:]:
                text += f"🆔 {w['id']} | {w['amount']:.2f} TON | {w['status']}\n"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    # ===== KPI: ГЛАВНОЕ МЕНЮ =====
    elif call.data == "kpi_main":
        bot.edit_message_text(
            "📊 *KPI ПАНЕЛЬ УПРАВЛЕНИЯ*\n\n"
            "Выберите направление для просмотра ключевых показателей эффективности:\n\n"
            "📌 *Доступные разделы:*\n"
            "• 💼 Продажи — клиенты, выручка, средний чек\n"
            "• 📢 Маркетинг — CPL, лиды, ROI\n"
            "• 🎯 Скам KPI — сколько заскамил и заработал\n\n"
            "🔄 Нажми «Обновить» для генерации новых данных",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=kpi_menu(),
            parse_mode="Markdown"
        )

    # ===== KPI: ПРОДАЖИ =====
    elif call.data == "kpi_sales":
        kpi_data = user_data[user_id].get("kpi_data", get_kpi_data())
        sales = kpi_data["sales"]
        
        text = f"""📊 *KPI ПРОДАЖИ*

📌 *Новые клиенты:* {sales['new_clients']}
💰 *Выручка за месяц:* {sales['revenue']:,} ₽
🧾 *Средний чек:* {sales['average_check']:,} ₽
🤝 *Закрытых сделок:* {sales['deals']}
📈 *Конверсия:* {sales['conversion']}%

{'🟢' if sales['new_clients'] > 30 else '🟡' if sales['new_clients'] > 15 else '🔴'} Динамика: {'Отлично!' if sales['new_clients'] > 30 else 'Нормально' if sales['new_clients'] > 15 else 'Нужно улучшать'}

📅 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}"""
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=kpi_menu(),
            parse_mode="Markdown"
        )

    # ===== KPI: МАРКЕТИНГ =====
    elif call.data == "kpi_marketing":
        kpi_data = user_data[user_id].get("kpi_data", get_kpi_data())
        marketing = kpi_data["marketing"]
        
        if marketing['cpl'] < 100:
            cpl_status = "🟢 Отлично! (низкая цена)"
        elif marketing['cpl'] < 250:
            cpl_status = "🟡 Средняя цена"
        else:
            cpl_status = "🔴 Высокая цена, нужно оптимизировать"
        
        text = f"""📊 *KPI МАРКЕТИНГ*

💵 *Цена привлечения лида (CPL):* {marketing['cpl']} ₽
👥 *Лидов:* {marketing['leads']}
📈 *ROI:* {marketing['roi']}%
💰 *Затраты на рекламу:* {marketing['ad_spend']:,} ₽
🎯 *CTR:* {marketing['ctr']}%

📌 *Оценка CPL:* {cpl_status}

{'🟢' if marketing['roi'] > 150 else '🟡' if marketing['roi'] > 80 else '🔴'} Эффективность: {'Высокая' if marketing['roi'] > 150 else 'Средняя' if marketing['roi'] > 80 else 'Низкая'}

📅 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}"""
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=kpi_menu(),
            parse_mode="Markdown"
        )

    # ===== KPI: СКАМ =====
    elif call.data == "kpi_scam":
        user = user_data[user_id]
        scam_data = user.get("kpi_data", get_kpi_data())["scam"]
        total_scammed = user.get('total_scammed', 0)
        total_earned = user.get('total_earned', 0)
        
        status = "🟢 Профи" if total_scammed > 10 else "🟡 Начинающий" if total_scammed > 3 else "🔴 Новичок"
        
        text = f"""🎯 *KPI СКАМА*

📌 *Заскамлено людей:* {total_scammed}
💰 *Заработано всего:* {total_earned:.2f} TON
💵 *Средний чек:* {total_earned / total_scammed if total_scammed > 0 else 0:.2f} TON
📈 *Успешность:* {scam_data['success_rate']}%

📌 *Статус:* {status}

📅 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}"""
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=kpi_menu(),
            parse_mode="Markdown"
        )

    # ===== KPI: ОБНОВИТЬ =====
    elif call.data == "kpi_refresh":
        user_data[user_id]["kpi_data"] = get_kpi_data()
        save_users(user_data)
        bot.answer_callback_query(call.id, "✅ KPI данные обновлены!")
        
        bot.edit_message_text(
            "📊 *KPI ПАНЕЛЬ УПРАВЛЕНИЯ*\n\n"
            "✅ Данные успешно обновлены!\n\n"
            "Выберите направление для просмотра:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=kpi_menu(),
            parse_mode="Markdown"
        )

    # ===== ПОДАРОК (MINI APP) =====
    elif call.data == "gift":
        markup = telebot.types.InlineKeyboardMarkup()
        web_app = telebot.types.WebAppInfo("https://stalwart-conkies-499882.netlify.app")
        button = telebot.types.InlineKeyboardButton(
            text="🎁 Открыть подарок",
            web_app=web_app
        )
        markup.add(button)
        markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back"))
        
        bot.edit_message_text(
            "🎁 *NFT ПОДАРОК*\n\n"
            "Тут ты можешь выиграть эксклюзивный NFT-подарок!\n\n"
            "📱 *Как играть:*\n"
            "1️⃣ Нажми на кнопку «Открыть подарок»\n"
            "2️⃣ Тапай по картинке\n"
            "3️⃣ Набери нужное количество тапов\n"
            "4️⃣ Получи свой приз! 🎉\n\n"
            "Удачи, мамонт! 💪",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # ===== ОСТАЛЬНЫЕ РАЗДЕЛЫ =====
    elif call.data == "shablon":
        bot.edit_message_text(
            "📄 ШАБЛОНЫ\n\n"
            "1️⃣ Шаблон А - Базовый\n"
            "2️⃣ Шаблон Б - Продвинутый\n"
            "3️⃣ Шаблон В - Премиум",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    elif call.data == "buty":
        bot.edit_message_text(
            "🍾 БУТЫ\n\n"
            "Доступные бусты:\n"
            "• 🚀 Буст 1 - 100 руб.\n"
            "• 🔥 Буст 2 - 250 руб.\n"
            "• 💎 Буст 3 - 500 руб.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    elif call.data == "manage":
        bot.edit_message_text(
            "⚙️ УПРАВЛЕНИЕ\n\n"
            "Что вы хотите сделать?\n"
            "• ✏️ Изменить данные\n"
            "• 🔑 Сменить пароль\n"
            "• 🚪 Выйти из аккаунта",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    elif call.data == "settings":
        bot.edit_message_text(
            "🛠 НАСТРОЙКИ\n\n"
            "🌐 Язык: Русский\n"
            "🔔 Уведомления: Включены\n"
            "🎨 Тема: Светлая\n"
            "🔒 Безопасность: Высокая",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    elif call.data == "projects":
        bot.edit_message_text(
            "ℹ️ О ПРОЕКТЕ\n\n"
            "🤖 Бот-панель v3.0\n"
            "💻 Создано в VS Code\n"
            "👨‍💻 Автор: Henryus\n"
            "📅 Дата: 13.08.2026",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    elif call.data == "market":
        bot.edit_message_text(
            "🛒 МАРКЕТ\n\n"
            "Доступные товары:\n"
            "1️⃣ Товар А - 100 руб.\n"
            "2️⃣ Товар Б - 200 руб.\n"
            "3️⃣ Товар В - 300 руб.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    elif call.data == "outcome":
        bot.edit_message_text(
            "💸 ОТС - ВЫПЛАТЫ И БОТЫ\n\n"
            "📊 Статистика:\n"
            "• 💰 Выплат: 5,000 руб.\n"
            "• 🤖 Активных ботов: 3\n"
            "• 📝 Всего операций: 15",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    elif call.data == "traffic":
        bot.edit_message_text(
            "📊 ТРАФИК\n\n"
            "Статистика за сегодня:\n"
            "👥 Посетителей: 156\n"
            "🔄 Переходов: 432\n"
            "📈 Конверсия: 12.5%\n\n"
            "📅 За неделю: +23%",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    elif call.data == "back":
        bot.edit_message_text(
            "🌟 ГЛАВНОЕ МЕНЮ\n\n"
            "👋 Добро пожаловать в панель управления!\n"
            "Выберите нужный раздел ниже:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    bot.answer_callback_query(call.id)

# ===== ЗАПУСК БОТА =====
if __name__ == '__main__':
    print("✅ Бот успешно запущен!")
    print("🤖 Ожидание сообщений...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            time.sleep(5)
