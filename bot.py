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
    ContextTypes,
)
from datetime import datetime
import csv
import os
from pathlib import Path

# =========================
# НАСТРОЙКИ
# =========================
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN env var is missing. Set TOKEN in environment.")

BASE_DIR = Path(__file__).resolve().parent
STATS_FILE = BASE_DIR / "stats.csv"

def p(name: str) -> Path:
    return BASE_DIR / name

def file_exists(name: str) -> bool:
    return p(name).exists()

SERVE_FORM_URL = "https://forms.yandex.ru/u/68e0b0bb50569060a96e8d2c"

# =========================
# СТАТИСТИКА
# =========================
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

# =========================
# ТЕКСТЫ / ЭКРАНЫ
# =========================

WELCOME_CAPTION = (
    'привет! давай знакомиться?\n\n'
    '• это бот молодежного служения Церковь "Жатвы", г. Курган.\n'
    'если хочешь узнать о нас больше — заходи в тг-канал:\n'
    '<a href="https://t.me/HarvestYouth">HarvestYouth</a>\n\n'
    '• каждое воскресенье в 14:30 я жду тебя по адресу:\n'
    '<a href="https://yandex.ru/maps/-/CLseE4oL">Курган, ул. Техническая, д. 8</a>\n\n'
    '• если ты пришел на молодежку первый раз — обязательно напиши:\n'
    '@romanmurash, будем на связи'
)

ABOUT_CAPTION = (
    "хочешь узнать кто мы?\n"
    "читай в этом посте:\n"
    '<a href="https://t.me/HarvestYouth/890">о нас</a>'
)

SCHEDULE_CAPTION = (
    "актуальное расписание всегда появляется в нашем Telegram-канале:\n"
    '<a href="https://t.me/HarvestYouth">перейти в канал</a>\n\n'
    "каждый понедельник в нём выходит свежая инфа на всю неделю!"
)

MAIN_CAPTION = (
    "здесь есть всё, что может быть тебе полезным, друг!\n\n"
    "мы всегда открыты для диалога, молитвы и общения."
)

HOMEGROUP_CAPTION = (
    "домашняя группа — это место, где можно поговорить по-честному, разобраться в Библии, "
    "задать любые вопросы и найти своих людей. тут поддержат, помолятся и помогут расти в вере не в одиночку!\n\n"
    '<a href="https://forms.yandex.ru/u/6938307f1f1eb5cddcef1b93">найти домашку</a>'
)

FEEDBACK_CAPTION = (
    "у нас к тебе три вопроса:\n"
    "1. ты нашел ошибку в постах?\n"
    "2. у тебя есть крутое предложение?\n"
    "3. хочешь нас поругать или похвалить?\n\n"
    "пиши про это в форме ниже!\n"
    '<a href="https://forms.yandex.ru/u/693838eb49af47b74be7c00e">написать сообщение!</a>'
)

PRAYS_CAPTION = (
    "молитвенная поддержка – это Божья атмосфера помощи и единства, которая способна изменить твою жизнь и все обстоятельства вокруг.\n\n"
    "отправь свою просьбу анонимно по ссылке ниже, наша команда за всё помолится!\n\n"
    '<a href="https://forms.yandex.ru/u/68446f8c505690a7125513ca">отправить молитвенную нужду!</a>'
)

# =========================
# СЛАЙДЫ СЛУЖЕНИЙ (БЕЗ ЗАГОЛОВКОВ В ТЕКСТЕ)
# =========================
SERVE_SLIDES = [
    {
        "image": "team.jpg",
        "text": (
            "здесь ты найдешь все команды и служения, которые делают одно большое дело. "
            "перелистывай через кнопки снизу, чтобы посмотреть их все.\n\n"
            "если ты хочешь служить вместе с нами, выбери команду, которая запала в сердце, "
            "нажми на кнопку «Оставить заявку», и мы свяжемся с тобой"
        ),
    },
    {
        "image": "media.jpg",
        "text": (
            "продакшн — это всё, что происходит за кадром. прямые трансляции, камеры, свет, экраны и видео для богослужений. "
            "команда, которая делает служение живым, чётким и современным.\n\n"
            "если тебе близки камеры, съёмка, свет, экраны или ты хочешь научиться работать с техникой и видео — тебе в продакшн."
        ),
    },
    {
        "image": "praise.jpg",
        "text": (
            "команда прославления — это про поклонение Богу через музыку. музыканты и вокалисты, которые ведут церковь в поклонении "
            "и создают атмосферу, где Бог в центре.\n\n"
            "если ты играешь на инструменте, поёшь или хочешь развивать свой музыкальный дар для Бога — присоединяйся к команде прославления."
        ),
    },
    {
        "image": "poryadok.jpg",
        "text": (
            "команда порядка — это те, кто создают комфорт на служении. они встречают людей у входа, помогают сориентироваться, "
            "следят за порядком в зале, гардеробом и подготовкой пространства. именно через них люди чувствуют заботу и внимание с первых минут.\n\n"
            "если тебе откликается встречать людей, помогать и служить делом — добро пожаловать в команду порядка."
        ),
    },
    {
        "image": "eda.jpg",
        "text": (
            "хозяюшки — это служение заботы и тепла. ребята, которые готовят еду к молодёжке и создают атмосферу дома, где хочется остаться, "
            "пообщаться и быть своим. через простые вещи они показывают любовь и внимание к каждому.\n\n"
            "если тебе нравится готовить, заботиться о людях и служить через практичные дела — тебе в служение хозяюшек."
        ),
    },
    {
        "image": "smm.jpg",
        "text": (
            "SMM — это всё, что ты видишь в соцсетях молодёжки. рилсы и короткие видео, тексты, идеи для постов, дизайн и визуал. "
            "команда, которая показывает жизнь церкви онлайн и помогает людям узнать о нас ещё до первого визита.\n\n"
            "если тебе близки соцсети, съёмка рилсов, написание текстов, дизайн или просто есть идеи, которые хочется реализовать — присоединяйся к SMM-команде."
        ),
    },
    {
        "image": "Jesus.jpg",
        "text": (
            "евангелизация — это выход за стены церкви. мы выходим на улицы города и рассказываем о Боге через творчество, общение и живые проекты. "
            "музыка, перформансы, диалоги — всё, чтобы делиться Евангелием простым и понятным языком.\n\n"
            "если тебе важно, чтобы люди узнавали о Боге, и ты готов выходить к людям и быть светом там, где ты есть — присоединяйся к служению евангелизации."
        ),
    },
]

# =========================
# INLINE-МЕНЮ
# =========================

def kb_home() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Расписание", callback_data="nav:schedule")],
        [InlineKeyboardButton("Самое главное", callback_data="nav:main")],
        [InlineKeyboardButton("Кто мы?", callback_data="nav:about")],
    ])

def kb_home_with_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Назад", callback_data="nav:home")],
    ])

def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Хочу служить", callback_data="feat:serve")],
        [InlineKeyboardButton("Задать вопрос / предложение", callback_data="feat:feedback")],
        [InlineKeyboardButton("Найти домашку", callback_data="feat:homegroup")],
        [InlineKeyboardButton("Молитвенная поддержка", callback_data="feat:prays")],
        [InlineKeyboardButton("Назад", callback_data="nav:home")],
    ])

def kb_serve(index: int) -> InlineKeyboardMarkup:
    total = len(SERVE_SLIDES)
    prev_i = (index - 1) % total
    next_i = (index + 1) % total
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀", callback_data=f"serve:goto:{prev_i}"),
            InlineKeyboardButton(f"{index+1}/{total}", callback_data="noop"),
            InlineKeyboardButton("▶", callback_data=f"serve:goto:{next_i}"),
        ],
        [InlineKeyboardButton("Оставить заявку", url=SERVE_FORM_URL)],
        [InlineKeyboardButton("Назад", callback_data="nav:main")],
    ])

# =========================
# ЕДИНЫЙ РЕНДЕР: ВСЕГДА РЕДАКТИРУЕМ ОДНО СООБЩЕНИЕ
# =========================

async def render(update: Update, context: ContextTypes.DEFAULT_TYPE, *, image: str, caption: str, keyboard: InlineKeyboardMarkup):
    """
    Пытаемся отредактировать одно "главное" сообщение пользователя.
    Если нечего редактировать или редактирование упало — отправим новое и запомним его.
    """
    chat_id = update.effective_chat.id
    msg_id = context.user_data.get("main_msg_id")

    img = p(image) if image else None
    if img and not img.exists():
        # запасной вариант — если нужной картинки нет
        img = p("main.jpg") if file_exists("main.jpg") else None

    try:
        if msg_id and img:
            media = InputMediaPhoto(media=open(img, "rb"), caption=caption, parse_mode="HTML")
            await context.bot.edit_message_media(
                chat_id=chat_id,
                message_id=msg_id,
                media=media,
                reply_markup=keyboard,
            )
            return
        elif msg_id and not img:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=caption,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
            return
    except Exception as e:
        # если не получилось — пошлём новое (и дальше снова будем редачить уже его)
        print("render edit failed:", e)

    # fallback: send new
    if img:
        msg = await context.bot.send_photo(
            chat_id=chat_id,
            photo=open(img, "rb"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    else:
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=caption,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    context.user_data["main_msg_id"] = msg.message_id

# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_event(user, "/start")
    await render(
        update, context,
        image="welcome.jpg",
        caption=WELCOME_CAPTION,
        keyboard=kb_home(),
    )

# =========================
# CALLBACKS
# =========================

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data or ""

    if data == "noop":
        return

    # -------- NAV --------
    if data == "nav:home":
        log_event(user, "nav:home")
        await render(update, context, image="welcome.jpg", caption=WELCOME_CAPTION, keyboard=kb_home())
        return

    if data == "nav:about":
        log_event(user, "nav:about")
        # используем main.jpg как фон, чтобы всегда редактировать медиа
        await render(update, context, image="main.jpg", caption=ABOUT_CAPTION, keyboard=kb_home_with_back())
        return

    if data == "nav:schedule":
        log_event(user, "nav:schedule")
        await render(update, context, image="time.jpg", caption=SCHEDULE_CAPTION, keyboard=kb_home_with_back())
        return

    if data == "nav:main":
        log_event(user, "nav:main")
        await render(update, context, image="main.jpg", caption=MAIN_CAPTION, keyboard=kb_main())
        return

    # -------- FEATURES --------
    if data == "feat:serve":
        log_event(user, "feat:serve")
        context.user_data["serve_index"] = 0
        slide = SERVE_SLIDES[0]
        await render(update, context, image=slide["image"], caption=slide["text"], keyboard=kb_serve(0))
        return

    if data == "feat:homegroup":
        log_event(user, "feat:homegroup")
        await render(update, context, image="homegroup.jpg", caption=HOMEGROUP_CAPTION, keyboard=kb_main())
        return

    if data == "feat:feedback":
        log_event(user, "feat:feedback")
        await render(update, context, image="feedback.jpg", caption=FEEDBACK_CAPTION, keyboard=kb_main())
        return

    if data == "feat:prays":
        log_event(user, "feat:prays")
        await render(update, context, image="prays.jpg", caption=PRAYS_CAPTION, keyboard=kb_main())
        return

    # -------- SERVE SLIDER --------
    if data.startswith("serve:goto:"):
        try:
            idx = int(data.split(":")[-1])
        except Exception:
            return
        idx = max(0, min(idx, len(SERVE_SLIDES) - 1))
        context.user_data["serve_index"] = idx
        log_event(user, f"serve:goto:{idx}")
        slide = SERVE_SLIDES[idx]
        await render(update, context, image=slide["image"], caption=slide["text"], keyboard=kb_serve(idx))
        return

# =========================
# ЗАПУСК
# =========================

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
