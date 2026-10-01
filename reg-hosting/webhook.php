<?php

declare(strict_types=1);

$configPath = __DIR__ . '/config.php';
if (!is_file($configPath)) {
    http_response_code(503);
    exit('Bot is not configured');
}

/** @var array<string, mixed> $config */
$config = require $configPath;
$requiredConfig = ['user_bot_token', 'admin_bot_token', 'admin_chat_id', 'webhook_secret', 'asset_base_url'];
foreach ($requiredConfig as $key) {
    if (!isset($config[$key]) || $config[$key] === '') {
        http_response_code(503);
        exit('Bot config is incomplete');
    }
}

$storageDir = __DIR__ . '/storage';
if (!is_dir($storageDir)) {
    mkdir($storageDir, 0700, true);
}

$serveSlides = [
    [
        'title' => 'Команды и служения',
        'image' => 'team.jpg',
        'text' => 'здесь ты найдешь все команды и служения, которые делают одно большое дело, перелистывай через кнопки снизу, чтобы посмотреть их все' . "\n\n" . 'если ты хочешь служить вместе с нами, выбери команду, которая запала в сердце, нажми на кнопку «Оставить заявку», и мы свяжемся с тобой!',
    ],
    [
        'title' => 'Продакшн',
        'image' => 'media.jpg',
        'text' => 'продакшн — это всё, что происходит за кадром: прямые трансляции, камеры, свет, экраны и видео для богослужений. команда, которая делает служение живым, чётким и современным' . "\n\n" . 'если тебе близки камеры, съёмка, свет или видео — тебе в продакшн',
    ],
    [
        'title' => 'Команда прославления',
        'image' => 'praise.jpg',
        'text' => 'команда прославления — это поклонение Богу через музыку' . "\n\n" . 'если ты играешь, поёшь или хочешь развивать музыкальный дар для Бога — присоединяйся!',
    ],
    [
        'title' => 'Команда порядка',
        'image' => 'poryadok.jpg',
        'text' => 'команда порядка создаёт комфорт на служении: встречают людей, помогают, следят за порядком' . "\n\n" . 'если тебе близко служение делом — добро пожаловать',
    ],
    [
        'title' => 'Хозяюшки',
        'image' => 'eda.jpg',
        'text' => 'хозяюшки — служение заботы и тепла. готовка, общение, атмосфера дома' . "\n\n" . 'если любишь заботиться о людях — тебе сюда!',
    ],
    [
        'title' => 'SMM',
        'image' => 'smm.jpg',
        'text' => 'SMM — это всё, что ты видишь в соцсетях молодёжки' . "\n\n" . 'если тебе близки рилсы, тексты, дизайн или идеи — давай к нам!',
    ],
    [
        'title' => 'Евангелизация',
        'image' => 'Jesus.jpg',
        'text' => 'евангелизация — это выход за стены церкви' . "\n\n" . 'если тебе важно делиться Евангелием с людьми — присоединяйся!',
    ],
];

$welcomeText = 'привет, давай знакомиться!' . "\n\n"
    . '• это бот молодежного служения Церковь "Жатвы", г. Курган.' . "\n"
    . 'если хочешь узнать о нас больше — заходи в тг-канал:' . "\n"
    . '<a href="https://t.me/HarvestYouth">HarvestYouth</a>' . "\n\n"
    . '• каждое воскресенье в 14:30 я жду тебя по адресу:' . "\n"
    . '<a href="https://yandex.ru/maps/-/CLseE4oL">Курган, ул. Техническая, д. 8</a>' . "\n\n"
    . '• если ты пришел на молодежку первый раз — обязательно напиши:' . "\n"
    . '@romanmurash, будем на связи';

$featuresText = 'здесь есть всё, что может быть тебе полезным, друг!' . "\n\n"
    . 'мы всегда открыты для диалога, молитвы и общения';

function jsonResponse(array $body, int $status = 200): never
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($body, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function telegramApi(string $token, string $method, array $payload): array
{
    $curl = curl_init('https://api.telegram.org/bot' . $token . '/' . $method);
    curl_setopt_array($curl, [
        CURLOPT_POST => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_TIMEOUT => 25,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_POSTFIELDS => json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES),
    ]);
    $raw = curl_exec($curl);
    $status = (int) curl_getinfo($curl, CURLINFO_RESPONSE_CODE);
    $error = curl_error($curl);
    curl_close($curl);

    if ($raw === false || $status >= 400) {
        throw new RuntimeException($method . ' failed: ' . ($error ?: (string) $raw));
    }

    $result = json_decode((string) $raw, true);
    if (!is_array($result) || !($result['ok'] ?? false)) {
        throw new RuntimeException($method . ' failed: ' . ($result['description'] ?? 'unknown error'));
    }
    return $result;
}

function assetUrl(array $config, string $image): string
{
    return rtrim((string) $config['asset_base_url'], '/') . '/' . rawurlencode($image);
}

function mainKeyboard(): array
{
    return ['inline_keyboard' => [
        [['text' => 'Расписание', 'callback_data' => 'menu_schedule']],
        [['text' => 'Самое главное', 'callback_data' => 'menu_features']],
        [['text' => 'Кто мы?', 'callback_data' => 'menu_whowe']],
    ]];
}

function featuresKeyboard(): array
{
    return ['inline_keyboard' => [
        [['text' => 'Хочу служить', 'callback_data' => 'feat_serve']],
        [['text' => 'Задать вопрос / предложение', 'callback_data' => 'feat_feedback']],
        [['text' => 'Найти домашку', 'callback_data' => 'feat_homegroup']],
        [['text' => 'Молитвенная поддержка', 'callback_data' => 'feat_prays']],
        [['text' => 'Пожертвование', 'callback_data' => 'feat_finance']],
        [['text' => 'Назад', 'callback_data' => 'back_main']],
    ]];
}

function backKeyboard(string $callback): array
{
    return ['inline_keyboard' => [[['text' => 'Назад', 'callback_data' => $callback]]]];
}

function cancelKeyboard(): array
{
    return ['inline_keyboard' => [[['text' => 'Отменить', 'callback_data' => 'form_cancel']]]];
}

function contactKeyboard(?string $username, bool $allowSkip): array
{
    $rows = [];
    if ($username !== null && $username !== '') {
        $rows[] = [['text' => 'Использовать @' . $username, 'callback_data' => 'form_use_username']];
    }
    if ($allowSkip) {
        $rows[] = [['text' => 'Отправить без контакта', 'callback_data' => 'form_skip_contact']];
    }
    $rows[] = [['text' => 'Отменить', 'callback_data' => 'form_cancel']];
    return ['inline_keyboard' => $rows];
}

function serveKeyboard(int $index, int $total): array
{
    $previous = ($index - 1 + $total) % $total;
    $next = ($index + 1) % $total;
    return ['inline_keyboard' => [
        [
            ['text' => '◀', 'callback_data' => 'srv_show_' . $previous],
            ['text' => ($index + 1) . '/' . $total, 'callback_data' => 'noop'],
            ['text' => '▶', 'callback_data' => 'srv_show_' . $next],
        ],
        [['text' => 'Оставить заявку', 'callback_data' => 'form_serve_start_' . $index]],
        [['text' => 'Назад', 'callback_data' => 'back_features']],
    ]];
}

function financeKeyboard(): array
{
    return ['inline_keyboard' => [
        [[
            'text' => 'Пожертвовать',
            'url' => 'https://qr.nspk.ru/AS1A005HCS949R4298Q9Q6UM6NJREQK6?type=01&bank=100000000008&crc=8435',
        ]],
        [['text' => 'Назад', 'callback_data' => 'back_features']],
    ]];
}

function sendText(array $config, int|string $chatId, string $text, ?array $keyboard = null): void
{
    $payload = [
        'chat_id' => $chatId,
        'text' => $text,
        'parse_mode' => 'HTML',
        'link_preview_options' => ['is_disabled' => true],
    ];
    if ($keyboard !== null) {
        $payload['reply_markup'] = $keyboard;
    }
    telegramApi((string) $config['user_bot_token'], 'sendMessage', $payload);
}

function sendPhoto(array $config, int|string $chatId, string $image, string $caption, array $keyboard): void
{
    try {
        telegramApi((string) $config['user_bot_token'], 'sendPhoto', [
            'chat_id' => $chatId,
            'photo' => assetUrl($config, $image),
            'caption' => $caption,
            'parse_mode' => 'HTML',
            'reply_markup' => $keyboard,
        ]);
    } catch (Throwable $error) {
        error_log('sendPhoto: ' . $error->getMessage());
        sendText($config, $chatId, $caption, $keyboard);
    }
}

function editPhoto(array $config, array $message, string $image, string $caption, array $keyboard): void
{
    try {
        telegramApi((string) $config['user_bot_token'], 'editMessageMedia', [
            'chat_id' => $message['chat']['id'],
            'message_id' => $message['message_id'],
            'media' => [
                'type' => 'photo',
                'media' => assetUrl($config, $image),
                'caption' => $caption,
                'parse_mode' => 'HTML',
            ],
            'reply_markup' => $keyboard,
        ]);
    } catch (Throwable $error) {
        error_log('editPhoto: ' . $error->getMessage());
        sendPhoto($config, $message['chat']['id'], $image, $caption, $keyboard);
    }
}

function answerCallback(array $config, string $callbackId, ?string $text = null): void
{
    try {
        $payload = ['callback_query_id' => $callbackId, 'cache_time' => 1];
        if ($text !== null) {
            $payload['text'] = $text;
        }
        telegramApi((string) $config['user_bot_token'], 'answerCallbackQuery', $payload);
    } catch (Throwable $error) {
        error_log('answerCallbackQuery: ' . $error->getMessage());
    }
}

function statePath(string $storageDir, int $userId): string
{
    $stateDir = $storageDir . '/states';
    if (!is_dir($stateDir)) {
        mkdir($stateDir, 0700, true);
    }
    return $stateDir . '/' . $userId . '.json';
}

function loadState(string $storageDir, int $userId): ?array
{
    $path = statePath($storageDir, $userId);
    if (!is_file($path)) {
        return null;
    }
    $state = json_decode((string) file_get_contents($path), true);
    return is_array($state) ? $state : null;
}

function saveState(string $storageDir, int $userId, array $state): void
{
    $path = statePath($storageDir, $userId);
    $temporary = $path . '.' . bin2hex(random_bytes(4)) . '.tmp';
    file_put_contents($temporary, json_encode($state, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT), LOCK_EX);
    chmod($temporary, 0600);
    rename($temporary, $path);
}

function clearState(string $storageDir, int $userId): void
{
    $path = statePath($storageDir, $userId);
    if (is_file($path)) {
        unlink($path);
    }
}

function appendJsonLine(string $path, array $record): void
{
    $handle = fopen($path, 'ab');
    if ($handle === false) {
        throw new RuntimeException('Cannot open ' . $path);
    }
    flock($handle, LOCK_EX);
    fwrite($handle, json_encode($record, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n");
    fflush($handle);
    flock($handle, LOCK_UN);
    fclose($handle);
    chmod($path, 0600);
}

function logEvent(string $storageDir, array $user, string $action): void
{
    appendJsonLine($storageDir . '/stats.jsonl', [
        'created_at' => date(DATE_ATOM),
        'user_id' => $user['id'] ?? null,
        'username' => $user['username'] ?? '',
        'name' => trim(($user['first_name'] ?? '') . ' ' . ($user['last_name'] ?? '')),
        'action' => $action,
    ]);
}

function html(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function flowTitle(string $flow): string
{
    return match ($flow) {
        'serve' => '🙌 хочу служить',
        'homegroup' => '🏠 найти домашку',
        'feedback' => '💬 вопрос / предложение',
        'prayer' => '🙏 молитвенная нужда',
        default => 'новая заявка',
    };
}

function submitApplication(array $config, string $storageDir, array $user, array $state): void
{
    $record = [
        'created_at' => date(DATE_ATOM),
        'flow' => $state['flow'],
        'user' => [
            'id' => $user['id'],
            'username' => $user['username'] ?? '',
            'first_name' => $user['first_name'] ?? '',
            'last_name' => $user['last_name'] ?? '',
        ],
        'data' => $state['data'] ?? [],
    ];
    appendJsonLine($storageDir . '/applications.jsonl', $record);

    $data = $record['data'];
    $lines = ['<b>' . flowTitle((string) $state['flow']) . '</b>', ''];
    if (isset($data['service'])) {
        $lines[] = '<b>служение:</b> ' . html((string) $data['service']);
    }
    if (isset($data['name'])) {
        $lines[] = '<b>имя:</b> ' . html((string) $data['name']);
    }
    if (isset($data['age'])) {
        $lines[] = '<b>возраст:</b> ' . html((string) $data['age']);
    }
    if (isset($data['district'])) {
        $lines[] = '<b>район:</b> ' . html((string) $data['district']);
    }
    if (isset($data['message'])) {
        $messageLabel = ($state['flow'] ?? '') === 'prayer' ? 'молитвенная нужда' : 'сообщение';
        $lines[] = '<b>' . $messageLabel . ':</b>' . "\n" . html((string) $data['message']);
    }
    $lines[] = '<b>контакт:</b> ' . html((string) ($data['contact'] ?? 'не указан'));
    $telegramName = isset($user['username']) ? '@' . $user['username'] : 'без username';
    $lines[] = '<b>telegram:</b> <a href="tg://user?id=' . (int) $user['id'] . '">' . html($telegramName) . '</a>';

    $adminChatId = $config['admin_chat_id'];
    $adminBotToken = (string) $config['admin_bot_token'];
    if (!$adminChatId && !empty($config['fallback_admin_chat_id'])) {
        $adminChatId = $config['fallback_admin_chat_id'];
        $adminBotToken = (string) $config['user_bot_token'];
    }

    try {
        telegramApi($adminBotToken, 'sendMessage', [
            'chat_id' => $adminChatId,
            'text' => implode("\n", $lines),
            'parse_mode' => 'HTML',
            'link_preview_options' => ['is_disabled' => true],
        ]);
    } catch (Throwable $error) {
        error_log('Admin notification failed: ' . $error->getMessage());
    }
}

function beginFlow(array $config, string $storageDir, array $user, int|string $chatId, string $flow, array $data = []): void
{
    saveState($storageDir, (int) $user['id'], [
        'flow' => $flow,
        'step' => in_array($flow, ['feedback', 'prayer'], true) ? 'message' : 'name',
        'data' => $data,
        'updated_at' => time(),
    ]);

    $prompt = match ($flow) {
        'feedback' => '<b>вопрос или предложение</b>' . "\n\n" . 'напиши одним сообщением всё, что хочешь передать команде.',
        'prayer' => '<b>молитвенная нужда</b>' . "\n\n" . 'напиши одним сообщением, о чём команда может помолиться.',
        default => '<b>' . flowTitle($flow) . '</b>' . "\n\n" . 'как тебя зовут?',
    };
    sendText($config, $chatId, $prompt, cancelKeyboard());
}

function finishFlow(array $config, string $storageDir, array $user, int|string $chatId, array $state): void
{
    submitApplication($config, $storageDir, $user, $state);
    clearState($storageDir, (int) $user['id']);
    sendText(
        $config,
        $chatId,
        'спасибо! всё записали и передали команде. с тобой свяжутся 🙌',
        featuresKeyboard()
    );
}

function handleFormMessage(array $config, string $storageDir, array $message, array $state): void
{
    $user = $message['from'];
    $chatId = $message['chat']['id'];
    $text = trim((string) ($message['text'] ?? ''));
    if ($text === '' && isset($message['contact']['phone_number'])) {
        $text = (string) $message['contact']['phone_number'];
    }
    if ($text === '') {
        sendText($config, $chatId, 'пожалуйста, отправь ответ текстом или нажми «Отменить».', cancelKeyboard());
        return;
    }

    if ($text === '/cancel') {
        clearState($storageDir, (int) $user['id']);
        sendText($config, $chatId, 'анкета отменена.', featuresKeyboard());
        return;
    }

    $flow = (string) $state['flow'];
    $step = (string) $state['step'];
    $state['data'] ??= [];
    $state['updated_at'] = time();

    if ($step === 'name') {
        $state['data']['name'] = $text;
        $state['step'] = 'age';
        saveState($storageDir, (int) $user['id'], $state);
        sendText($config, $chatId, 'сколько тебе лет?', cancelKeyboard());
        return;
    }

    if ($step === 'age') {
        if (!preg_match('/^\d{1,2}$/', $text) || (int) $text < 7 || (int) $text > 99) {
            sendText($config, $chatId, 'напиши возраст цифрами, например: 19.', cancelKeyboard());
            return;
        }
        $state['data']['age'] = $text;
        if ($flow === 'homegroup') {
            $state['step'] = 'district';
            saveState($storageDir, (int) $user['id'], $state);
            sendText($config, $chatId, 'в каком районе Кургана тебе удобнее посещать домашнюю группу?', cancelKeyboard());
            return;
        }
        $state['step'] = 'contact';
        saveState($storageDir, (int) $user['id'], $state);
        sendText($config, $chatId, 'оставь номер телефона или Telegram username, чтобы мы могли связаться.', contactKeyboard($user['username'] ?? null, false));
        return;
    }

    if ($step === 'district') {
        $state['data']['district'] = $text;
        $state['step'] = 'contact';
        saveState($storageDir, (int) $user['id'], $state);
        sendText($config, $chatId, 'оставь номер телефона или Telegram username, чтобы лидер домашки мог связаться.', contactKeyboard($user['username'] ?? null, false));
        return;
    }

    if ($step === 'message') {
        $state['data']['message'] = $text;
        $state['step'] = 'contact_optional';
        saveState($storageDir, (int) $user['id'], $state);
        $contactPrompt = $flow === 'prayer'
            ? 'если хочешь, оставь контакт, чтобы мы могли поддержать тебя лично. можно отправить нужду без контакта.'
            : 'можешь оставить контакт для ответа или отправить без контакта.';
        sendText($config, $chatId, $contactPrompt, contactKeyboard($user['username'] ?? null, true));
        return;
    }

    if ($step === 'contact' || $step === 'contact_optional') {
        $state['data']['contact'] = $text;
        finishFlow($config, $storageDir, $user, $chatId, $state);
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    jsonResponse(['ok' => true, 'service' => 'HarvestYouth Telegram bot']);
}

$receivedSecret = (string) ($_SERVER['HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN'] ?? '');
if ($receivedSecret === '' || !hash_equals((string) $config['webhook_secret'], $receivedSecret)) {
    jsonResponse(['ok' => false], 401);
}

$update = json_decode((string) file_get_contents('php://input'), true);
if (!is_array($update)) {
    jsonResponse(['ok' => false], 400);
}

try {
    if (isset($update['callback_query'])) {
        $query = $update['callback_query'];
        $data = (string) ($query['data'] ?? '');
        $user = $query['from'];
        $message = $query['message'] ?? null;
        answerCallback($config, (string) $query['id']);

        if ($data === 'noop' || !is_array($message)) {
            jsonResponse(['ok' => true]);
        }

        $chatId = $message['chat']['id'];
        if ($data === 'form_cancel') {
            clearState($storageDir, (int) $user['id']);
            sendText($config, $chatId, 'анкета отменена.', featuresKeyboard());
            jsonResponse(['ok' => true]);
        }

        $state = loadState($storageDir, (int) $user['id']);
        if ($data === 'form_use_username' && is_array($state) && !empty($user['username'])) {
            $state['data']['contact'] = '@' . $user['username'];
            finishFlow($config, $storageDir, $user, $chatId, $state);
            jsonResponse(['ok' => true]);
        }
        if ($data === 'form_skip_contact' && is_array($state) && ($state['step'] ?? '') === 'contact_optional') {
            $state['data']['contact'] = '';
            finishFlow($config, $storageDir, $user, $chatId, $state);
            jsonResponse(['ok' => true]);
        }

        if ($data === 'back_main') {
            editPhoto($config, $message, 'welcome.jpg', $welcomeText, mainKeyboard());
        } elseif ($data === 'menu_whowe') {
            editPhoto($config, $message, 'whowe.jpg', 'мы подготовили для тебя пост, где ты сможешь узнать о том, кто мы такие' . "\n" . '<a href="https://t.me/HarvestYouth/890">о нас</a>', backKeyboard('back_main'));
        } elseif ($data === 'menu_schedule') {
            editPhoto($config, $message, 'time.jpg', 'актуальное расписание на неделю всегда появляется в нашем Telegram-канале в понедельник:' . "\n" . '<a href="https://t.me/HarvestYouth">перейти в канал</a>', backKeyboard('back_main'));
        } elseif ($data === 'menu_features' || $data === 'back_features') {
            editPhoto($config, $message, 'main.jpg', $featuresText, featuresKeyboard());
        } elseif ($data === 'feat_serve') {
            logEvent($storageDir, $user, 'Хочу служить');
            editPhoto($config, $message, $serveSlides[0]['image'], $serveSlides[0]['text'], serveKeyboard(0, count($serveSlides)));
        } elseif (preg_match('/^srv_show_(\d+)$/', $data, $match)) {
            $index = (int) $match[1];
            if (isset($serveSlides[$index])) {
                editPhoto($config, $message, $serveSlides[$index]['image'], $serveSlides[$index]['text'], serveKeyboard($index, count($serveSlides)));
            }
        } elseif (preg_match('/^form_serve_start_(\d+)$/', $data, $match)) {
            $index = (int) $match[1];
            $service = $serveSlides[$index]['title'] ?? 'Команды и служения';
            beginFlow($config, $storageDir, $user, $chatId, 'serve', ['service' => $service]);
        } elseif ($data === 'feat_feedback') {
            logEvent($storageDir, $user, 'Вопрос / предложение');
            editPhoto($config, $message, 'feedback.jpg', 'здесь можно задать вопрос, предложить идею, сообщить об ошибке или просто оставить обратную связь.' . "\n\n" . 'нажми кнопку ниже — всё заполним прямо в боте.', ['inline_keyboard' => [
                [['text' => 'Написать сообщение', 'callback_data' => 'form_feedback_start']],
                [['text' => 'Назад', 'callback_data' => 'back_features']],
            ]]);
        } elseif ($data === 'form_feedback_start') {
            beginFlow($config, $storageDir, $user, $chatId, 'feedback');
        } elseif ($data === 'feat_homegroup') {
            logEvent($storageDir, $user, 'Найти домашку');
            editPhoto($config, $message, 'homegroup.jpg', 'домашняя группа — это место, где можно поговорить по-честному, разобраться в Библии и найти своих людей!' . "\n\n" . 'нажми кнопку ниже — подберём домашку прямо здесь.', ['inline_keyboard' => [
                [['text' => 'Подобрать домашку', 'callback_data' => 'form_homegroup_start']],
                [['text' => 'Назад', 'callback_data' => 'back_features']],
            ]]);
        } elseif ($data === 'form_homegroup_start') {
            beginFlow($config, $storageDir, $user, $chatId, 'homegroup');
        } elseif ($data === 'feat_prays') {
            logEvent($storageDir, $user, 'Молитвенная поддержка');
            editPhoto($config, $message, 'prays.jpg', 'молитвенная поддержка — это Божья атмосфера помощи и единства!' . "\n\n" . 'нажми кнопку ниже и напиши нужду прямо здесь. её получит только команда, которая будет молиться за тебя.', ['inline_keyboard' => [
                [['text' => 'Написать молитвенную нужду', 'callback_data' => 'form_prayer_start']],
                [['text' => 'Назад', 'callback_data' => 'back_features']],
            ]]);
        } elseif ($data === 'form_prayer_start') {
            beginFlow($config, $storageDir, $user, $chatId, 'prayer');
        } elseif ($data === 'feat_finance') {
            editPhoto($config, $message, 'finance.jpg', 'Бог доверил тебе многое: не только финансы, но и время, способности, силы.' . "\n" . 'всё это — ресурсы, через которые можно служить людям, делать добро и быть частью Божьего дела.' . "\n" . 'щедрость — это не про обязанность, а про сердце, готовое откликаться!' . "\n\n" . '<blockquote>«Не собирайте себе сокровищ на земле, где моль и ржа истребляют и где воры подкапывают и крадут; но собирайте себе сокровища на небе, где ни моль, ни ржа не истребляют и где воры не подкапывают и не крадут»' . "\n" . '(Евангелие от Матфея 6:19–20)</blockquote>' . "\n\n" . 'давайте вместе вкладываться в то, что имеет вечную ценность — в основание, которое не исчезнет и не сгорит' . "\n" . 'спасибо за твои пожертвования!', financeKeyboard());
        }
        jsonResponse(['ok' => true]);
    }

    if (isset($update['message'])) {
        $message = $update['message'];
        $user = $message['from'] ?? null;
        if (!is_array($user)) {
            jsonResponse(['ok' => true]);
        }
        $chatId = $message['chat']['id'];
        $text = trim((string) ($message['text'] ?? ''));
        if ($text === '/start' || str_starts_with($text, '/start@')) {
            clearState($storageDir, (int) $user['id']);
            logEvent($storageDir, $user, '/start');
            sendPhoto($config, $chatId, 'welcome.jpg', $welcomeText, mainKeyboard());
        } else {
            $state = loadState($storageDir, (int) $user['id']);
            if (is_array($state)) {
                handleFormMessage($config, $storageDir, $message, $state);
            } elseif ($text !== '' && !str_starts_with($text, '/')) {
                sendText($config, $chatId, 'Используй кнопки меню 🙂');
            }
        }
    }
} catch (Throwable $error) {
    error_log('Webhook error: ' . $error->getMessage());
    jsonResponse(['ok' => false], 500);
}

jsonResponse(['ok' => true]);
