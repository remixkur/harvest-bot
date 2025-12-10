from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from datetime import datetime
import csv
import os
import json

# ТОКЕН ИЗ ПЕРЕМЕННОЙ ОКРУЖЕНИЯ
TOKEN = os.getenv("TOKEN")

# ФАЙЛ ДЛЯ СОХРАНЕНИЯ ПОСЛЕДНЕГО ПОСТА С РАСПИСАНИЕМ
SCHEDULE_FILE = "schedule.json"


# === ФУНКЦИИ РАБОТЫ С РАСПИСАНИЕМ ===

def save_schedule(chat_id: int, message_id: int) -> None:
    """Сохраняем, откуда копировать пост с расписанием."""
    data = {"chat_id": chat_id, "message_id": message_id}
    try:
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        print("Сохранил новое расписание:", data)
    except Exception as e:
        print("Ошибка сохранения расписания:", e)


def load_schedule():
    """Читаем сохранённый пост с расписанием, если он есть."""
    if not os.path.exists(SCHEDULE_FILE):
        return None
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Ошибка чтения расписания:", e)
        return None


# === ФУНКЦИЯ ЛОГА СТАТИСТИКИ ===

def log_event(user, action: str):
    """
    Пишем строку в stats.csv:
    время; id; username; имя; действие
    """
    try:
        with open("stats.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                user.id,
                user.username or "",
                f"{user.first_name or ''} {user.last_name or ''}".strip(),
                action,
            ])
    except Exception as e:
        print("Ошибка записи статистики:", e)


# === КЛАВИАТУРЫ ===

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton("Расписание")],
        [KeyboardButton("Самое главное")],
        [KeyboardButton("Кто мы?")],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def main_menu_with_back_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton("Расписание")],
        [KeyboardButton("Самое главное")],
        [KeyboardButton("Кто мы?")],
        [KeyboardButton("Назад")],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def features_menu_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton("Хочу служить"), KeyboardButton("Задать вопрос / предложение")],
        [KeyboardButton("Найти домашку"), KeyboardButton("Молитвенная поддержка")],
        [KeyboardButton("Назад")],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


# === ВОЗВРАТ НА СТАРТОВЫЙ ЭКРАН ===

async def send_start_screen(update: Update):
    user = update.message.from_user
    log_event(user, "start_screen")

    await update.message.reply_photo(
        photo=open("welcome.jpg", "rb"),
        caption=(
            'привет! давай знакомиться?\n\n'
            '• это бот молодежного служения Церковь "Жатвы", г. Курган.\n'
            'если хочешь узнать о нас больше — заходи в тг-канал:\n'
            '<a href="https://t.me/HarvestYouth">HarvestYouth</a>\n\n'
            '• каждое воскресенье в 14:30 я жду тебя по адресу:\n'
            '<a href="https://yandex.ru/maps/-/CLseE4oL">Курган, ул. Техническая, д. 8</a>\n\n'
            '• если ты пришел на молодежку первый раз — обязательно напиши:\n'
            '@romanmurash, будем на связи'
        ),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


# === /START ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_event(user, "/start")
    await send_start_screen(update)


# === ХЕНДЛЕР ПОСТОВ КАНАЛА (ЛОВИМ ФРАЗУ ИЗ РАСПИСАНИЯ) ===

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if not msg:
        return

    text = (msg.text or msg.caption or "").lower()

    # фраза, которая есть только в посте с расписанием
    phrase1 = "для тех, кто ещё не нашёл своё служение"
    phrase2 = "для тех, кто еще не нашел свое служение"  # вариант без ё

    if phrase1 in text or phrase2 in text:
        save_schedule(msg.chat_id, msg.message_id)


# === ОСНОВНОЙ ХЕНДЛЕР ТЕКСТА ===

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    user = update.message.from_user

    # --- НАЗАД ---
    if text == "Назад":
        log_event(user, "Назад")
        await send_start_screen(update)
        return

    # --- КТО МЫ ---
    if text == "Кто мы?":
        log_event(user, "Кто мы?")
        msg = (
            "хочешь узнать кто мы?\n"
            "читай в этом посте:\n"
            '<a href="https://t.me/HarvestYouth/890">о нас</a>'
        )
        await update.message.reply_text(
            msg, parse_mode="HTML", reply_markup=main_menu_with_back_keyboard()
        )
        return

    # --- РАСПИСАНИЕ ---
    if text == "Расписание":
        log_event(user, "Расписание")

        # Пытаемся взять последнее расписание из канала
        data = load_schedule()
        if data:
            try:
                # Копируем пост из канала пользователю
                await context.bot.copy_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=data["chat_id"],
                    message_id=data["message_id"],
                )
                return
            except Exception as e:
                print("Ошибка копирования расписания:", e)

        # Если нет сохранённого расписания или ошибка — запасной вариант
        try:
            await update.message.reply_photo(
                photo=open("time.jpg", "rb"),
                caption=(
                    "актуальное расписание всегда появляется в нашем Telegram-канале:\n"
                    '<a href="https://t.me/HarvestYouth">перейти в канал</a>\n\n'
                    "каждый понедельник в нём выходит свежая инфа на всю неделю!"
                ),
                parse_mode="HTML",
                reply_markup=main_menu_with_back_keyboard(),
            )
        except Exception:
            await update.message.reply_text(
                'актуальное расписание: <a href="https://t.me/HarvestYouth">наш канал</a>',
                parse_mode="HTML",
                reply_markup=main_menu_with_back_keyboard(),
            )
        return

    # --- САМОЕ ГЛАВНОЕ ---
    if text == "Самое главное":
        log_event(user, "Самое главное")
        intro = (
            "здесь есть всё, что может быть тебе полезным, друг!\n\n"
            "мы всегда открыты для диалога, молитвы и общения."
        )

        try:
            await update.message.reply_photo(
                photo=open("main.jpg", "rb"),
                caption=intro,
                reply_markup=features_menu_keyboard(),
            )
        except Exception:
            await update.message.reply_text(intro, reply_markup=features_menu_keyboard())
        return

    # --- ХОЧУ СЛУЖИТЬ ---
    if text == "Хочу служить":
        log_event(user, "Хочу служить")
        caption = (
            "хочешь помогать в церкви? это очень круто!\n"
            "каждое служение — это шанс расти, найти своё призвание и делать что-то значимое для других.\n\n"
            "заполняй заявку по ссылке ниже и мы с радостью свяжемся с тобой!\n"
            '<a href="https://forms.yandex.ru/u/68e0b0bb50569060a96e8d2c">хочу служить!</a>'
        )

        try:
            await update.message.reply_photo(
                photo=open("volonter.jpg", "rb"),
                caption=caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
            )
        except Exception:
            await update.message.reply_text(
                caption, parse_mode="HTML", reply_markup=features_menu_keyboard()
            )
        return

    # --- НАЙТИ ДОМАШКУ ---
    if text == "Найти домашку":
        log_event(user, "Найти домашку")
        caption = (
            "домашняя группа — это место, где можно поговорить по-честному, "
            "разобраться в Библии, задать любые вопросы и найти своих людей. "
            "тут поддержат, помолятся и помогут расти в вере не в одиночку!\n\n"
            '<a href="https://forms.yandex.ru/u/6938307f1f1eb5cddcef1b93">найти домашку</a>'
        )

        try:
            await update.message.reply_photo(
                photo=open("homegroup.jpg", "rb"),
                caption=caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
            )
        except Exception:
            await update.message.reply_text(
                caption, parse_mode="HTML", reply_markup=features_menu_keyboard()
            )
        return

    # --- ЗАДАТЬ ВОПРОС / ПРЕДЛОЖЕНИЕ ---
    if text == "Задать вопрос / предложение":
        log_event(user, "Задать вопрос / предложение")
        caption = (
            "у нас к тебе три вопроса:\n"
            "1. ты нашел ошибку в постах?\n"
            "2. у тебя есть крутое предложение?\n"
            "3. хочешь нас поругать или похвалить?\n\n"
            "пиши про это в форме ниже!\n"
            '<a href="https://forms.yandex.ru/u/693838eb49af47b74be7c00e">написать сообщение!</a>'
        )

        try:
            await update.message.reply_photo(
                photo=open("feedback.jpg", "rb"),
                caption=caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
            )
        except Exception:
            await update.message.reply_text(
                caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
            )
        return

    # --- МОЛИТВЕННАЯ ПОДДЕРЖКА ---
    if text == "Молитвенная поддержка":
        log_event(user, "Молитвенная поддержка")
        caption = (
            "молитвенная поддержка – это Божья атмосфера помощи и единства, "
            "которая способна изменить твою жизнь и все обстоятельства вокруг.\n\n"
            "отправь свою просьбу анонимно по ссылке ниже, наша команда за всё помолится!\n\n"
            '<a href="https://forms.yandex.ru/u/68446f8c505690a7125513ca">отправить молитвенную нужду!</a>'
        )

        try:
            await update.message.reply_photo(
                photo=open("prays.jpg", "rb"),
                caption=caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
            )
        except Exception:
            await update.message.reply_text(
                caption, parse_mode="HTML", reply_markup=features_menu_keyboard()
            )
        return

    # --- ЕСЛИ НЕ ПОНЯЛ ---
    log_event(user, f"непонятный ввод: {text}")
    await update.message.reply_text(
        "Не понял тебя. Выбери, пожалуйста, пункт в меню ниже.",
        reply_markup=main_menu_keyboard(),
    )


# === ЗАПУСК БОТА ===

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # /start
    app.add_handler(CommandHandler("start", start))
    # посты в канале (бот должен быть админом канала)
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))
    # личка/чаты
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен. Нажми Ctrl+C, чтобы остановить.")
    app.run_polling()


if __name__ == "__main__":
    main()
