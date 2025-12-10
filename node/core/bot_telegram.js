// node/core/bot_telegram.js
const { Telegraf, Markup } = require('telegraf');
const axios = require('axios');
const Joi = require('joi');
require('dotenv').config();

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);
const PYTHON_API = process.env.PYTHON_API_URL;
const API_TOKEN = process.env.API_TOKEN;
const ADMIN_IDS = process.env.ADMIN_TELEGRAM_IDS.split(',').map(id => id.trim());

let userStates = {};

bot.start(async (ctx) => {
    const userId = ctx.from.id.toString();
    userStates[userId] = { step: 'onboarding_type', data: {} };

    await ctx.reply(
        '🚀 Bienvenue chez CommerceBoost ! Choisis ton type de commerce :',
        Markup.inlineKeyboard([
            [Markup.button.callback('🏪 Physique', 'type_physique')],
            [Markup.button.callback('🛒 En ligne', 'type_online')],
            [Markup.button.callback('🔄 Mixte', 'type_mixte')]
        ])
    );
});

bot.action(/type_(physique|online|mixte)/, async (ctx) => {
    const userId = ctx.from.id.toString();
    const type = ctx.match[1];
    userStates[userId].data.business_type = type;
    userStates[userId].step = 'sector';
    await ctx.reply('Secteur ?', Markup.inlineKeyboard([
        [Markup.button.callback('🍴 Alimentation', 'sector_alimentation')],
        [Markup.button.callback('👗 Mode', 'sector_mode')],
        [Markup.button.callback('💄 Beauté', 'sector_beaute')],
        [Markup.button.callback('📱 Électronique', 'sector_electronique')],
        [Markup.button.callback('Autre', 'sector_autre')]
    ]));
});

bot.action(/sector_(.+)/, async (ctx) => {
    const userId = ctx.from.id.toString();
    userStates[userId].data.sector = ctx.match[1];
    userStates[userId].step = 'level';
    await ctx.reply('Niveau ?', Markup.inlineKeyboard([
        [Markup.button.callback('Débutant', 'level_debutant')],
        [Markup.button.callback('Intermédiaire', 'level_intermediaire')],
        [Markup.button.callback('Expérimenté', 'level_experimente')]
    ]));
});

bot.action(/level_(debutant|intermediaire|experimente)/, async (ctx) => {
    const userId = ctx.from.id.toString();
    userStates[userId].data.level = ctx.match[1];
    try {
        await axios.post(`${PYTHON_API}/api/user/profile`, {
            user_id: userId,
            profile: userStates[userId].data
        }, { headers: { Authorization: `Bearer ${API_TOKEN}` } });
        await ctx.reply('Profil enregistré ! Essai gratuit activé.');
    } catch (err) {
        await ctx.reply('Erreur enregistrement.');
    }
    delete userStates[userId].step;
});

bot.command('beta', async (ctx) => {
    const userId = ctx.from.id.toString();
    userStates[userId].step = 'beta_code';
    await ctx.reply('Entre ton code bêta :');
});

bot.command('parrain', async (ctx) => {
    const userId = ctx.from.id.toString();
    try {
        const { data } = await axios.post(`${PYTHON_API}/api/referral/generate`, { user_id: userId }, { headers: { Authorization: `Bearer ${API_TOKEN}` } });
        await ctx.reply(`Ton code parrain : ${data.code} (-30% pour toi et ton filleul)`);
    } catch (err) {
        await ctx.reply('Erreur génération code.');
    }
});

bot.command('appliquer_parrain', async (ctx) => {
    const userId = ctx.from.id.toString();
    userStates[userId].step = 'referral_code';
    await ctx.reply('Entre le code parrain :');
});

bot.command('admin', async (ctx) => {
    const userId = ctx.from.id.toString();
    if (!ADMIN_IDS.includes(userId)) return ctx.reply('Accès refusé.');

    try {
        const { data } = await axios.get(`${PYTHON_API}/api/admin/users`, { headers: { Authorization: `Bearer ${API_TOKEN}` } });
        let msg = 'Utilisateurs :\n';
        data.forEach(u => msg += `${u.user_id} - ${u.business_type} - Abonné: ${u.subscription?.active ? 'Oui' : 'Non'}\n`);
        await ctx.reply(msg);
    } catch (err) {
        await ctx.reply('Erreur dashboard.');
    }
    // Ajoute boutons pour histo, feedback, etc.
});

bot.on('text', async (ctx) => {
    const userId = ctx.from.id.toString();
    const text = ctx.message.text;

    const schema = Joi.string().min(1).max(1000);
    if (schema.validate(text).error) return ctx.reply('Input invalide.');

    const hour = new Date().getHours(); // GMT pour Togo
    if (hour >= 1 && hour < 4) return ctx.reply('Bot en maintenance (01h-04h).');

    try {
        const { data: sub } = await axios.get(`${PYTHON_API}/api/subscription/check?user_id=${userId}`, { headers: { Authorization: `Bearer ${API_TOKEN}` } });
        if (!sub.active) return ctx.reply('Abonne-toi pour accéder !');
    } catch (err) {
        return ctx.reply('Erreur vérification abonnement.');
    }

    if (userStates[userId]?.step === 'beta_code') {
        try {
            const { data } = await axios.post(`${PYTHON_API}/api/beta/register`, { user_id: userId, code: text }, { headers: { Authorization: `Bearer ${API_TOKEN}` } });
            if (data.success) {
                await ctx.reply(`Bêta activé ! Rejoins le groupe : ${data.group_link}`);
            } else {
                await ctx.reply(data.error);
            }
        } catch (err) {
            await ctx.reply('Erreur activation bêta.');
        }
        delete userStates[userId].step;
        return;
    }

    if (userStates[userId]?.step === 'referral_code') {
        try {
            const { data } = await axios.post(`${PYTHON_API}/api/referral/apply`, { code: text, new_user_id: userId }, { headers: { Authorization: `Bearer ${API_TOKEN}` } });
            if (data.success) {
                await ctx.reply('Réduction -30% appliquée !');
            } else {
                await ctx.reply(data.error);
            }
        } catch (err) {
            await ctx.reply('Erreur application code.');
        }
        delete userStates[userId].step;
        return;
    }

    try {
        const { data } = await axios.post(`${PYTHON_API}/api/ia`, { user_id: userId, question: text, context: userStates[userId]?.data || {} }, { headers: { Authorization: `Bearer ${API_TOKEN}` } });
        await ctx.reply(data.response, { parse_mode: 'Markdown' });
    } catch (err) {
        await ctx.reply('Erreur IA, réessaie.');
    }
});

bot.launch().then(() => console.log('Bot Telegram démarré'));