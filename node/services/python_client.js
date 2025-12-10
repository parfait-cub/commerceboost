// node/services/python_client.js
const axios = require('axios');
require('dotenv').config();

const PYTHON_API = process.env.PYTHON_API_URL;
const API_TOKEN = process.env.API_TOKEN;

const api = axios.create({
    baseURL: PYTHON_API,
    headers: { 'Authorization': `Bearer ${API_TOKEN}` }
});

module.exports = api;