import express from "express";
import axios from "axios";

const app = express();
app.use(express.json());

const PAGE_ACCESS_TOKEN = process.env.PAGE_ACCESS_TOKEN;
const VERIFY_TOKEN = process.env.MESSENGER_VERIFY_TOKEN;
const PYTHON_API_URL = process.env.PYTHON_API_URL;
const API_TOKEN = process.env.API_TOKEN;

app.get("/webhook", (req, res) => {
  if (req.query["hub.verify_token"] === VERIFY_TOKEN) {
    return res.send(req.query["hub.challenge"]);
  }
  res.sendStatus(403);
});

app.post("/webhook", async (req, res) => {
  const entries = req.body.entry || [];

  for (const entry of entries) {
    const events = entry.messaging || [];
    for (const event of events) {
      if (event.message?.text) {
        try {
          const response = await axios.post(
            `${PYTHON_API_URL}/promo`,
            {},
            { headers: { Authorization: `Bearer ${API_TOKEN}` } }
          );

          await axios.post(
            `https://graph.facebook.com/v18.0/me/messages?access_token=${PAGE_ACCESS_TOKEN}`,
            {
              recipient: { id: event.sender.id },
              message: { text: response.data.message }
            }
          );
        } catch (e) {
          console.error("Messenger error:", e.message);
        }
      }
    }
  }
  res.sendStatus(200);
});

app.listen(process.env.PORT || 3000);
