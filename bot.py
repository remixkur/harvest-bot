from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
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


# === НАСТРОЙКИ ===

TOKEN = os.getenv("TOKEN")  # переменная окружения TOKEN
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # папка, где лежит bot.py


# === УТИЛИТЫ ===

def abs_path(filename: str) -> str:
    """Абсолютный путь к файлам рядом с bot.py"""
    return os.path.join(BASE_DIR, filename)


def log_event(user, action: str):
    """
    Пишем строку в stats.csv:
    время; id; username; имя; действие
    """
    try:
        with open(abs_path("stats.csv"), "a", newline="", encoding="utf-8") as f:
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


async def safe_reply_photo(update: Update, filename: str, caption: str = "", parse_mode: str | None = None, reply_markup=None) -> bool:
    """
    Пытаемся отправить фото. Если не получилось — возвращаем False.
    """
    try:
        with open(abs_path(filename), "rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
        return True
    except Exception as e:
        print(f"Ошибка при отправке фото {filename}:", e)
        return False


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


# === СТАРТОВЫЙ ЭКРАН ===

START_CAPTION = (
    'привет! давай знакомиться?\n\n'
    '• это бот молодежного служения Церковь "Жатвы", г. Курган.\n'
    'если хочешь узнать о нас больше — заходи в тг-канал:\n'
    '<a href="https://t.me/HarvestYouth">HarvestYouth</a>\n\n'
    '• каждое воскресенье в 14:30 я жду тебя по адресу:\n'
    '<a href="https://yandex.ru/maps/-/CLseE4oL">Курган, ул. Техническая, д. 8</a>\n\n'
    '• если ты пришел на молодежку первый раз — обязательно напиши:\n'
    '@romanmurash, будем на связи'
)


async def send_start_screen(update: Update):
    user = update.message.from_user
    log_event(user, "start_screen")

    # Пытаемся отправить welcome-картинку.
    ok = await safe_reply_photo(
        update,
        "welcome.jpg",
        caption=START_CAPTION,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )

    # Если фото не отправилось — всё равно показываем текст и меню.
    if not ok:
        await update.message.reply_text(
            START_CAPTION,
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )


# === /START ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_event(user, "/start")
    await send_start_screen(update)


# === ОСНОВНОЙ ХЕНДЛЕР ===

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
            msg,
            parse_mode="HTML",
            reply_markup=main_menu_with_back_keyboard(),
        )
        return

    # --- РАСПИСАНИЕ ---
    if text == "Расписание":
        log_event(user, "Расписание")
        caption = (
            "актуальное расписание всегда появляется в нашем Telegram-канале:\n"
            '<a href="https://t.me/HarvestYouth">перейти в канал</a>\n\n'
            "каждый понедельник в нём выходит свежая инфа на всю неделю!"
        )

        ok = await safe_reply_photo(
            update,
            "time.jpg",
            caption=caption,
            parse_mode="HTML",
            reply_markup=main_menu_with_back_keyboard(),
        )
        if not ok:
            await update.message.reply_text(
                caption,
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

        ok = await safe_reply_photo(
            update,
            "main.jpg",
            caption=intro,
            reply_markup=features_menu_keyboard(),
        )
        if not ok:
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

        ok = await safe_reply_photo(
            update,
            "volonter.jpg",
            caption=caption,
            parse_mode="HTML",
            reply_markup=features_menu_keyboard(),
        )
        if not ok:
            await update.message.reply_text(
                caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
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

        ok = await safe_reply_photo(
            update,
            "homegroup.jpg",
            caption=caption,
            parse_mode="HTML",
            reply_markup=features_menu_keyboard(),
        )
        if not ok:
            await update.message.reply_text(
                caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
            )
        return

    # --- ОБРАТНАЯ СВЯЗЬ ---
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

        ok = await safe_reply_photo(
            update,
            "feedback.jpg",
            caption=caption,
            parse_mode="HTML",
            reply_markup=features_menu_keyboard(),
        )
        if not ok:
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

        ok = await safe_reply_photo(
            update,
            "prays.jpg",
            caption=caption,
            parse_mode="HTML",
            reply_markup=features_menu_keyboard(),
        )
        if not ok:
            await update.message.reply_text(
                caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
            )
        return

    # --- ЕСЛИ НЕ ПОНЯЛ ---
    log_event(user, f"непонятный ввод: {text}")
    await update.message.reply_text(
        "Не понял тебя. Выбери, пожалуйста, пункт в меню ниже.",
        reply_markup=main_menu_keyboard(),
    )


# === ЗАПУСК ===

def main():
    if not TOKEN:
        raise RuntimeError("Переменная окружения TOKEN не задана!")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен. Нажми Ctrl+C, чтобы остановить.")
    app.run_polling()


if __name__ == "__main__":
    main()
