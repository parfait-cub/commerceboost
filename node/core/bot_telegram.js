// node/core/bot_telegram.js
const { Telegraf, Markup } = require('telegraf');
const axios = require('axios');
require('dotenv').config();

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);
const PYTHON_API = process.env.PYTHON_API_URL || 'http://localhost:5000';

let userStates = {};

bot.start(async (ctx) => {
    const userId = ctx.from.id.toString();
    userStates[userId] = { step: 'niveau_prix' };
    await ctx.reply('Bienvenue chez CommerceBoost !\nTon niveau de prix ?', Markup.inlineKeyboard([
        [Markup.button.callback('Bas', 'bas'), Markup.button.callback('Moyen', 'moyen'), Markup.button.callback('Élevé', 'élevé')]
    ]));
});

bot.action(['bas', 'moyen', 'élevé'], async (ctx) => {
    const userId = ctx.from.id.toString();
    userStates[userId].niveau_prix = ctx.match[0];
    userStates[userId].step = 'objectif';
    await ctx.reply('Ton objectif principal ?', Markup.inlineKeyboard([
        [Markup.button.callback('Mieux fixer mes prix', 'prix'), Markup.button.callback('Attirer plus de clients', 'clients')]
    ]));
});

bot.action(['prix', 'clients'], async (ctx) => {
    const userId = ctx.from.id.toString();
    const objectif = ctx.match[0] === 'prix' ? 'mieux fixer prix' : 'attirer plus de clients';
    await axios.post(`${PYTHON_API}/api/profile`, {
        user_id: userId,
        niveau_prix: userStates[userId].niveau_prix,
        objectif: objectif
    });
    await ctx.reply('Profil enregistré ! Essai gratuit 7 jours activé.\n\nCommandes :\n/prix → calculateur marge\n/promo → générer promo\n/abonnement → payer');
    delete userStates[userId];
});

bot.command('prix', async (ctx) => {
    ctx.reply('Envoie prix d’achat, frais approx, prix de vente actuel (ex: 5000 500 6000)');
});

bot.on('text', async (ctx) => {
    const text = ctx.message.text;
    const userId = ctx.from.id.toString();

    if (text.includes(' ')) {
        const parts = text.split(' ').map(Number);
        if (parts.length === 3 && parts.every(n => !isNaN(n))) {
            const [achat, frais, vente] = parts;
            const res = await axios.post(`${PYTHON_API}/api/calcul-prix`, { achat, frais, vente_actuel: vente });
            const data = res.data;
            let message = `Marge : ${data.marge}%\n`;
            if (data.alerte) message += data.alerte + '\n';
            message += `Prix conseillé : ${data.prix_conseille} FCFA`;
            await ctx.reply(message);
            await ctx.reply('Utile ?', Markup.inlineKeyboard([
                [Markup.button.callback('👍', 'utile'), Markup.button.callback('😐', 'moyen'), Markup.button.callback('👎', 'inutile')]
            ]));
            return;
        }
    }

    if (text === '/promo') {
        await ctx.reply('Type de promo ?', Markup.inlineKeyboard([
            [Markup.button.callback('Du jour', 'jour'), Markup.button.callback('Week-end', 'weekend'), Markup.button.callback('Déstockage', 'destockage')]
        ]));
        return;
    }

    if (text === '/abonnement') {
        await ctx.reply('Essai gratuit 7 jours.\nPour continuer : 3 000 FCFA/mois via Flooz ou TMoney au [ton numéro].\nEnvoie la preuve de paiement ici.');
    }
});

bot.action(['utile', 'moyen', 'inutile'], async (ctx) => {
    await axios.post(`${PYTHON_API}/api/feedback`, {
        user_id: ctx.from.id.toString(),
        reaction: ctx.match[0]
    });
    await ctx.reply('Merci pour ton retour !');
});

bot.launch();
console.log('Bot Telegram CommerceBoost V1 lancé');