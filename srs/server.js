// Entry point: only starts the server.
const app = require('./app');
const config = require('./config');

app.listen(config.port, () => {
  console.log(`SmartCine running at http://localhost:${config.port}`);
});
