# REG.RU webhook

PHP webhook for the HarvestYouth Telegram bot. It is designed for REG.RU shared hosting and does not require a background process.

Requirements: PHP 8.0 or newer with the cURL extension, HTTPS and write access to `storage/`.

## Deployment

1. Copy this directory to an HTTPS-accessible directory on the church site.
2. Copy `config.example.php` to `config.php` and fill in both bot tokens, the feedback group ID, a private fallback administrator ID and a random webhook secret. If the group ID is not known yet, set `admin_chat_id` to `0`; completed applications will go to the fallback administrator through the main bot.
3. Ensure PHP can write to `storage/`.
4. Register `webhook.php` as the webhook for `@harvestyouth_bot` with the same secret.

The `storage/` directory contains form state, statistics and a JSONL application archive. Both it and `config.php` are blocked by `.htaccess`.
