import telebot
import time
import random
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "8505372036:AAEf3B8QrqRKKJxo8B7OkrGNX41s2MCMx3Y"

bot = telebot.TeleBot(TOKEN)

USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

user_data = load_users()
captcha_data = {}

def generate_captcha():
    emojis = ["🍎", "🍌", "🍇", "🍉", "🍓", "🍒", "🍑", "🍊", "🍋", "🍍", "🥝", "🥑", "🍆", "🥕", "🌽", "🍩", "🍪", "🎂", "🧁", "🍫", "🍬", "🍭", "🍮"]
    chosen = random.sample(emojis, 6)
    return chosen

def captcha_markup(correct):
    random.shuffle(correct)
    markup = InlineKeyboardMarkup(row_width=3)
    for emoji in correct:
        markup.add(InlineKeyboardButton(emoji, callback_data=f"captcha_{emoji}"))
    return markup

def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        InlineKeyboardButton("📄 Шаблоны", callback_data="shablon"),
        InlineKeyboardButton("🍾 Буты", callback_data="buty"),
        InlineKeyboardButton("⚙️ Управление", callback_data="manage"),
        InlineKeyboardButton("🛠 Настройки", callback_data="settings"),
        InlineKeyboardButton("ℹ️ О проекте", callback_data="projects"),
        InlineKeyboardButton("🛒 Маркет", callback_data="market"),
        InlineKeyboardButton("💸 ОТС - выплаты", callback_data="outcome"),
        InlineKeyboardButton("📊 Трафик", callback_data="traffic"),
        InlineKeyboardButton("🎁 Подарок", callback_data="giftgame")  # НОВАЯ КНОПКА
    )
    return markup

def profile_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📋 Рефералка", callback_data="referral"),
        InlineKeyboardButton("👨‍🏫 Наставники", callback_data="mentors"),
        InlineKeyboardButton("🏷 Изменить тэг", callback_data="change_tag"),
        InlineKeyboardButton("📊 Фон профитов", callback_data="profit_fond"),
        InlineKeyboardButton("👁 Показать тэг", callback_data="show_tag"),
        InlineKeyboardButton("💰 Выплаты", callback_data="payments"),
        InlineKeyboardButton("💳 Кошелёк", callback_data="wallet"),
        InlineKeyboardButton("💸 Вывести баланс", callback_data="withdraw"),
        InlineKeyboardButton("➕ Пополнить", callback_data="deposit"),
        InlineKeyboardButton("🔄 Перевести", callback_data="transfer"),
        InlineKeyboardButton("🛡 Страховка", callback_data="insurance"),
        InlineKeyboardButton("🔙 Главное меню", callback_data="back")
    )
    return markup

def mentors_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("👨‍🏫 @Stoprar (10%)", callback_data="mentor_stoprar"),
        InlineKeyboardButton("🔙 Назад в профиль", callback_data="profile")
    )
    return markup

def back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))
    return markup

def back_profile():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Назад в профиль", callback_data="profile"))
    return markup

# ===== КНОПКА ДЛЯ MINI APP =====
def giftgame_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🎁 Открыть подарок", web_app=WebAppInfo(url="https://kad22904-max.github.io/tap-miniapp/webapp.html"))
    )
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))
    return markup

# ===== КОМАНДА /start =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.chat.id)

    if user_id not in user_data:
        user_data[user_id] = {"captcha_passed": False, "mentor": None, "captcha_attempts": 0}
        save_users(user_data)

    if not user_data[user_id]["captcha_passed"]:
        emojis = generate_captcha()
        captcha_data[user_id] = emojis
        bot.send_message(
            user_id,
            "🔐 Пройди каптчу для входа:\n\n"
            "Нажми на кнопку с последним эмодзи из этого списка:\n" + " ".join(emojis),
            reply_markup=captcha_markup(emojis),
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

# ===== КАПТЧА =====
@bot.callback_query_handler(func=lambda call: call.data.startswith("captcha_"))
def handle_captcha(call):
    user_id = str(call.message.chat.id)
    selected = call.data.split("_")[1]
    correct = captcha_data.get(user_id, [])

    if not correct:
        bot.edit_message_text(
            "❌ Каптча устарела. Напиши /start заново.",
            user_id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        return

    if user_data[user_id]["captcha_attempts"] >= 3:
        bot.edit_message_text(
            "❌ Вы исчерпали 3 попытки. Напишите /start заново.",
            user_id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        return

    if selected == correct[-1]:
        user_data[user_id]["captcha_passed"] = True
        save_users(user_data)
        captcha_data.pop(user_id, None)
        bot.edit_message_text(
            "✅ Каптча пройдена!",
            user_id,
            call.message.message_id,
            parse_mode="Markdown"
        )
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
        bot.edit_message_text(
            f"❌ Неверно! Осталось попыток: {3 - user_data[user_id]['captcha_attempts']}",
            user_id,
            call.message.message_id,
            reply_markup=captcha_markup(correct),
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id)

# ===== ОСНОВНЫЕ КНОПКИ =====
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.message.chat.id)

    if user_id not in user_data or not user_data[user_id]["captcha_passed"]:
        bot.answer_callback_query(call.id, "Сначала пройди каптчу через /start")
        return

    # ===== MINI APP =====
    if call.data == "giftgame":
        bot.edit_message_text(
            "🎁 ТАПАЙ ПОДАРОК\n\n"
            "Нажми на кнопку ниже, открой мини-приложение и тапай по подарку!\n"
            "После 100 тапов ты получишь выигрыш!",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=giftgame_markup(),
            parse_mode="Markdown"
        )

    elif call.data == "back":
        bot.edit_message_text(
            "🌟 ГЛАВНОЕ МЕНЮ\n\n"
            "👋 Добро пожаловать в панель управления!\n"
            "Выберите нужный раздел:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    elif call.data == "profile":
        bot.edit_message_text(
            "👤 ТВОЙ ПРОФИЛЬ\n\n"
            "📌 Имя: Henryus\n"
            "🆔 Telegram ID: 8936341915\n"
            "🏷 Тэг: Скрыт\n"
            "📊 Статус: Воркер\n\n"
            "👨‍🏫 Наставник: –\n"
            "💰 TON Кошелёк: –\n"
            "💎 Баланс: 0.00 TON\n"
            "💸 Выплачено: 0.00 TON\n"
            "📈 Процент выплат: 80%\n\n"
            "📅 Дней в команде: 4\n"
            "🛡 Страховка профита: включена",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=profile_menu(),
            parse_mode="Markdown"
        )

    elif call.data == "mentors":
        bot.edit_message_text(
            "👨‍🏫 ВЫБОР НАСТАВНИКА\n\n"
            "Выбери наставника и начни зарабатывать!\n\n"
            "📌 Выбранный наставник будет помогать тебе с поиском и обработкой твоих первых мамонтов.\n\n"
            "📌 Процент, указанный рядом с ником наставника, будет вычитаться из суммы твоего профита в течение первых 50 профитов с начала наставничества.\n\n"
            "✅ Если ты согласен с условиями, выбери одного из наставников:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=mentors_menu(),
            parse_mode="Markdown"
        )

    elif call.data == "mentor_stoprar":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Да, готов!", callback_data="confirm_stoprar"),
            InlineKeyboardButton("🔙 Назад", callback_data="profile")
        )
        bot.edit_message_text(
            "Ты уверен, что хочешь выбрать наставником @stoprar?\n\n"
            "💬 Послание наставника\n"
            "👍 Все еще сомневаешься? Пока ты думаешь, другие уже выводят кэш.\n"
            "🦣 Твой личный билет в профит\n"
            "👍 @stoprar — наставник, который не просто покажет дорогу, а доведет тебя до первых реальных денег. Никакой теории из гугла — только чистая практика.\n\n"
            "Почему выбирают именно @stoprar?\n"
            "🔥 Опыт с августа 2025 — прошел все штормы рынка и собрал самые свежие фишки.\n"
            "👍 6+ месяцев в топе — ежедневная практика, доведенная до автоматизма.\n"
            "👏 Миллионные кассы учеников — сотни ребят прямо сейчас делают результат.\n\n"
            "Что тебя ждет внутри:\n"
            "👍 Связь 24/7 — плотный коннект и поддержка на каждом шагу.\n"
            "👑 Пошаговая система — без воды, заумных терминов и скучной рутины.\n"
            "💵 Разбор полетов — личный анализ твоих ошибок для моментального роста.\n"
            "👊 Эксклюзивный бонус: Полная поддержка и ведение даже после официальной отвязки!\n\n"
            "👍 Внимание: Места в группе жестко ограничены. Не останься за бортом.\n"
            "👍 Важно: отвязать наставника можно только через 50 профитов.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif call.data == "confirm_stoprar":
        bot.edit_message_text(
            "✅ Вы выбрали наставника @stoprar!\n\n"
            "🎉 Добро пожаловать в команду!\n"
            "🔗 Переходи по ссылке:\n"
            "https://t.me/+0R4r9osfhvI1ZTNi",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_profile(),
            parse_mode="Markdown"
        )

    elif call.data == "referral":
        bot.edit_message_text(
            "📋 РЕФЕРАЛКА\n\n"
            "Ваша реферальная ссылка:\n"
            "https://t.me/ваш_бот?start=ref_ваш_код\n\n"
            "👥 Приглашено: 0\n"
            "💰 Заработано: 0.00 TON",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_profile(),
            parse_mode="Markdown"
        )

    elif call.data == "change_tag":
        bot.edit_message_text(
            "🏷 ИЗМЕНИТЬ ТЭГ\n\n"
            "Введите новый тэг для профиля.\n"
            "Тэг должен быть уникальным.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_profile(),
            parse_mode="Markdown"
        )

    elif call.data == "profit_fond":
        bot.edit_message_text(
            "📊 ФОН ПРОФИТОВ\n\n"
            "Всего в фонде: 1000 TON\n"
            "Ваша доля: 0.00 TON\n"
            "Процент: 0%",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_profile(),
            parse_mode="Markdown"
        )

    elif call.data == "show_tag":
        bot.edit_message_text(
            "👁 ПОКАЗАТЬ ТЭГ\n\n"
            "Ваш тэг: Скрыт\n"
            "Статус: Скрыт (виден только вам)",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_profile(),
            parse_mode="Markdown"
        )

    elif call.data == "payments":
        bot.edit_message_text(
            "💰 ВЫПЛАТЫ\n\n"
            "История выплат:\n"
            "📅 13.08.2026: +0.00 TON\n"
            "Всего выплачено: 0.00 TON",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_profile(),
            parse_mode="Markdown"
        )

    elif call.data == "wallet":
        bot.edit_message_text(
            "💳 КОШЕЛЁК\n\n"
            "💰 Баланс: 0.00 TON\n"
            "💳 TON Кошелёк: –\n\n"
            "Выберите действие:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_profile(),
            parse_mode="Markdown"
        )

    elif call.data == "withdraw":
        bot.edit_message_text(
            "💸 ВЫВЕСТИ БАЛАНС\n\n"
            "💰 Доступно: 0.00 TON\n"
            "Минимальная сумма вывода: 10 TON\n\n"
            "Введите сумму для вывода:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_profile(),
            parse_mode="Markdown"
        )

    elif call.data == "deposit":
        bot.edit_message_text(
            "➕ ПОПОЛНИТЬ\n\n"
            "💳 Адрес для пополнения:\n"
            "EQD...ваш_адрес\n\n"
            "Минимальная сумма: 10 TON",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_profile(),
            parse_mode="Markdown"
        )

    elif call.data == "transfer":
        bot.edit_message_text(
            "🔄 ПЕРЕВЕСТИ\n\n"
            "💰 Баланс: 0.00 TON\n"
            "Введите ID получателя и сумму:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_profile(),
            parse_mode="Markdown"
        )

    elif call.data == "insurance":
        bot.edit_message_text(
            "🛡 СТРАХОВКА\n\n"
            "Статус: ✅ Включена\n"
            "Страховка профита активна.\n"
            "Вы защищены от потерь!",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_profile(),
            parse_mode="Markdown"
        )

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

    else:
        bot.edit_message_text(
            f"✅ Вы выбрали раздел",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button()
        )

    bot.answer_callback_query(call.id)

# ===== ЗАПУСК =====
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
