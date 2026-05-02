const path = require('path');
const { randomUUID } = require('crypto');
const { google } = require('googleapis');

require('dotenv').config({ path: path.join(__dirname, '.env') });

const TIME_ZONE = 'Asia/Kolkata';
const REQUIRED_ENV = ['CLIENT_ID', 'CLIENT_SECRET', 'REDIRECT_URI', 'REFRESH_TOKEN'];

let oauth2Client;
let gmailClient;
let calendarClient;

function getMissingGoogleConfig() {
  return REQUIRED_ENV.filter((name) => {
    const value = process.env[name];
    return !value || value.trim() === '' || value.trim().startsWith('your_');
  });
}

function getOAuth2Client() {
  if (oauth2Client) {
    return oauth2Client;
  }

  const missingConfig = getMissingGoogleConfig();

  if (missingConfig.length > 0) {
    throw new Error(`Missing Google OAuth2 configuration: ${missingConfig.join(', ')}`);
  }

  oauth2Client = new google.auth.OAuth2(
    process.env.CLIENT_ID,
    process.env.CLIENT_SECRET,
    process.env.REDIRECT_URI
  );

  oauth2Client.setCredentials({
    refresh_token: process.env.REFRESH_TOKEN
  });

  oauth2Client.on('tokens', (tokens) => {
    if (tokens.access_token) {
      console.log('Google OAuth2 access token refreshed.');
    }
  });

  return oauth2Client;
}

function getGmailClient() {
  if (!gmailClient) {
    gmailClient = google.gmail({ version: 'v1', auth: getOAuth2Client() });
  }

  return gmailClient;
}

function getCalendarClient() {
  if (!calendarClient) {
    calendarClient = google.calendar({ version: 'v3', auth: getOAuth2Client() });
  }

  return calendarClient;
}

function normalizeHeaderValue(value, fieldName) {
  const normalized = String(value || '').trim().replace(/[\r\n]+/g, ' ');

  if (!normalized) {
    throw new Error(`${fieldName} is required.`);
  }

  return normalized;
}

function encodeBase64Url(value) {
  return Buffer.from(value, 'utf8')
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

function encodeMimeWord(value) {
  return Buffer.from(value, 'utf8').toString('base64');
}

function createRawEmail(to, subject, text) {
  const recipient = normalizeHeaderValue(to, 'Recipient email');
  const encodedSubject = encodeMimeWord(normalizeHeaderValue(subject, 'Email subject'));
  const body = String(text || '');

  const message = [
    `To: ${recipient}`,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset="UTF-8"',
    'Content-Transfer-Encoding: 8bit',
    `Subject: =?UTF-8?B?${encodedSubject}?=`,
    '',
    body
  ].join('\r\n');

  return encodeBase64Url(message);
}

function getGoogleApiErrorMessage(error) {
  return (
    error?.response?.data?.error_description ||
    error?.response?.data?.error?.message ||
    error?.errors?.[0]?.message ||
    error?.message ||
    'Unknown Google API error.'
  );
}

async function sendMail(to, subject, text) {
  const recipient = normalizeHeaderValue(to, 'Recipient email');

  try {
    const response = await getGmailClient().users.messages.send({
      userId: 'me',
      requestBody: {
        raw: createRawEmail(recipient, subject, text)
      }
    });

    console.log(`Gmail API email sent to ${recipient}: ${response.data.id}`);
    return response.data;
  } catch (error) {
    const message = getGoogleApiErrorMessage(error);
    console.error(`Gmail API email failed for ${recipient}: ${message}`);
    throw new Error(`Failed to send email to ${recipient}: ${message}`);
  }
}

function normalizeAttendees(emails) {
  if (!Array.isArray(emails) || emails.length === 0) {
    throw new Error('At least one attendee email is required.');
  }

  const uniqueEmails = [...new Set(emails.map((email) => String(email || '').trim()).filter(Boolean))];

  if (uniqueEmails.length === 0) {
    throw new Error('At least one attendee email is required.');
  }

  return uniqueEmails.map((email) => ({ email }));
}

function toKolkataDateTime(value, fieldName) {
  const rawValue = String(value || '').trim();

  if (!rawValue) {
    throw new Error(`${fieldName} is required.`);
  }

  if (/[zZ]$|[+-]\d{2}:\d{2}$/.test(rawValue)) {
    return rawValue;
  }

  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(rawValue)) {
    return `${rawValue}:00+05:30`;
  }

  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(rawValue)) {
    return `${rawValue}+05:30`;
  }

  return rawValue;
}

function assertValidMeetingWindow(startDateTime, endDateTime) {
  const startDate = new Date(startDateTime);
  const endDate = new Date(endDateTime);

  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
    throw new Error('Meeting startTime and endTime must be valid date-time values.');
  }

  if (endDate <= startDate) {
    throw new Error('Meeting endTime must be after startTime.');
  }
}

async function createMeeting(emails, startTime, endTime) {
  const attendees = normalizeAttendees(emails);
  const startDateTime = toKolkataDateTime(startTime, 'Meeting startTime');
  const endDateTime = toKolkataDateTime(endTime, 'Meeting endTime');

  assertValidMeetingWindow(startDateTime, endDateTime);

  const event = {
    summary: 'Negotiation Meeting',
    description: 'Negotiation meeting scheduled after deal completion.',
    start: {
      dateTime: startDateTime,
      timeZone: TIME_ZONE
    },
    end: {
      dateTime: endDateTime,
      timeZone: TIME_ZONE
    },
    attendees,
    conferenceData: {
      createRequest: {
        requestId: `negotiation-${randomUUID()}`,
        conferenceSolutionKey: {
          type: 'hangoutsMeet'
        }
      }
    }
  };

  try {
    const response = await getCalendarClient().events.insert({
      calendarId: 'primary',
      conferenceDataVersion: 1,
      sendUpdates: 'all',
      requestBody: event
    });

    console.log(`Google Calendar meeting created: ${response.data.id}`);
    return response.data;
  } catch (error) {
    const message = getGoogleApiErrorMessage(error);
    console.error(`Google Calendar meeting creation failed: ${message}`);
    throw new Error(`Failed to create Google Calendar meeting: ${message}`);
  }
}

module.exports = {
  sendMail,
  createMeeting
};
