// const fetch = require('node-fetch');

async function sendPushNotification(token, entry, sem, subject) {
  const message = {
    to: token,
    sound: 'default',
    title: `Attendance Marked - ${subject}`,
    body: `You were marked ${entry.status.toUpperCase()} on ${entry.date} at ${entry.time} by ${entry.teacher}.`,
    data: { subject, semester: sem }
  };

  await fetch('https://exp.host/--/api/v2/push/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(message)
  });
}

module.exports = sendPushNotification;
