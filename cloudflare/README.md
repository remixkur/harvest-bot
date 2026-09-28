# Cloudflare relay

This Worker is a fast ingress relay for Telegram. It acknowledges Telegram updates immediately and forwards them in the background to the PHP webhook hosted on REG.RU. Bot logic, form state, statistics and application storage remain on REG.RU.

## Deployment

1. Install dependencies: `npm install`.
2. Log in to Cloudflare: `npx wrangler login`.
3. Set `UPSTREAM_URL` in `wrangler.toml` to the REG.RU webhook URL.
4. Set the Telegram-facing secret: `npx wrangler secret put WEBHOOK_SECRET`.
5. Set the matching REG.RU secret: `npx wrangler secret put UPSTREAM_SECRET`.
6. Check the code: `npm run check`.
7. Deploy: `npm run deploy`.
8. Register `<worker-url>/webhook` as the webhook for the Telegram bot.

The Worker does not contain bot tokens and does not persist user data.
