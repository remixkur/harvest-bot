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
# КНОПКИ / МЕНЮ
# =========================
def kb_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Расписание", callback_data="menu_schedule")],
        [InlineKeyboardButton("Самое главное", callback_data="menu_features")],
        [InlineKeyboardButton("Кто мы?", callback_data="menu_whowe")],
    ])


def kb_back_to_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Назад", callback_data="back_main")]
    ])


def kb_features_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Хочу служить", callback_data="feat_serve"),
            InlineKeyboardButton("Задать вопрос / предложение", callback_data="feat_feedback"),
        ],
        [
            InlineKeyboardButton("Найти домашку", callback_data="feat_homegroup"),
            InlineKeyboardButton("Молитвенная поддержка", callback_data="feat_prays"),
        ],
        [InlineKeyboardButton("Назад", callback_data="back_main")],
    ])


def kb_only_back_to_features() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Назад", callback_data="back_features")]
    ])


# =========================
# ЛИСТАЛКА "ХОЧУ СЛУЖИТЬ"
# =========================
APPLY_URL = "https://forms.yandex.ru/u/68e0b0bb50569060a96e8d2c"

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
            "продакшн — это всё, что происходит за кадром. "
            "прямые трансляции, камеры, свет, экраны и видео для богослужений. "
            "команда, которая делает служение живым, чётким и современным.\n\n"
            "если тебе близки камеры, съёмка, свет, экраны или ты хочешь научиться работать с техникой и видео — тебе в продакшн."
        ),
    },
    {
        "image": "praise.jpg",
        "text": (
            "команда прославления — это про поклонение Богу через музыку. "
            "музыканты и вокалисты, которые ведут церковь в поклонении и создают атмосферу, где Бог в центре.\n\n"
            "если ты играешь на инструменте, поёшь или хочешь развивать свой музыкальный дар для Бога — присоединяйся."
        ),
    },
    {
        "image": "poryadok.jpg",
        "text": (
            "команда порядка — это те, кто создают комфорт на служении. "
            "они встречают людей у входа, помогают сориентироваться, следят за порядком в зале, гардеробом и подготовкой пространства. "
            "именно через них люди чувствуют заботу и внимание с первых минут.\n\n"
            "если тебе откликается встречать людей, помогать и служить делом — добро пожаловать."
        ),
    },
    {
        "image": "eda.jpg",
        "text": (
            "хозяюшки — это служение заботы и тепла. "
            "ребята, которые готовят еду к молодёжке и создают атмосферу дома, где хочется остаться, пообщаться и быть своим. "
            "через простые вещи они показывают любовь и внимание к каждому.\n\n"
            "если тебе нравится готовить, заботиться о людях и служить через практичные дела — тебе в служение хозяюшек."
        ),
    },
    {
        "image": "smm.jpg",
        "text": (
            "SMM — это всё, что ты видишь в соцсетях молодёжки. "
            "рилсы и короткие видео, тексты, идеи для постов, дизайн и визуал. "
            "команда, которая показывает жизнь церкви онлайн и помогает людям узнать о нас ещё до первого визита.\n\n"
            "если тебе близки соцсети, съёмка рилсов, написание текстов, дизайн или просто есть идеи — присоединяйся."
        ),
    },
    {
        "image": "Jesus.jpg",
        "text": (
            "евангелизация — это выход за стены церкви. "
            "мы выходим на улицы города и рассказываем о Боге через творчество, общение и живые проекты. "
            "музыка, перфомансы, диалоги — всё, чтобы делиться Евангелием простым и понятным языком.\n\n"
            "если тебе важно, чтобы люди узнавали о Боге, и ты готов выходить к людям и быть светом там, где ты есть — присоединяйся."
        ),
    },
]


def kb_serve_slider(index: int) -> InlineKeyboardMarkup:
    total = len(SERVE_SLIDES)
    prev_btn = InlineKeyboardButton("◀", callback_data="srv_prev")
    next_btn = InlineKeyboardButton("▶", callback_data="srv_next")
    counter = InlineKeyboardButton(f"{index+1}/{total}", callback_data="noop")
    return InlineKeyboardMarkup([
        [prev_btn, counter, next_btn],
        [InlineKeyboardButton("Оставить заявку", url=APPLY_URL)],
        [InlineKeyboardButton("Назад", callback_data="back_features")],
    ])


# =========================
# УТИЛИТЫ РЕДАКТИРОВАНИЯ ОДНОГО СООБЩЕНИЯ
# =========================
async def edit_to_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    image_path: str,
    caption: str,
    keyboard: InlineKeyboardMarkup,
):
    q = update.callback_query
    await q.answer()

    media = InputMediaPhoto(media=open(image_path, "rb"), caption=caption, parse_mode="HTML")
    try:
        await q.message.edit_media(media=media, reply_markup=keyboard)
    except Exception:
        # если Telegram не даёт редактировать медиа (редко), fallback на edit_caption
        try:
            await q.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=keyboard)
        except Exception as e:
            print("edit_to_photo error:", e)


async def send_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        reply_markup=kb_main_menu(),
    )


# =========================
# CALLBACK HANDLER
# =========================
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = update.effective_user
    data = q.data or ""

    if data == "noop":
        await q.answer()
        return

    # ---- MAIN MENU ----
    if data == "back_main":
        log_event(user, "back_main")
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
        await edit_to_photo(update, context, "welcome.jpg", caption, kb_main_menu())
        return

    if data == "menu_whowe":
        log_event(user, "Кто мы?")
        caption = (
            "хочешь узнать кто мы?\n"
            "читай в этом посте:\n"
            '<a href="https://t.me/HarvestYouth/890">о нас</a>'
        )
        await edit_to_photo(update, context, "whowe.jpg", caption, kb_back_to_main())
        return

    if data == "menu_schedule":
        log_event(user, "Расписание")
        caption = (
            "актуальное расписание всегда появляется в нашем Telegram-канале:\n"
            '<a href="https://t.me/HarvestYouth">перейти в канал</a>\n\n'
            "каждый понедельник в нём выходит свежая инфа на всю неделю!"
        )
        await edit_to_photo(update, context, "time.jpg", caption, kb_back_to_main())
        return

    if data == "menu_features":
        log_event(user, "Самое главное (меню)")
        caption = (
            "здесь есть всё, что может быть тебе полезным, друг!\n\n"
            "мы всегда открыты для диалога, молитвы и общения."
        )
        await edit_to_photo(update, context, "main.jpg", caption, kb_features_menu())
        return

    # ---- FEATURES: OPEN BLOCK (ONLY BACK) ----
    if data == "back_features":
        log_event(user, "back_features")
        caption = (
            "здесь есть всё, что может быть тебе полезным, друг!\n\n"
            "мы всегда открыты для диалога, молитвы и общения."
        )
        await edit_to_photo(update, context, "main.jpg", caption, kb_features_menu())
        return

    if data == "feat_feedback":
        log_event(user, "Задать вопрос / предложение")
        caption = (
            "у нас к тебе три вопроса:\n"
            "1. ты нашел ошибку в постах?\n"
            "2. у тебя есть крутое предложение?\n"
            "3. хочешь нас поругать или похвалить?\n\n"
            "пиши про это в форме ниже!\n"
            '<a href="https://forms.yandex.ru/u/693838eb49af47b74be7c00e">написать сообщение!</a>'
        )
        await edit_to_photo(update, context, "feedback.jpg", caption, kb_only_back_to_features())
        return

    if data == "feat_homegroup":
        log_event(user, "Найти домашку")
        caption = (
            "домашняя группа — это место, где можно поговорить по-честному, "
            "разобраться в Библии, задать любые вопросы и найти своих людей. "
            "тут поддержат, помолятся и помогут расти в вере не в одиночку!\n\n"
            '<a href="https://forms.yandex.ru/u/6938307f1f1eb5cddcef1b93">найти домашку</a>'
        )
        await edit_to_photo(update, context, "homegroup.jpg", caption, kb_only_back_to_features())
        return

    if data == "feat_prays":
        log_event(user, "Молитвенная поддержка")
        caption = (
            "молитвенная поддержка — это Божья атмосфера помощи и единства, "
            "которая способна изменить твою жизнь и обстоятельства вокруг.\n\n"
            "отправь свою просьбу анонимно по ссылке ниже — наша команда за всё помолится!\n\n"
            '<a href="https://forms.yandex.ru/u/68446f8c505690a7125513ca">отправить молитвенную нужду!</a>'
        )
        await edit_to_photo(update, context, "prays.jpg", caption, kb_only_back_to_features())
        return

    # ---- SERVE SLIDER ----
    if data == "feat_serve":
        log_event(user, "Хочу служить (листалка)")
        context.user_data["serve_idx"] = 0
        slide = SERVE_SLIDES[0]
        await edit_to_photo(update, context, slide["image"], slide["text"], kb_serve_slider(0))
        return

    if data in ("srv_prev", "srv_next"):
        idx = int(context.user_data.get("serve_idx", 0))
        total = len(SERVE_SLIDES)

        if data == "srv_prev":
            idx = (idx - 1) % total
        else:
            idx = (idx + 1) % total

        context.user_data["serve_idx"] = idx
        slide = SERVE_SLIDES[idx]
        log_event(user, f"serve_slide_{idx+1}/{total}")
        await edit_to_photo(update, context, slide["image"], slide["text"], kb_serve_slider(idx))
        return

    # ---- UNKNOWN ----
    await q.answer()
    log_event(user, f"unknown_callback:{data}")


# =========================
# ТЕКСТОВЫЙ ФОЛБЭК (если кто-то пишет руками)
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    txt = (update.message.text or "").strip()
    log_event(user, f"text:{txt}")
    await update.message.reply_text("Выбери пункт в меню через /start 🙂")  # просто подсказка


# =========================
# MAIN
# =========================
def main():
    if not TOKEN:
        raise RuntimeError("TOKEN не задан. Добавь переменную окружения TOKEN.")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", send_start))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен.")
    app.run_polling()


if __name__ == "__main__":
    main()
