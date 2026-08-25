interface Env {
  BOT_TOKEN: string;
  WEBHOOK_SECRET: string;
  ASSET_BASE_URL: string;
  DB: D1Database;
}

interface TelegramUser {
  id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
}

interface TelegramMessage {
  message_id: number;
  chat: { id: number };
  from?: TelegramUser;
  text?: string;
}

interface CallbackQuery {
  id: string;
  from: TelegramUser;
  data?: string;
  message?: TelegramMessage;
}

interface TelegramUpdate {
  message?: TelegramMessage;
  callback_query?: CallbackQuery;
}

type Button = {
  text: string;
  callback_data?: string;
  url?: string;
};

type Keyboard = {
  inline_keyboard: Button[][];
};

type ApiResult = {
  ok: boolean;
  description?: string;
  result?: unknown;
};

const APPLY_URL = "https://forms.yandex.ru/u/68e0b0bb50569060a96e8d2c";

const SERVE_SLIDES = [
  {
    image: "team.jpg",
    text:
      "здесь ты найдешь все команды и служения, которые делают одно большое дело, " +
      "перелистывай через кнопки снизу, чтобы посмотреть их все\n\n" +
      "если ты хочешь служить вместе с нами, выбери команду, которая запала в сердце, " +
      "нажми на кнопку «Оставить заявку», и мы свяжемся с тобой!",
  },
  {
    image: "media.jpg",
    text:
      "продакшн — это всё, что происходит за кадром: прямые трансляции, камеры, свет, " +
      "экраны и видео для богослужений. команда, которая делает служение живым, чётким и современным\n\n" +
      "если тебе близки камеры, съёмка, свет или видео — тебе в продакшн",
  },
  {
    image: "praise.jpg",
    text:
      "команда прославления — это поклонение Богу через музыку\n\n" +
      "если ты играешь, поёшь или хочешь развивать музыкальный дар для Бога — присоединяйся!",
  },
  {
    image: "poryadok.jpg",
    text:
      "команда порядка создаёт комфорт на служении: встречают людей, помогают, следят за порядком\n\n" +
      "если тебе близко служение делом — добро пожаловать",
  },
  {
    image: "eda.jpg",
    text:
      "хозяюшки — служение заботы и тепла. готовка, общение, атмосфера дома\n\n" +
      "если любишь заботиться о людях — тебе сюда!",
  },
  {
    image: "smm.jpg",
    text:
      "SMM — это всё, что ты видишь в соцсетях молодёжки\n\n" +
      "если тебе близки рилсы, тексты, дизайн или идеи — давай к нам!",
  },
  {
    image: "Jesus.jpg",
    text:
      "евангелизация — это выход за стены церкви\n\n" +
      "если тебе важно делиться Евангелием с людьми — присоединяйся!",
  },
] as const;

const WELCOME_TEXT =
  'привет, давай знакомиться!\n\n' +
  '• это бот молодежного служения Церковь "Жатвы", г. Курган.\n' +
  'если хочешь узнать о нас больше — заходи в тг-канал:\n' +
  '<a href="https://t.me/HarvestYouth">HarvestYouth</a>\n\n' +
  '• каждое воскресенье в 14:30 я жду тебя по адресу:\n' +
  '<a href="https://yandex.ru/maps/-/CLseE4oL">Курган, ул. Техническая, д. 8</a>\n\n' +
  '• если ты пришел на молодежку первый раз — обязательно напиши:\n' +
  '@romanmurash, будем на связи';

const FEATURES_TEXT =
  "здесь есть всё, что может быть тебе полезным, друг!\n\n" +
  "мы всегда открыты для диалога, молитвы и общения";

const kbMain = (): Keyboard => ({
  inline_keyboard: [
    [{ text: "Расписание", callback_data: "menu_schedule" }],
    [{ text: "Самое главное", callback_data: "menu_features" }],
    [{ text: "Кто мы?", callback_data: "menu_whowe" }],
  ],
});

const kbBackMain = (): Keyboard => ({
  inline_keyboard: [[{ text: "Назад", callback_data: "back_main" }]],
});

const kbFeatures = (): Keyboard => ({
  inline_keyboard: [
    [{ text: "Хочу служить", callback_data: "feat_serve" }],
    [{ text: "Задать вопрос / предложение", callback_data: "feat_feedback" }],
    [{ text: "Найти домашку", callback_data: "feat_homegroup" }],
    [{ text: "Молитвенная поддержка", callback_data: "feat_prays" }],
    [{ text: "Пожертвование", callback_data: "feat_finance" }],
    [{ text: "Назад", callback_data: "back_main" }],
  ],
});

const kbBackFeatures = (): Keyboard => ({
  inline_keyboard: [[{ text: "Назад", callback_data: "back_features" }]],
});

const kbFinance = (): Keyboard => ({
  inline_keyboard: [
    [
      {
        text: "Пожертвовать",
        url: "https://qr.nspk.ru/AS1A005HCS949R4298Q9Q6UM6NJREQK6?type=01&bank=100000000008&crc=8435",
      },
    ],
    [{ text: "Назад", callback_data: "back_features" }],
  ],
});

const kbServe = (index: number): Keyboard => {
  const total = SERVE_SLIDES.length;
  const previous = (index - 1 + total) % total;
  const next = (index + 1) % total;

  return {
    inline_keyboard: [
      [
        { text: "◀", callback_data: `srv_show_${previous}` },
        { text: `${index + 1}/${total}`, callback_data: "noop" },
        { text: "▶", callback_data: `srv_show_${next}` },
      ],
      [{ text: "Оставить заявку", url: APPLY_URL }],
      [{ text: "Назад", callback_data: "back_features" }],
    ],
  };
};

function imageUrl(env: Env, image: string): string {
  return `${env.ASSET_BASE_URL.replace(/\/$/, "")}/${encodeURIComponent(image)}`;
}

async function telegram(
  env: Env,
  method: string,
  payload: Record<string, unknown>,
): Promise<unknown> {
  const response = await fetch(
    `https://api.telegram.org/bot${env.BOT_TOKEN}/${method}`,
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
  const result = (await response.json()) as ApiResult;
  if (!response.ok || !result.ok) {
    throw new Error(`Telegram ${method}: ${result.description ?? response.status}`);
  }
  return result.result;
}

async function logEvent(env: Env, user: TelegramUser, action: string): Promise<void> {
  const fullName = [user.first_name ?? "", user.last_name ?? ""]
    .filter(Boolean)
    .join(" ");

  await env.DB.prepare(
    "INSERT INTO events (created_at, user_id, username, full_name, action) VALUES (?, ?, ?, ?, ?)",
  )
    .bind(new Date().toISOString(), user.id, user.username ?? "", fullName, action)
    .run();
}

async function sendText(
  env: Env,
  chatId: number,
  text: string,
  keyboard?: Keyboard,
): Promise<void> {
  await telegram(env, "sendMessage", {
    chat_id: chatId,
    text,
    parse_mode: "HTML",
    disable_web_page_preview: true,
    ...(keyboard ? { reply_markup: keyboard } : {}),
  });
}

async function sendPhoto(
  env: Env,
  chatId: number,
  image: string,
  caption: string,
  keyboard: Keyboard,
): Promise<void> {
  try {
    await telegram(env, "sendPhoto", {
      chat_id: chatId,
      photo: imageUrl(env, image),
      caption,
      parse_mode: "HTML",
      reply_markup: keyboard,
    });
  } catch (error) {
    console.error("sendPhoto failed, using text fallback", error);
    await sendText(env, chatId, caption, keyboard);
  }
}

async function editPhoto(
  env: Env,
  message: TelegramMessage,
  image: string,
  caption: string,
  keyboard: Keyboard,
): Promise<void> {
  try {
    await telegram(env, "editMessageMedia", {
      chat_id: message.chat.id,
      message_id: message.message_id,
      media: {
        type: "photo",
        media: imageUrl(env, image),
        caption,
        parse_mode: "HTML",
      },
      reply_markup: keyboard,
    });
  } catch (error) {
    console.error("editMessageMedia failed, sending a new message", error);
    await sendPhoto(env, message.chat.id, image, caption, keyboard);
  }
}

async function answerCallback(env: Env, callbackId: string): Promise<void> {
  try {
    await telegram(env, "answerCallbackQuery", {
      callback_query_id: callbackId,
      cache_time: 1,
    });
  } catch (error) {
    console.error("answerCallbackQuery failed", error);
  }
}

async function handleStart(
  env: Env,
  message: TelegramMessage,
  ctx: ExecutionContext,
): Promise<void> {
  if (message.from) {
    ctx.waitUntil(logEvent(env, message.from, "/start"));
  }
  await sendPhoto(env, message.chat.id, "welcome.jpg", WELCOME_TEXT, kbMain());
}

async function handleCallback(
  env: Env,
  query: CallbackQuery,
  ctx: ExecutionContext,
): Promise<void> {
  const data = query.data ?? "";
  await answerCallback(env, query.id);

  if (data === "noop" || !query.message) return;
  const message = query.message;

  if (data === "back_main") {
    await editPhoto(env, message, "welcome.jpg", WELCOME_TEXT, kbMain());
    return;
  }

  if (data === "menu_whowe") {
    await editPhoto(
      env,
      message,
      "whowe.jpg",
      'мы подготовили для тебя пост, где ты сможешь узнать о том, кто мы такие\n<a href="https://t.me/HarvestYouth/890">о нас</a>',
      kbBackMain(),
    );
    return;
  }

  if (data === "menu_schedule") {
    await editPhoto(
      env,
      message,
      "time.jpg",
      'актуальное расписание на неделю всегда появляется в нашем Telegram-канале в понедельник:\n<a href="https://t.me/HarvestYouth">перейти в канал</a>',
      kbBackMain(),
    );
    return;
  }

  if (data === "menu_features" || data === "back_features") {
    await editPhoto(env, message, "main.jpg", FEATURES_TEXT, kbFeatures());
    return;
  }

  if (data === "feat_serve") {
    ctx.waitUntil(logEvent(env, query.from, "Хочу служить"));
    const slide = SERVE_SLIDES[0];
    await editPhoto(env, message, slide.image, slide.text, kbServe(0));
    return;
  }

  if (data === "srv_prev" || data === "srv_next") {
    const index = data === "srv_prev" ? SERVE_SLIDES.length - 1 : 1;
    const slide = SERVE_SLIDES[index];
    await editPhoto(env, message, slide.image, slide.text, kbServe(index));
    return;
  }

  const slideMatch = /^srv_show_(\d+)$/.exec(data);
  if (slideMatch) {
    const index = Number(slideMatch[1]);
    if (Number.isInteger(index) && index >= 0 && index < SERVE_SLIDES.length) {
      const slide = SERVE_SLIDES[index];
      await editPhoto(env, message, slide.image, slide.text, kbServe(index));
    }
    return;
  }

  if (data === "feat_feedback") {
    await editPhoto(
      env,
      message,
      "feedback.jpg",
      "у нас к тебе три вопроса:\n1. ты нашел ошибку в постах?\n2. у тебя есть крутое предложение?\n3. хочешь нас поругать или похвалить?\n\n" +
        '<a href="https://forms.yandex.ru/u/693838eb49af47b74be7c00e">написать сообщение!</a>',
      kbBackFeatures(),
    );
    return;
  }

  if (data === "feat_homegroup") {
    await editPhoto(
      env,
      message,
      "homegroup.jpg",
      "домашняя группа — это место, где можно поговорить по-честному, разобраться в Библии и найти своих людей!\n\n" +
        '<a href="https://forms.yandex.ru/u/6938307f1f1eb5cddcef1b93">найти домашку</a>',
      kbBackFeatures(),
    );
    return;
  }

  if (data === "feat_prays") {
    await editPhoto(
      env,
      message,
      "prays.jpg",
      "молитвенная поддержка — это Божья атмосфера помощи и единства!\n\n" +
        '<a href="https://forms.yandex.ru/u/68446f8c505690a7125513ca">отправить молитвенную нужду!</a>',
      kbBackFeatures(),
    );
    return;
  }

  if (data === "feat_finance") {
    await editPhoto(
      env,
      message,
      "finance.jpg",
      "Бог доверил тебе многое: не только финансы, но и время, способности, силы.\n" +
        "всё это — ресурсы, через которые можно служить людям, делать добро и быть частью Божьего дела.\n" +
        "щедрость — это не про обязанность, а про сердце, готовое откликаться!\n\n" +
        "<blockquote>«Не собирайте себе сокровищ на земле, где моль и ржа истребляют и где воры подкапывают и крадут; " +
        "но собирайте себе сокровища на небе, где ни моль, ни ржа не истребляют и где воры не подкапывают и не крадут»\n" +
        "(Евангелие от Матфея 6:19–20)</blockquote>\n\n" +
        "давайте вместе вкладываться в то, что имеет вечную ценность — в основание, которое не исчезнет и не сгорит\n" +
        "спасибо за твои пожертвования!",
      kbFinance(),
    );
  }
}

async function handleUpdate(
  env: Env,
  update: TelegramUpdate,
  ctx: ExecutionContext,
): Promise<void> {
  if (update.callback_query) {
    await handleCallback(env, update.callback_query, ctx);
    return;
  }

  const message = update.message;
  if (!message) return;

  if (message.text === "/start" || message.text?.startsWith("/start@")) {
    await handleStart(env, message, ctx);
    return;
  }

  if (message.text && !message.text.startsWith("/")) {
    await sendText(env, message.chat.id, "Используй кнопки меню 🙂");
  }
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/") {
      return Response.json({ ok: true, service: "HarvestYouth Telegram bot" });
    }

    if (request.method !== "POST" || url.pathname !== "/webhook") {
      return new Response("Not found", { status: 404 });
    }

    const secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token");
    if (!env.WEBHOOK_SECRET || secret !== env.WEBHOOK_SECRET) {
      return new Response("Unauthorized", { status: 401 });
    }

    try {
      const update = (await request.json()) as TelegramUpdate;
      await handleUpdate(env, update, ctx);
      return Response.json({ ok: true });
    } catch (error) {
      console.error("Unhandled webhook error", error);
      return Response.json({ ok: false }, { status: 500 });
    }
  },
} satisfies ExportedHandler<Env>;
