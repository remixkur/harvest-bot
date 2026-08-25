# Cloudflare deployment

This directory contains the webhook version of the HarvestYouth Telegram bot.

## One-time deployment

1. Install dependencies: `npm install`
2. Log in to Cloudflare: `npx wrangler login`
3. Create D1: `npm run db:create`
4. Put the returned database ID into `wrangler.toml`
5. Apply migrations: `npm run db:migrate`
6. Add secrets:
   - `npx wrangler secret put BOT_TOKEN`
   - `npx wrangler secret put WEBHOOK_SECRET`
7. Deploy: `npm run deploy`
8. Configure Telegram webhook:

```sh
TELEGRAM_BOT_TOKEN="..." \
WORKER_URL="https://harvest-youth-bot.<account>.workers.dev" \
WEBHOOK_SECRET="..." \
node scripts/set-webhook.mjs
```

The old polling service must be stopped only after the webhook responds successfully.
