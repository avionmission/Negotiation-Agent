const path = require('path');
const readline = require('readline');
const { google } = require('googleapis');

require('dotenv').config({ path: path.join(__dirname, '.env') });

const scopes = [
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/calendar.events'
];

function requireEnv(name) {
  const value = process.env[name];

  if (!value || value.trim() === '' || value.trim().startsWith('your_')) {
    throw new Error(`${name} must be set in .env before generating a refresh token.`);
  }

  return value.trim();
}

function ask(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

async function main() {
  const oauth2Client = new google.auth.OAuth2(
    requireEnv('CLIENT_ID'),
    requireEnv('CLIENT_SECRET'),
    requireEnv('REDIRECT_URI')
  );

  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    prompt: 'consent',
    scope: scopes
  });

  console.log('\nOpen this URL in your browser:\n');
  console.log(authUrl);
  console.log('\nAfter approving, Google will redirect to your REDIRECT_URI.');
  console.log('If the localhost page does not load, copy the code= value from the browser address bar.\n');

  const code = await ask('Paste the code here: ');

  if (!code) {
    throw new Error('Authorization code is required.');
  }

  const { tokens } = await oauth2Client.getToken(code);

  if (!tokens.refresh_token) {
    console.log('\nNo refresh token was returned.');
    console.log('Try again after removing this app from your Google Account access list, then rerun this script.');
    console.log('Also make sure prompt: consent and access_type: offline are being used.\n');
    return;
  }

  console.log('\nAdd this to your .env:\n');
  console.log(`REFRESH_TOKEN=${tokens.refresh_token}`);
  console.log('\nThen restart the server with npm start.\n');
}

main().catch((error) => {
  console.error(`\nFailed to generate refresh token: ${error.message}\n`);
  process.exit(1);
});
