import os
import csv
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")

# =========================
# ЛОГ СТАТИСТИКИ
# =========================
def log_event(user, action: str):
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


# =========================
# INLINE-КНОПКИ
# =========================
def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Расписание", callback_data="menu_schedule")],
        [InlineKeyboardButton("Самое главное", callback_data="menu_features")],
        [InlineKeyboardButton("Кто мы?", callback_data="menu_whowe")],
    ])


def kb_back_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Назад", callback_data="back_main")]
    ])


def kb_features():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Хочу служить", callback_data="feat_serve")],
        [InlineKeyboardButton("Задать вопрос / предложение", callback_data="feat_feedback")],
        [InlineKeyboardButton("Найти домашку", callback_data="feat_homegroup")],
        [InlineKeyboardButton("Молитвенная поддержка", callback_data="feat_prays")],
        [InlineKeyboardButton("Назад", callback_data="back_main")],
    ])


def kb_back_features():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Назад", callback_data="back_features")]
    ])


# =========================
# СЛУЖЕНИЯ (ЛИСТАЛКА)
# =========================
APPLY_URL = "https://forms.yandex.ru/u/68e0b0bb50569060a96e8d2c"

SERVE_SLIDES = [
    {
        "image": "team.jpg",
        "text": (
            "здесь ты найдешь все команды и служения, которые делают одно большое дело, "
            "перелистывай через кнопки снизу, чтобы посмотреть их все\n\n"
            "если ты хочешь служить вместе с нами, выбери команду, которая запала в сердце, "
            "нажми на кнопку «Оставить заявку», и мы свяжемся с тобой!"
        ),
    },
    {
        "image": "media.jpg",
        "text": (
            "продакшн — это всё, что происходит за кадром: "
            "прямые трансляции, камеры, свет, экраны и видео для богослужений. "
            "команда, которая делает служение живым, чётким и современным\n\n"
            "если тебе близки камеры, съёмка, свет или видео — тебе в продакшн"
        ),
    },
    {
        "image": "praise.jpg",
        "text": (
            "команда прославления — это поклонение Богу через музыку\n\n"
            "если ты играешь, поёшь или хочешь развивать музыкальный дар для Бога — присоединяйся!"
        ),
    },
    {
        "image": "poryadok.jpg",
        "text": (
            "команда порядка создаёт комфорт на служении: встречают людей, помогают, следят за порядком\n\n"
            "если тебе близко служение делом — добро пожаловать"
        ),
    },
    {
        "image": "eda.jpg",
        "text": (
            "хозяюшки — служение заботы и тепла. готовка, общение, атмосфера дома\n\n"
            "если любишь заботиться о людях — тебе сюда!"
        ),
    },
    {
        "image": "smm.jpg",
        "text": (
            "SMM — это всё, что ты видишь в соцсетях молодёжки\n\n"
            "если тебе близки рилсы, тексты, дизайн или идеи — давай к нам!"
        ),
    },
    {
        "image": "Jesus.jpg",
        "text": (
            "евангелизация — это выход за стены церкви\n\n"
            "если тебе важно делиться Евангелием с людьми — присоединяйся!"
        ),
    },
]


def kb_serve(index: int):
    total = len(SERVE_SLIDES)
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀", callback_data="srv_prev"),
            InlineKeyboardButton(f"{index+1}/{total}", callback_data="noop"),
            InlineKeyboardButton("▶", callback_data="srv_next"),
        ],
        [InlineKeyboardButton("Оставить заявку", url=APPLY_URL)],
        [InlineKeyboardButton("Назад", callback_data="back_features")],
    ])


# =========================
# УТИЛИТА РЕДАКТИРОВАНИЯ
# =========================
async def safe_edit(update, image, caption, keyboard):
    q = update.callback_query
    await q.answer(cache_time=1)

    try:
        await q.message.edit_media(
            media=InputMediaPhoto(
                media=open(image, "rb"),
                caption=caption,
                parse_mode="HTML",
            ),
            reply_markup=keyboard,
        )
    except Exception as e:
        print("EDIT FAILED → SEND NEW:", e)
        await q.message.reply_photo(
            photo=open(image, "rb"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard,
        )


# =========================
# /START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_event(user, "/start")

    caption = (
        'привет! давай знакомиться?\n\n'
        '• это бот молодежного служения Церковь "Жатвы", г. Курган.\n'
        'если хочешь узнать о нас больше — заходи в тг-канал:\n'
        '<a href="https://t.me/HarvestYouth">HarvestYouth</a>\n\n'
        '• каждое воскресенье в 14:30 я жду тебя по адресу:\n'
        '<a href="https://yandex.ru/maps/-/CLseE4oL">Курган, ул. Техническая, д. 8</a>\n\n'
        '• если ты пришел на молодежку первый раз — обязательно напиши:\n'
        '@romanmurash, будем на связи'
    )

    await update.message.reply_photo(
        photo=open("welcome.jpg", "rb"),
        caption=caption,
        parse_mode="HTML",
        reply_markup=kb_main(),
    )


# =========================
# CALLBACK HANDLER
# =========================
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data or ""
    user = q.from_user

    if data == "noop":
        await q.answer()
        return

    if data == "back_main":
        await safe_edit(update, "welcome.jpg", start_caption := (
            'привет! давай знакомиться?\n\n'
            '• это бот молодежного служения Церковь "Жатвы", г. Курган.\n'
            'если хочешь узнать о нас больше — заходи в тг-канал:\n'
            '<a href="https://t.me/HarvestYouth">HarvestYouth</a>\n\n'
            '• каждое воскресенье в 14:30 я жду тебя по адресу:\n'
            '<a href="https://yandex.ru/maps/-/CLseE4oL">Курган, ул. Техническая, д. 8</a>\n\n'
            '• если ты пришел на молодежку первый раз — обязательно напиши:\n'
            '@romanmurash, будем на связи'
        ), kb_main())
        return

    if data == "menu_whowe":
        await safe_edit(update, "whowe.jpg", (
            "мы подготовили для тебя пост, где ты сможешь узнать о том, кто мы такие\n"
            '<a href="https://t.me/HarvestYouth/890">о нас</a>'
        ), kb_back_main())
        return

    if data == "menu_schedule":
        await safe_edit(update, "time.jpg", (
            "актуальное расписание на неделю всегда появляется в нашем Telegram-канале в понедельник:\n"
            '<a href="https://t.me/HarvestYouth">перейти в канал</a>'
        ), kb_back_main())
        return

    if data == "menu_features":
        await safe_edit(update, "main.jpg", (
            "здесь есть всё, что может быть тебе полезным, друг!\n\n"
            "мы всегда открыты для диалога, молитвы и общения"
        ), kb_features())
        return

    if data == "back_features":
        await safe_edit(update, "main.jpg", (
            "здесь есть всё, что может быть тебе полезным, друг!\n\n"
            "мы всегда открыты для диалога, молитвы и общения"
        ), kb_features())
        return

    if data == "feat_serve":
        log_event(user, "Хочу служить")
        context.user_data["srv_idx"] = 0
        slide = SERVE_SLIDES[0]
        await safe_edit(update, slide["image"], slide["text"], kb_serve(0))
        return

    if data in ("srv_prev", "srv_next"):
        idx = context.user_data.get("srv_idx", 0)
        idx = (idx - 1) % len(SERVE_SLIDES) if data == "srv_prev" else (idx + 1) % len(SERVE_SLIDES)
        context.user_data["srv_idx"] = idx
        slide = SERVE_SLIDES[idx]
        await safe_edit(update, slide["image"], slide["text"], kb_serve(idx))
        return

    if data == "feat_feedback":
        await safe_edit(update, "feedback.jpg", (
            "у нас к тебе три вопроса:\n"
            "1. ты нашел ошибку в постах?\n"
            "2. у тебя есть крутое предложение?\n"
            "3. хочешь нас поругать или похвалить?\n\n"
            '<a href="https://forms.yandex.ru/u/693838eb49af47b74be7c00e">написать сообщение!</a>'
        ), kb_back_features())
        return

    if data == "feat_homegroup":
        await safe_edit(update, "homegroup.jpg", (
            "домашняя группа — это место, где можно поговорить по-честному, разобраться в Библии и найти своих людей!\n\n"
            '<a href="https://forms.yandex.ru/u/6938307f1f1eb5cddcef1b93">найти домашку</a>'
        ), kb_back_features())
        return

    if data == "feat_prays":
        await safe_edit(update, "prays.jpg", (
            "молитвенная поддержка — это Божья атмосфера помощи и единства!\n\n"
            '<a href="https://forms.yandex.ru/u/68446f8c505690a7125513ca">отправить молитвенную нужду!</a>'
        ), kb_back_features())
        return


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используй кнопки меню 🙂")


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()


if __name__ == "__main__":
    main()
