// node/core/bot_messenger.js
const express = require('express');
const axios = require('axios');
const Joi = require('joi');
const app = express();
require('dotenv').config();

app.use(express.json());

const VERIFY_TOKEN = process.env.MESSENGER_VERIFY_TOKEN;
const PAGE_ACCESS_TOKEN = process.env.MESSENGER_PAGE_ACCESS_TOKEN;
const PYTHON_API = process.env.PYTHON_API_URL;
const API_TOKEN = process.env.API_TOKEN;

let userStates = {};

app.get('/webhook', (req, res) => {
    if (req.query['hub.verify_token'] === VERIFY_TOKEN) {
        res.send(req.query['hub.challenge']);
    } else {
        res.sendStatus(403);
    }
});

app.post('/webhook', async (req, res) => {
    const body = req.body;
    if (body.object === 'page') {
        for (const entry of body.entry) {
            const webhook_event = entry.messaging[0];
            const sender_psid = webhook_event.sender.id;

            if (webhook_event.message) {
                const text = webhook_event.message.text;
                if (!text) return res.sendStatus(200);

                const schema = Joi.string().min(1).max(500);
                const { error } = schema.validate(text);
                if (error) return callSendAPI(sender_psid, { text: 'Message invalide.' });

                try {
                    const sub = await axios.get(`${PYTHON_API}/api/subscription/check?user_id=${sender_psid}`, {
                        headers: { Authorization: `Bearer ${API_TOKEN}` }
                    });
                    if (!sub.data.active) {
                        return callSendAPI(sender_psid, { text: 'Abonne-toi pour accéder ! Essai gratuit 5 jours.' });
                    }
                } catch (err) {
                    return callSendAPI(sender_psid, { text: 'Erreur sub, réessaie.' });
                }

                // Handle onboarding, beta, etc. similar to Telegram (implement flows)

                try {
                    const resp = await axios.post(`${PYTHON_API}/api/ia`, {
                        user_id: sender_psid,
                        question: text,
                        context: userStates[sender_psid] || {}
                    }, { headers: { Authorization: `Bearer ${API_TOKEN}` } });
                    await callSendAPI(sender_psid, { text: resp.data.response });
                } catch (err) {
                    await callSendAPI(sender_psid, { text: "Erreur, réessaie." });
                }
            }
        }
        res.sendStatus(200);
    } else {
        res.sendStatus(404);
    }
});

async function callSendAPI(sender_psid, response) {
    const request_body = {
        recipient: { id: sender_psid },
        message: response
    };

    try {
        await axios.post(
            `https://graph.facebook.com/v20.0/me/messages?access_token=${PAGE_ACCESS_TOKEN}`,
            request_body
        );
    } catch (err) {
        console.error('Erreur envoi Messenger:', err);
    }
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Bot Messenger sur port ${PORT}`));