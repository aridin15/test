const express = require('express');
const app = express();
const axios = require('axios');
const dotenv = require('dotenv');

dotenv.config();

app.get('/healthz', (req, res) => res.status(200).send('OK'));

app.get('/api/node', (req, res) => {
  res.send('Hello, World from Node.js!');
});

app.post('/api/fetch', async (req, res) => {
  console.log('inside api fetch');
  console.log(`process env flask uri is: ${process.env.FLASK_API_URL}`);
  try {
    const result = await axios.get(process.env.FLASK_API_URL);
    res.status(200).json({
      data: result.data
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
