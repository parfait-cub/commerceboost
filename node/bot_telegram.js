import { Telegraf } from "telegraf";
import axios from "axios";

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);
const ADMIN_IDS = process.env.ADMIN_USER_IDS.split(",");
const PYTHON_API_URL = process.env.PYTHON_API_URL;
const API_TOKEN = process.env.API_TOKEN;

function isAdmin(ctx) {
  return ADMIN_IDS.includes(ctx.from.id.toString());
}

bot.use((ctx, next) => {
  if (!isAdmin(ctx)) return ctx.reply("⛔ Accès refusé");
  return next();
});

bot.command("add_conseil", async (ctx) => {
  const conseil = ctx.message.text.replace("/add_conseil", "").trim();
  try {
    await axios.post(
      `${PYTHON_API_URL}/admin/conseil`,
      { conseil },
      { headers: { Authorization: `Bearer ${API_TOKEN}` } }
    );
    ctx.reply("✅ Conseil ajouté");
  } catch {
    ctx.reply("⚠️ API indisponible");
  }
});

bot.command("add_promo", async (ctx) => {
  const message = ctx.message.text.replace("/add_promo", "").trim();
  try {
    await axios.post(
      `${PYTHON_API_URL}/admin/promo`,
      { message },
      { headers: { Authorization: `Bearer ${API_TOKEN}` } }
    );
    ctx.reply("✅ Promo ajoutée");
  } catch {
    ctx.reply("⚠️ API indisponible");
  }
});

bot.launch();
