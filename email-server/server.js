const express = require('express');
const http = require('http');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

const { sendMail, createMeeting } = require('./googleService');

const app = express();
const DEFAULT_PORT = 3000;
const PORT = Number.parseInt(process.env.PORT || DEFAULT_PORT, 10);
const MAX_PORT_ATTEMPTS = 10;
const MEETING_SUBJECT = 'Meeting Scheduled';
const MEETING_BODY =
  'Your negotiation meeting has been scheduled. Please check your Google Calendar for details.';
const NEGOTIATION_LINK_SUBJECT = 'Negotiation Link for Your Deal Discussion';

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

function getMeetLink(event) {
  return (
    event?.hangoutLink ||
    event?.conferenceData?.entryPoints?.find((entryPoint) => entryPoint.entryPointType === 'video')?.uri ||
    null
  );
}

function getMessageIds(results) {
  return results.map((result) => result.id).filter(Boolean);
}

function getBuyerEmailFromEvent(event) {
  return event?.organizer?.email || event?.creator?.email || null;
}

function requireFields(body, fields) {
  const missingFields = fields.filter((field) => !String(body[field] || '').trim());

  if (missingFields.length > 0) {
    return `${missingFields.join(', ')} ${missingFields.length === 1 ? 'is' : 'are'} required.`;
  }

  return null;
}

function normalizeUrl(value, fieldName) {
  const normalized = String(value || '').trim();

  if (!normalized) {
    throw new Error(`${fieldName} is required.`);
  }

  try {
    return new URL(normalized).toString();
  } catch (error) {
    throw new Error(`${fieldName} must be a valid URL.`);
  }
}

function buildNegotiationLinkEmailBody(agentLink) {
  return [
    'Hello Seller,',
    '',
    'Your negotiation session is ready.',
    'Please use the link below to join the negotiation with the agent:',
    '',
    agentLink,
    '',
    'If you have any trouble opening the link, please reply to this email for assistance.',
    '',
    'Regards,',
    'Smart Deal Team'
  ].join('\n');
}

async function sendMeetingNotifications(buyerEmail, sellerEmail) {
  const recipients = [...new Set([buyerEmail, sellerEmail].filter(Boolean))];
  return Promise.all(recipients.map((email) => sendMail(email, MEETING_SUBJECT, MEETING_BODY)));
}

async function scheduleNegotiationMeeting({ sellerEmail, startTime, endTime }) {
  const event = await createMeeting([sellerEmail], startTime, endTime);
  const buyerEmail = getBuyerEmailFromEvent(event);
  const emailResults = await sendMeetingNotifications(buyerEmail, sellerEmail);

  return {
    event,
    emailResults,
    meetLink: getMeetLink(event),
    buyerEmail
  };
}

app.post('/send-mail', async (req, res) => {
  const email = req.body.email || req.body.recipient;
  const agentLink = req.body.agentLink;

  if (!email || !String(agentLink || '').trim()) {
    return res.status(400).json({
      success: false,
      message: 'Recipient email and agent link are required.'
    });
  }

  try {
    const normalizedAgentLink = normalizeUrl(agentLink, 'Agent link');
    const info = await sendMail(
      email,
      NEGOTIATION_LINK_SUBJECT,
      buildNegotiationLinkEmailBody(normalizedAgentLink)
    );

    console.log(`Negotiation link email sent to ${email}: ${info.id}`);

    return res.status(200).json({
      success: true,
      message: `Negotiation link email sent successfully to ${email}.`,
      messageId: info.id
    });
  } catch (error) {
    console.error('Failed to send negotiation link email:', error.message);

    return res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

app.post('/schedule-meeting', async (req, res) => {
  const validationError = requireFields(req.body, ['sellerEmail', 'startTime', 'endTime']);

  if (validationError) {
    return res.status(400).json({
      success: false,
      message: validationError
    });
  }

  try {
    const { sellerEmail, startTime, endTime } = req.body;
    const { event, emailResults, meetLink, buyerEmail } = await scheduleNegotiationMeeting({
      sellerEmail,
      startTime,
      endTime
    });

    console.log(`Meeting scheduled for ${buyerEmail || 'connected buyer account'} and ${sellerEmail}: ${event.id}`);

    return res.status(201).json({
      success: true,
      message: 'Meeting scheduled and confirmation emails sent.',
      eventId: event.id,
      calendarLink: event.htmlLink,
      meetLink,
      emailMessageIds: getMessageIds(emailResults)
    });
  } catch (error) {
    console.error('Failed to schedule meeting:', error.message);

    return res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

app.post('/end-negotiation', async (req, res) => {
  const { buyerEmail, sellerEmail, status = 'completed', startTime, endTime } = req.body;

  if (!sellerEmail) {
    return res.status(400).json({
      success: false,
      message: 'Seller email is required.'
    });
  }

  if (status !== 'completed') {
    return res.status(200).json({
      success: true,
      message: `Negotiation status is ${status}. No completion action was taken.`
    });
  }

  try {
    if (startTime && endTime) {
      const { event, emailResults, meetLink, buyerEmail: derivedBuyerEmail } = await scheduleNegotiationMeeting({
        sellerEmail,
        startTime,
        endTime
      });

      console.log(
        `Negotiation completed and meeting scheduled for ${derivedBuyerEmail || 'connected buyer account'} and ${sellerEmail}: ${event.id}`
      );

      return res.status(200).json({
        success: true,
        message: 'Negotiation completed. Meeting scheduled and confirmation emails sent.',
        eventId: event.id,
        calendarLink: event.htmlLink,
        meetLink,
        emailMessageIds: getMessageIds(emailResults)
      });
    }

    const recipients = [...new Set([buyerEmail, sellerEmail].filter(Boolean))];
    const results = await Promise.all(
      recipients.map((email) =>
        sendMail(email, 'Deal Completed', 'Your negotiation has been successfully completed.')
      )
    );

    console.log(`Negotiation completion emails sent to ${recipients.join(', ')}.`);

    return res.status(200).json({
      success: true,
      message: 'Negotiation completed. Completion emails sent successfully.',
      emailMessageIds: getMessageIds(results)
    });
  } catch (error) {
    console.error('Failed to complete negotiation workflow:', error.message);

    return res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

function startServer(preferredPort, attemptsRemaining = MAX_PORT_ATTEMPTS) {
  const server = http.createServer(app);

  server.once('error', (error) => {
    if (error.code === 'EADDRINUSE' && attemptsRemaining > 1) {
      const nextPort = preferredPort + 1;

      console.warn(`Port ${preferredPort} is busy. Trying port ${nextPort}...`);
      startServer(nextPort, attemptsRemaining - 1);
      return;
    }

    console.error(`Failed to start server on port ${preferredPort}:`, error);
    process.exit(1);
  });

  server.listen(preferredPort, () => {
    console.log(`Smart Deal Google API System running at http://localhost:${preferredPort}`);
  });
}

startServer(Number.isNaN(PORT) ? DEFAULT_PORT : PORT);
