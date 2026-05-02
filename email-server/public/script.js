const testMailForm = document.querySelector('#testMailForm');
const negotiationForm = document.querySelector('#negotiationForm');
const statusBox = document.querySelector('#statusBox');
const sendTestButton = document.querySelector('#sendTestButton');
const endNegotiationButton = document.querySelector('#endNegotiationButton');
const scheduleMeetingButton = document.querySelector('#scheduleMeetingButton');

function setStatus(message, type = 'loading') {
  statusBox.textContent = message;
  statusBox.className = `status-box ${type}`;
}

function setButtonLoading(button, isLoading, loadingText) {
  if (isLoading) {
    button.dataset.originalText = button.textContent.trim();
    button.textContent = loadingText;
    button.disabled = true;
    return;
  }

  button.textContent = button.dataset.originalText || button.textContent;
  button.disabled = false;
}

function setNegotiationLoading(isLoading, activeButton, loadingText) {
  [endNegotiationButton, scheduleMeetingButton].forEach((button) => {
    if (isLoading) {
      button.dataset.originalText = button.textContent.trim();
      button.disabled = true;

      if (button === activeButton) {
        button.textContent = loadingText;
      }

      return;
    }

    button.textContent = button.dataset.originalText || button.textContent;
    button.disabled = false;
  });
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || 'Request failed.');
  }

  return data;
}

function buildKolkataDateTime(date, time) {
  if (!date || !time) {
    throw new Error('Meeting date and time are required.');
  }

  return `${date}T${time}:00+05:30`;
}

function getMeetingPayload() {
  const sellerEmail = document.querySelector('#sellerEmail').value.trim();
  const meetingDate = document.querySelector('#meetingDate').value;
  const meetingStartTime = document.querySelector('#meetingStartTime').value;
  const meetingEndTime = document.querySelector('#meetingEndTime').value;

  const startTime = buildKolkataDateTime(meetingDate, meetingStartTime);
  const endTime = buildKolkataDateTime(meetingDate, meetingEndTime);

  if (new Date(endTime) <= new Date(startTime)) {
    throw new Error('End time must be after start time.');
  }

  return {
    sellerEmail,
    startTime,
    endTime
  };
}

function formatMeetingStatus(data) {
  if (!data.meetLink) {
    return data.message;
  }

  return `${data.message} Meet link: ${data.meetLink}`;
}

testMailForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const email = document.querySelector('#recipientEmail').value.trim();
  const agentLink = document.querySelector('#agentLink').value.trim();

  setButtonLoading(sendTestButton, true, 'Sending...');
  setStatus('Sending negotiation link email to seller...', 'loading');

  try {
    const data = await postJson('/send-mail', { email, agentLink });
    setStatus(data.message, 'success');
    testMailForm.reset();
  } catch (error) {
    setStatus(error.message, 'error');
  } finally {
    setButtonLoading(sendTestButton, false);
  }
});

negotiationForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const action = event.submitter?.dataset.action || 'end';
  const activeButton = action === 'schedule' ? scheduleMeetingButton : endNegotiationButton;
  const endpoint = action === 'schedule' ? '/schedule-meeting' : '/end-negotiation';
  const loadingText = action === 'schedule' ? 'Scheduling...' : 'Completing...';
  const loadingMessage =
    action === 'schedule'
      ? 'Scheduling meeting and sending confirmations...'
      : 'Completing negotiation, scheduling meeting, and sending confirmations...';

  setNegotiationLoading(true, activeButton, loadingText);
  setStatus(loadingMessage, 'loading');

  try {
    const payload = {
      ...getMeetingPayload(),
      status: 'completed'
    };
    const data = await postJson(endpoint, payload);
    setStatus(formatMeetingStatus(data), 'success');
    negotiationForm.reset();
  } catch (error) {
    setStatus(error.message, 'error');
  } finally {
    setNegotiationLoading(false);
  }
});
