const token = process.env.TELEGRAM_BOT_TOKEN;
const workerUrl = process.env.WORKER_URL;
const secret = process.env.WEBHOOK_SECRET;

if (!token || !workerUrl || !secret) {
  throw new Error("Set TELEGRAM_BOT_TOKEN, WORKER_URL and WEBHOOK_SECRET");
}

const response = await fetch(`https://api.telegram.org/bot${token}/setWebhook`, {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    url: `${workerUrl.replace(/\/$/, "")}/webhook`,
    secret_token: secret,
    allowed_updates: ["message", "callback_query"],
    drop_pending_updates: true
  })
});

const result = await response.json();
if (!response.ok || !result.ok) {
  throw new Error(JSON.stringify(result));
}

console.log("Webhook configured:", result.description);
