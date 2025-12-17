from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
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

TOKEN = os.getenv("TOKEN")

# ========= ЛОГ СТАТИСТИКИ =========

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


# ========= INLINE КЛАВИАТУРЫ (НЕ НИЖНИЕ) =========

def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Расписание", callback_data="main_schedule")],
        [InlineKeyboardButton("Самое главное", callback_data="main_features")],
        [InlineKeyboardButton("Кто мы?", callback_data="main_whowe")],
    ])

def kb_features() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Хочу служить", callback_data="feat_volunteer")],
        [InlineKeyboardButton("Задать вопрос / предложение", callback_data="feat_feedback")],
        [InlineKeyboardButton("Найти домашку", callback_data="feat_homegroup")],
        [InlineKeyboardButton("Молитвенная поддержка", callback_data="feat_prays")],
        [InlineKeyboardButton("Назад", callback_data="back_main")],
    ])

def kb_back_to_features() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Назад", callback_data="back_features")]
    ])

def kb_back_to_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Назад", callback_data="back_main")]
    ])


# ========= ЭКРАНЫ =========

async def show_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_event(user, "start_screen")

    text = (
        'привет! давай знакомиться?\n\n'
        '• это бот молодежного служения Церковь "Жатвы", г. Курган.\n'
        'если хочешь узнать о нас больше — заходи в тг-канал:\n'
        '<a href="https://t.me/HarvestYouth">HarvestYouth</a>\n\n'
        '• каждое воскресенье в 14:30 я жду тебя по адресу:\n'
        '<a href="https://yandex.ru/maps/-/CLseE4oL">Курган, ул. Техническая, д. 8</a>\n\n'
        '• если ты пришел на молодежку первый раз — обязательно напиши:\n'
        '@romanmurash, будем на связи'
    )

    # нижних кнопок не будет — только inline под сообщением
    await update.message.reply_photo(
        photo=open("welcome.jpg", "rb"),
        caption=text,
        parse_mode="HTML",
        reply_markup=kb_main(),
    )


async def show_schedule(query):
    user = query.from_user
    log_event(user, "Расписание")

    caption = (
        "актуальное расписание всегда появляется в нашем Telegram-канале:\n"
        '<a href="https://t.me/HarvestYouth">перейти в канал</a>\n\n'
        "каждый понедельник в нём выходит свежая инфа на всю неделю!"
    )

    try:
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=open("time.jpg", "rb"),
                caption=caption,
                parse_mode="HTML",
            ),
            reply_markup=kb_back_to_main(),
        )
    except Exception:
        # если не получилось отредачить медиа — просто отправим новое
        await query.message.reply_photo(
            photo=open("time.jpg", "rb"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=kb_back_to_main(),
        )


async def show_whowe(query):
    user = query.from_user
    log_event(user, "Кто мы?")

    caption = (
        "хочешь узнать кто мы?\n"
        "читай в этом посте:\n"
        '<a href="https://t.me/HarvestYouth/890">о нас</a>'
    )

    try:
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=open("whowe.jpg", "rb"),
                caption=caption,
                parse_mode="HTML",
            ),
            reply_markup=kb_back_to_main(),
        )
    except Exception:
        await query.message.reply_photo(
            photo=open("whowe.jpg", "rb"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=kb_back_to_main(),
        )


async def show_features_menu(query):
    user = query.from_user
    log_event(user, "Самое главное")

    caption = (
        "здесь есть всё, что может быть тебе полезным, друг!\n\n"
        "мы всегда открыты для диалога, молитвы и общения."
    )

    try:
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=open("main.jpg", "rb"),
                caption=caption,
            ),
            reply_markup=kb_features(),
        )
    except Exception:
        await query.message.reply_photo(
            photo=open("main.jpg", "rb"),
            caption=caption,
            reply_markup=kb_features(),
        )


# ========= ЭКРАНЫ БЛОКОВ ВНУТРИ "САМОЕ ГЛАВНОЕ" =========
# Требование: при входе в блок — убрать все остальные кнопки и оставить только "Назад"

async def show_feature_card(query, key: str):
    user = query.from_user
    log_event(user, f"feature:{key}")

    if key == "volunteer":
        photo = "volonter.jpg"
        caption = (
            "хочешь помогать в церкви? это очень круто!\n"
            "каждое служение — это шанс расти, найти своё призвание и делать что-то значимое для других.\n\n"
            "заполняй заявку по ссылке ниже и мы с радостью свяжемся с тобой!\n"
            '<a href="https://forms.yandex.ru/u/68e0b0bb50569060a96e8d2c">хочу служить!</a>'
        )
    elif key == "homegroup":
        photo = "homegroup.jpg"
        caption = (
            "домашняя группа — это место, где можно поговорить по-честному, "
            "разобраться в Библии, задать любые вопросы и найти своих людей. "
            "тут поддержат, помолятся и помогут расти в вере не в одиночку!\n\n"
            '<a href="https://forms.yandex.ru/u/6938307f1f1eb5cddcef1b93">найти домашку</a>'
        )
    elif key == "feedback":
        photo = "feedback.jpg"
        caption = (
            "у нас к тебе три вопроса:\n"
            "1. ты нашел ошибку в постах?\n"
            "2. у тебя есть крутое предложение?\n"
            "3. хочешь нас поругать или похвалить?\n\n"
            "пиши про это в форме ниже!\n"
            '<a href="https://forms.yandex.ru/u/693838eb49af47b74be7c00e">написать сообщение!</a>'
        )
    elif key == "prays":
        photo = "prays.jpg"
        caption = (
            "молитвенная поддержка – это Божья атмосфера помощи и единства, "
            "которая способна изменить твою жизнь и все обстоятельства вокруг.\n\n"
            "отправь свою просьбу анонимно по ссылке ниже, наша команда за всё помолится!\n\n"
            '<a href="https://forms.yandex.ru/u/68446f8c505690a7125513ca">отправить молитвенную нужду!</a>'
        )
    else:
        photo = "main.jpg"
        caption = "раздел не найден"

    try:
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=open(photo, "rb"),
                caption=caption,
                parse_mode="HTML",
            ),
            reply_markup=kb_back_to_features(),  # только Назад
        )
    except Exception:
        await query.message.reply_photo(
            photo=open(photo, "rb"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=kb_back_to_features(),
        )


# ========= ХЕНДЛЕРЫ =========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_event(user, "/start")
    await show_start(update, context)


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back_main":
        # возвращаем главный экран (редактируем текущее сообщение)
        user = query.from_user
        log_event(user, "back_main")

        text = (
            'привет! давай знакомиться?\n\n'
            '• это бот молодежного служения Церковь "Жатвы", г. Курган.\n'
            'если хочешь узнать о нас больше — заходи в тг-канал:\n'
            '<a href="https://t.me/HarvestYouth">HarvestYouth</a>\n\n'
            '• каждое воскресенье в 14:30 я жду тебя по адресу:\n'
            '<a href="https://yandex.ru/maps/-/CLseE4oL">Курган, ул. Техническая, д. 8</a>\n\n'
            '• если ты пришел на молодежку первый раз — обязательно напиши:\n'
            '@romanmurash, будем на связи'
        )
        try:
            await query.message.edit_media(
                media=InputMediaPhoto(
                    media=open("welcome.jpg", "rb"),
                    caption=text,
                    parse_mode="HTML",
                ),
                reply_markup=kb_main(),
            )
        except Exception:
            await query.message.reply_photo(
                photo=open("welcome.jpg", "rb"),
                caption=text,
                parse_mode="HTML",
                reply_markup=kb_main(),
            )
        return

    if data == "back_features":
        await show_features_menu(query)
        return

    if data == "main_schedule":
        await show_schedule(query)
        return

    if data == "main_whowe":
        await show_whowe(query)
        return

    if data == "main_features":
        await show_features_menu(query)
        return

    if data == "feat_volunteer":
        await show_feature_card(query, "volunteer")
        return

    if data == "feat_homegroup":
        await show_feature_card(query, "homegroup")
        return

    if data == "feat_feedback":
        await show_feature_card(query, "feedback")
        return

    if data == "feat_prays":
        await show_feature_card(query, "prays")
        return


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_callback))

    print("Бот запущен. Нажми Ctrl+C, чтобы остановить.")
    app.run_polling()


if __name__ == "__main__":
    main()
