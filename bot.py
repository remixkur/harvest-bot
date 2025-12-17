from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from datetime import datetime
import csv
import os

# =========================
# НАСТРОЙКИ
# =========================

TOKEN = os.getenv("TOKEN")  # токен хранится в переменных окружения
if not TOKEN:
    raise RuntimeError("TOKEN env var is missing. Set TOKEN in environment.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def file_path(name: str) -> str:
    return os.path.join(BASE_DIR, name)

# Ссылка на заявку (одна на всех слайдах)
SERVE_FORM_URL = "https://forms.yandex.ru/u/68e0b0bb50569060a96e8d2c"

# Слайды "Хочу служить" (0 = вступление)
SERVE_SLIDES = [
    {
        "title": "ХОЧУ СЛУЖИТЬ",
        "text": (
            "здесь ты найдешь все команды и служения, которые делают одно большое дело. "
            "перелистывай через кнопки снизу, чтобы посмотреть их все.\n\n"
            "если ты хочешь служить вместе с нами, выбери команду, которая запала в сердце, "
            "нажми на кнопку «Оставить заявку», и мы свяжемся с тобой"
        ),
        "image": "team.jpg",
        "has_apply": True,
    },
    {
        "title": "Продакшн",
        "text": (
            "продакшн — это всё, что происходит за кадром. прямые трансляции, камеры, свет, "
            "экраны и видео для богослужений. команда, которая делает служение живым, чётким и современным.\n\n"
            "если тебе близки камеры, съёмка, свет, экраны или ты хочешь научиться работать с техникой и видео — "
            "тебе в продакшн."
        ),
        "image": "media.jpg",
        "has_apply": True,
    },
    {
        "title": "Прославление",
        "text": (
            "команда прославления — это про поклонение Богу через музыку. музыканты и вокалисты, "
            "которые ведут церковь в поклонении и создают атмосферу, где Бог в центре.\n\n"
            "если ты играешь на инструменте, поёшь или хочешь развивать свой музыкальный дар для Бога — "
            "присоединяйся к команде прославления."
        ),
        "image": "praise.jpg",
        "has_apply": True,
    },
    {
        "title": "Команда порядка",
        "text": (
            "команда порядка — это те, кто создают комфорт на служении. они встречают людей у входа, "
            "помогают сориентироваться, следят за порядком в зале, гардеробом и подготовкой пространства. "
            "именно через них люди чувствуют заботу и внимание с первых минут.\n\n"
            "если тебе откликается встречать людей, помогать и служить делом — добро пожаловать в команду порядка."
        ),
        "image": "poryadok.jpg",
        "has_apply": True,
    },
    {
        "title": "Хозяюшки",
        "text": (
            "хозяюшки — это служение заботы и тепла. ребята, которые готовят еду к молодёжке и создают атмосферу дома, "
            "где хочется остаться, пообщаться и быть своим. через простые вещи они показывают любовь и внимание к каждому.\n\n"
            "если тебе нравится готовить, заботиться о людях и служить через практичные дела — тебе в служение хозяюшек."
        ),
        "image": "eda.jpg",
        "has_apply": True,
    },
    {
        "title": "SMM",
        "text": (
            "SMM — это всё, что ты видишь в соцсетях молодёжки. рилсы и короткие видео, тексты, идеи для постов, "
            "дизайн и визуал. команда, которая показывает жизнь церкви онлайн и помогает людям узнать о нас ещё до первого визита.\n\n"
            "если тебе близки соцсети, съёмка рилсов, написание текстов, дизайн или просто есть идеи, которые хочется реализовать — "
            "присоединяйся к SMM-команде."
        ),
        "image": "smm.jpg",
        "has_apply": True,
    },
    {
        "title": "Евангелизация",
        "text": (
            "евангелизация — это выход за стены церкви. мы выходим на улицы города и рассказываем о Боге через творчество, "
            "общение и живые проекты. музыка, перфомансы, диалоги — всё, чтобы делиться Евангелием простым и понятным языком.\n\n"
            "если тебе важно, чтобы люди узнавали о Боге, и ты готов выходить к людям и быть светом там, где ты есть — "
            "присоединяйся к служению евангелизации."
        ),
        "image": "Jesus.jpg",
        "has_apply": True,
    },
]


# =========================
# СТАТИСТИКА
# =========================

def log_event(user, action: str):
    """
    Пишем строку в stats.csv:
    время; id; username; имя; действие
    """
    try:
        with open(file_path("stats.csv"), "a", newline="", encoding="utf-8") as f:
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
# КЛАВИАТУРЫ
# =========================

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

def serve_inline_keyboard(index: int) -> InlineKeyboardMarkup:
    total = len(SERVE_SLIDES)
    prev_i = (index - 1) % total
    next_i = (index + 1) % total

    row_nav = [
        InlineKeyboardButton("◀", callback_data=f"serve:goto:{prev_i}"),
        InlineKeyboardButton(f"{index+1}/{total}", callback_data="serve:noop"),
        InlineKeyboardButton("▶", callback_data=f"serve:goto:{next_i}"),
    ]

    rows = [row_nav]

    # Кнопка заявки на каждом слайде
    if SERVE_SLIDES[index].get("has_apply"):
        rows.append([InlineKeyboardButton("Оставить заявку", url=SERVE_FORM_URL)])

    # Назад (выйти из листалки)
    rows.append([InlineKeyboardButton("Назад", callback_data="serve:exit")])

    return InlineKeyboardMarkup(rows)


# =========================
# ЭКРАН СТАРТА
# =========================

async def send_start_screen(update: Update):
    user = update.message.from_user
    log_event(user, "start_screen")

    await update.message.reply_photo(
        photo=open(file_path("welcome.jpg"), "rb"),
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


# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_event(user, "/start")
    await send_start_screen(update)


# =========================
# ЛИСТАЛКА "ХОЧУ СЛУЖИТЬ"
# =========================

async def send_serve_slide_message(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int):
    """Отправить первое сообщение листалки."""
    user = update.message.from_user
    log_event(user, f"serve_open:{index}")

    slide = SERVE_SLIDES[index]
    caption = f"{slide['title']}\n\n{slide['text']}"

    msg = await update.message.reply_photo(
        photo=open(file_path(slide["image"]), "rb"),
        caption=caption,
        reply_markup=serve_inline_keyboard(index),
    )

    # сохраним, чтобы потом редактировать это сообщение, а не слать новое
    context.user_data["serve_msg_id"] = msg.message_id
    context.user_data["serve_chat_id"] = msg.chat_id
    context.user_data["serve_index"] = index


async def edit_serve_slide_message(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int):
    """Обновить текущее сообщение листалки (без новых сообщений)."""
    query = update.callback_query
    await query.answer()

    chat_id = context.user_data.get("serve_chat_id")
    msg_id = context.user_data.get("serve_msg_id")

    # если по какой-то причине нет сохраненного msg_id — просто отправим заново
    if not chat_id or not msg_id:
        context.user_data["serve_index"] = index
        return

    slide = SERVE_SLIDES[index]
    caption = f"{slide['title']}\n\n{slide['text']}"

    media = InputMediaPhoto(
        media=open(file_path(slide["image"]), "rb"),
        caption=caption,
    )

    await context.bot.edit_message_media(
        chat_id=chat_id,
        message_id=msg_id,
        media=media,
        reply_markup=serve_inline_keyboard(index),
    )

    context.user_data["serve_index"] = index

async def exit_serve_slider(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выйти из листалки: превратим сообщение в обычный экран 'Самое главное'."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    log_event(user, "serve_exit")

    chat_id = context.user_data.get("serve_chat_id")
    msg_id = context.user_data.get("serve_msg_id")

    # Чистим состояние листалки
    context.user_data.pop("serve_chat_id", None)
    context.user_data.pop("serve_msg_id", None)
    context.user_data.pop("serve_index", None)

    intro = (
        "здесь есть всё, что может быть тебе полезным, друг!\n\n"
        "мы всегда открыты для диалога, молитвы и общения."
    )

    if chat_id and msg_id:
        media = InputMediaPhoto(
            media=open(file_path("main.jpg"), "rb"),
            caption=intro,
        )
        await context.bot.edit_message_media(
            chat_id=chat_id,
            message_id=msg_id,
            media=media,
            reply_markup=None,
        )
    # ReplyKeyboard уже остаётся на месте (features_menu_keyboard), если пользователь пришёл оттуда.


async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""

    # serve:goto:{index}
    if data.startswith("serve:goto:"):
        try:
            index = int(data.split(":")[-1])
        except Exception:
            await query.answer()
            return
        await edit_serve_slide_message(update, context, index)
        return

    if data == "serve:exit":
        await exit_serve_slider(update, context)
        return

    if data == "serve:noop":
        await query.answer()
        return


# =========================
# ОСНОВНОЙ ТЕКСТОВЫЙ ХЕНДЛЕР
# =========================

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
        try:
            await update.message.reply_photo(
                photo=open(file_path("time.jpg"), "rb"),
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
                photo=open(file_path("main.jpg"), "rb"),
                caption=intro,
                reply_markup=features_menu_keyboard(),
            )
        except Exception:
            await update.message.reply_text(intro, reply_markup=features_menu_keyboard())
        return

    # --- ХОЧУ СЛУЖИТЬ (ЛИСТАЛКА) ---
    if text == "Хочу служить":
        log_event(user, "Хочу служить (slider)")
        await send_serve_slide_message(update, context, index=0)
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
                photo=open(file_path("homegroup.jpg"), "rb"),
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
                photo=open(file_path("feedback.jpg"), "rb"),
                caption=caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
            )
        except Exception:
            await update.message.reply_text(
                caption, parse_mode="HTML", reply_markup=features_menu_keyboard()
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
                photo=open(file_path("prays.jpg"), "rb"),
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


# =========================
# ЗАПУСК
# =========================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен. Нажми Ctrl+C, чтобы остановить.")
    app.run_polling()

if __name__ == "__main__":
    main()
