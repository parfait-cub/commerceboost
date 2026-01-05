// node/core/bot_telegram.js
const { Telegraf, Markup } = require('telegraf');
const axios = require('axios');
require('dotenv').config();

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);
const PYTHON_API = process.env.PYTHON_API_URL || 'http://localhost:5000';
const API_TOKEN = process.env.API_TOKEN;

bot.start(async (ctx) => {
    const userId = ctx.from.id.toString();
    await ctx.reply('Bienvenue chez CommerceBoost !\nQuel est ton niveau de prix ?', Markup.inlineKeyboard([
        [Markup.button.callback('Bas', 'bas'), Markup.button.callback('Moyen', 'moyen'), Markup.button.callback('Élevé', 'élevé')]
    ]));
});

bot.action(['bas', 'moyen', 'élevé'], async (ctx) => {
    const userId = ctx.from.id.toString();
    await ctx.reply('Ton objectif principal ?', Markup.inlineKeyboard([
        [Markup.button.callback('Mieux fixer mes prix', 'prix'), Markup.button.callback('Attirer plus de clients', 'clients')]
    ]));
});

bot.action(['prix', 'clients'], async (ctx) => {
    const userId = ctx.from.id.toString();
    const niveau_prix = ctx.update.callback_query.data === 'prix' ? ctx.message.text.split(' ')[0] : await ctx.reply('Erreur niveau');
    const objectif = ctx.match[0] === 'prix' ? 'mieux fixer prix' : 'attirer plus de clients';
    try {
        await axios.post(`${PYTHON_API}/api/profile`, {
            user_id: userId,
            niveau_prix: niveau_prix,
            objectif: objectif
        }, { headers: { 'Authorization': `Bearer ${API_TOKEN}` } });
        await ctx.reply('Profil enregistré ! Essai gratuit 7 jours activé.\n\nCommandes :\n/prix → calculateur marge\n/promo → générer promo\n/abonnement → payer');
    } catch (e) {
        await ctx.reply('Erreur sauvegarde profil. Réessaie.');
    }
});

bot.command('prix', async (ctx) => {
    await ctx.reply('Envoie : prix achat, frais approx, prix vente actuel (ex: 5000 500 6000)');
});

bot.on('text', async (ctx) => {
    const text = ctx.message.text.trim();
    const userId = ctx.from.id.toString();

    if (/^\d+\s+\d+\s+\d+$/.test(text)) {
        const [achat, frais, vente_actuel] = text.split(' ').map(Number);
        try {
            const res = await axios.post(`${PYTHON_API}/api/calcul-prix`, {
                user_id: userId,
                achat,
                frais,
                vente_actuel
            }, { headers: { 'Authorization': `Bearer ${API_TOKEN}` }, timeout: 10000 });
            const data = res.data;
            let message = `Marge : ${data.marge || 0}%\n`;
            if (data.alerte) message += `${data.alerte}\n`;
            message += `Prix conseillé : ${data.prix_conseille || vente_actuel} FCFA`;
            await ctx.reply(message);
            await ctx.reply('Utile ?', Markup.inlineKeyboard([
                [Markup.button.callback('👍', 'utile'), Markup.button.callback('😐', 'moyen'), Markup.button.callback('👎', 'inutile')]
            ]));
        } catch (e) {
            await ctx.reply('Erreur calcul. Vérifie les valeurs et réessaie.');
        }
        return;
    }

    if (text.toLowerCase() === '/promo') {
        await ctx.reply('Type de promo ?', Markup.inlineKeyboard([
            [Markup.button.callback('Du jour', 'jour'), Markup.button.callback('Week-end', 'weekend'), Markup.button.callback('Déstockage', 'destockage')]
        ]));
        return;
    }

    if (text.toLowerCase() === '/abonnement') {
        await ctx.reply('Essai gratuit 7 jours terminé ?\nPayer 3 000 FCFA/mois via Flooz ou TMoney.\nEnvoie la preuve de paiement ici, je valide manuellement.');
    }
});

bot.action(['jour', 'weekend', 'destockage'], async (ctx) => {
    const type_promo = ctx.match[0];
    try {
        const res = await axios.post(`${PYTHON_API}/api/promo`, { type: type_promo }, { headers: { 'Authorization': `Bearer ${API_TOKEN}` } });
        await ctx.reply(res.data.message);
    } catch (e) {
        await ctx.reply('Erreur génération promo.');
    }
});

bot.action(['utile', 'moyen', 'inutile'], async (ctx) => {
    try {
        await axios.post(`${PYTHON_API}/api/feedback`, {
            user_id: ctx.from.id.toString(),
            reaction: ctx.match[0]
        }, { headers: { 'Authorization': `Bearer ${API_TOKEN}` } });
        await ctx.reply('Merci pour ton retour !');
    } catch (e) {
        await ctx.reply('Erreur feedback.');
    }
});

bot.launch();
console.log('Bot Telegram CommerceBoost V1 lancé');