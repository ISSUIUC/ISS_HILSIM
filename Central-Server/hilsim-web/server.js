const express = require('express');
const path = require('path');

const app = express();

// Serve the static files from the React app
app.use(express.static(path.join(__dirname, 'build')));


// Handles any requests that don't match the ones above
app.get('*', (req, res) => {res.sendFile(path.resolve(__dirname, 'build', 'index.html'));});

const port = process.env.PORT || 8080;
app.listen(port, () => {
    console.clear()
    console.log(`Successfully initialized Webapp Server @ localhost:${port}`)
  })