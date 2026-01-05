// node/core/bot_messenger.js
const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());

const VERIFY_TOKEN = process.env.MESSENGER_VERIFY_TOKEN;
const PAGE_ACCESS_TOKEN = process.env.PAGE_ACCESS_TOKEN;

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
            const event = entry.messaging[0];
            if (event.message && event.message.text) {
                await callSendAPI(event.sender.id, { text: "Messenger en cours de développement. Utilise Telegram pour la V1 complète." });
            }
        }
        res.sendStatus(200);
    }
});

async function callSendAPI(sender, response) {
    await axios.post(`https://graph.facebook.com/v20.0/me/messages?access_token=${PAGE_ACCESS_TOKEN}`, {
        recipient: { id: sender },
        message: response
    });
}

app.listen(process.env.PORT || 3000, () => console.log('Bot Messenger actif'));