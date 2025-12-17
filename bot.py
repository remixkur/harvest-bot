from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
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
from pathlib import Path


# ====== НАСТРОЙКИ ======
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN env var is not set")

# Папка, где лежит bot.py и все картинки
BASE_DIR = Path(__file__).resolve().parent
STATS_FILE = BASE_DIR / "stats.csv"

# Ссылка на заявку (одна на всех)
APPLY_URL = "https://forms.yandex.ru/u/68e0b0bb50569060a96e8d2c"


# ====== СЛАЙДЫ СЛУЖЕНИЙ (первый — вступление) ======
MINISTRIES = [
    {
        "title": "Хочу служить",
        "text": (
            "здесь ты найдешь все команды и служения, которые делают одно большое дело.\n"
            "перелистывай через кнопки снизу, чтобы посмотреть их все.\n\n"
            "если ты хочешь служить вместе с нами, выбери команду, которая запала в сердце,\n"
            "нажми на кнопку «Оставить заявку», и мы свяжемся с тобой"
        ),
        "image": "team.jpg",
    },
    {
        "title": "Продакшн",
        "text": (
            "продакшн — это всё, что происходит за кадром.\n"
            "прямые трансляции, камеры, свет, экраны и видео для богослужений.\n"
            "команда, которая делает служение живым, чётким и современным.\n\n"
            "Если тебе близки камеры, съёмка, свет, экраны\n"
            "или ты хочешь научиться работать с техникой и видео —\n"
            "тебе в продакшн."
        ),
        "image": "media.jpg",
    },
    {
        "title": "Прославление",
        "text": (
            "команда прославления — это про поклонение Богу через музыку.\n"
            "Музыканты и вокалисты, которые ведут церковь в поклонении и создают атмосферу, где Бог в центре.\n\n"
            "Если ты играешь на инструменте, поёшь\n"
            "или хочешь развивать свой музыкальный дар для Бога —\n"
            "присоединяйся к команде прославления."
        ),
        "image": "praise.jpg",
    },
    {
        "title": "Команда порядка",
        "text": (
            "команда порядка — это те, кто создают комфорт на служении.\n"
            "Они встречают людей у входа, помогают сориентироваться, следят за порядком в зале, гардеробом и подготовкой пространства.\n"
            "Именно через них люди чувствуют заботу и внимание с первых минут.\n\n"
            "если тебе откликается встречать людей, помогать и служить делом —\n"
            "добро пожаловать в команду порядка."
        ),
        "image": "poryadok.jpg",
    },
    {
        "title": "Хозяюшки",
        "text": (
            "хозяюшки — это служение заботы и тепла.\n"
            "ребята, которые готовят еду к молодёжке и создают атмосферу дома, где хочется остаться, пообщаться и быть своим.\n"
            "Через простые вещи они показывают любовь и внимание к каждому.\n\n"
            "Если тебе нравится готовить, заботиться о людях\n"
            "и служить через практичные дела —\n"
            "тебе в служение хозяюшек."
        ),
        "image": "eda.jpg",
    },
    {
        "title": "SMM",
        "text": (
            "SMM — это всё, что ты видишь в соцсетях молодёжки.\n"
            "Рилсы и короткие видео, тексты, идеи для постов, дизайн и визуал.\n"
            "Команда, которая показывает жизнь церкви онлайн и помогает людям узнать о нас ещё до первого визита.\n\n"
            "Если тебе близки соцсети, съёмка рилсов, написание текстов, дизайн\n"
            "или просто есть идеи, которые хочется реализовать —\n"
            "присоединяйся к SMM-команде."
        ),
        "image": "smm.jpg",
    },
    {
        "title": "Евангелизация",
        "text": (
            "Евангелизация — это выход за стены церкви.\n"
            "Мы выходим на улицы города и рассказываем о Боге через творчество, общение и живые проекты.\n"
            "Музыка, перфомансы, диалоги — всё, чтобы делиться Евангелием простым и понятным языком.\n\n"
            "Если тебе важно, чтобы люди узнавали о Боге\n"
            "и ты готов выходить к людям и быть светом там, где ты есть —\n"
            "присоединяйся к служению евангелизации."
        ),
        "image": "Jesus.jpg",
    },
]


# ====== ЛОГ СТАТИСТИКИ ======
def log_event(user, action: str):
    try:
        with open(STATS_FILE, "a", newline="", encoding="utf-8") as f:
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


# ====== КЛАВИАТУРЫ ======
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


# ====== ВСПОМОГАТЕЛЬНОЕ: безопасно открыть картинку ======
def img_path(filename: str) -> Path:
    return BASE_DIR / filename


# ====== СТАРТОВЫЙ ЭКРАН ======
async def send_start_screen(update: Update):
    user = update.message.from_user
    log_event(user, "start_screen")

    photo_file = img_path("welcome.jpg")
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

    if photo_file.exists():
        await update.message.reply_photo(
            photo=open(photo_file, "rb"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await update.message.reply_text(
            caption,
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )


# ====== /START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_event(user, "/start")
    await send_start_screen(update)


# ====== ЛИСТАЛКА "ХОЧУ СЛУЖИТЬ" ======
def ministries_inline_kb(index: int) -> InlineKeyboardMarkup:
    left = InlineKeyboardButton("◀", callback_data="min:prev")
    right = InlineKeyboardButton("▶", callback_data="min:next")
    apply = InlineKeyboardButton("Оставить заявку", url=APPLY_URL)
    back = InlineKeyboardButton("Назад", callback_data="min:back")
    # стрелки + заявка + назад
    return InlineKeyboardMarkup([[left, right], [apply], [back]])

async def send_ministry_slide(target, context: ContextTypes.DEFAULT_TYPE, index: int):
    index = max(0, min(index, len(MINISTRIES) - 1))
    context.user_data["ministry_index"] = index

    slide = MINISTRIES[index]
    title = slide["title"]
    text = slide["text"]
    image_file = img_path(slide["image"])

    caption = f"<b>{title}</b>\n\n{text}"
    kb = ministries_inline_kb(index)

    # target = update.message (Message) или query.message (Message)
    if image_file.exists():
        await target.reply_photo(
            photo=open(image_file, "rb"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=kb,
        )
    else:
        await target.reply_text(
            caption,
            parse_mode="HTML",
            reply_markup=kb,
        )

async def ministries_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_event(user, "Хочу служить (open)")
    context.user_data["ministry_index"] = 0
    await send_ministry_slide(update.message, context, 0)

async def ministries_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    action = query.data or ""
    idx = int(context.user_data.get("ministry_index", 0))

    if action == "min:prev":
        idx -= 1
        if idx < 0:
            idx = len(MINISTRIES) - 1
        log_event(user, f"min_prev->{idx}")
        await send_ministry_slide(query.message, context, idx)
        return

    if action == "min:next":
        idx += 1
        if idx >= len(MINISTRIES):
            idx = 0
        log_event(user, f"min_next->{idx}")
        await send_ministry_slide(query.message, context, idx)
        return

    if action == "min:back":
        log_event(user, "min_back_to_menu")
        # вернём меню "Самое главное"
        intro = (
            "здесь есть всё, что может быть тебе полезным, друг!\n\n"
            "мы всегда открыты для диалога, молитвы и общения."
        )
        photo_file = img_path("main.jpg")
        if photo_file.exists():
            await query.message.reply_photo(
                photo=open(photo_file, "rb"),
                caption=intro,
                reply_markup=features_menu_keyboard(),
            )
        else:
            await query.message.reply_text(intro, reply_markup=features_menu_keyboard())
        return


# ====== ОСНОВНОЙ ХЕНДЛЕР ТЕКСТА ======
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
        photo_file = img_path("time.jpg")
        caption = (
            "актуальное расписание всегда появляется в нашем Telegram-канале:\n"
            '<a href="https://t.me/HarvestYouth">перейти в канал</a>\n\n'
            "каждый понедельник в нём выходит свежая инфа на всю неделю!"
        )
        if photo_file.exists():
            await update.message.reply_photo(
                photo=open(photo_file, "rb"),
                caption=caption,
                parse_mode="HTML",
                reply_markup=main_menu_with_back_keyboard(),
            )
        else:
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
        photo_file = img_path("main.jpg")
        if photo_file.exists():
            await update.message.reply_photo(
                photo=open(photo_file, "rb"),
                caption=intro,
                reply_markup=features_menu_keyboard(),
            )
        else:
            await update.message.reply_text(intro, reply_markup=features_menu_keyboard())
        return

    # --- ХОЧУ СЛУЖИТЬ (листалка) ---
    if text == "Хочу служить":
        await ministries_open(update, context)
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
        photo_file = img_path("homegroup.jpg")
        if photo_file.exists():
            await update.message.reply_photo(
                photo=open(photo_file, "rb"),
                caption=caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
            )
        else:
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
        photo_file = img_path("feedback.jpg")
        if photo_file.exists():
            await update.message.reply_photo(
                photo=open(photo_file, "rb"),
                caption=caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
            )
        else:
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
        photo_file = img_path("prays.jpg")
        if photo_file.exists():
            await update.message.reply_photo(
                photo=open(photo_file, "rb"),
                caption=caption,
                parse_mode="HTML",
                reply_markup=features_menu_keyboard(),
            )
        else:
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


# ====== ЗАПУСК ======
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(ministries_callback, pattern=r"^min:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен. Нажми Ctrl+C, чтобы остановить.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
