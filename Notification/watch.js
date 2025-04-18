const { getDB } = require('./mongo');
const sendPushNotification = require('./notifier');

async function startWatch() {
  const db = getDB();
  const collection = db.collection('Attendance');

  const changeStream = collection.watch();

  changeStream.on('change', async (change) => {
    try {
      if (change.operationType === 'update') {
        const userId = change.documentKey._id;
        const updated = change.updateDescription.updatedFields;

        console.log(updated)
        
        // Process all updated fields
        for (const key of Object.keys(updated)) {
          // Handle direct updates to existing entries
          const match = key.match(/^attendance\.(\d+)\.(\w+)\.(\d+)$/);
          console.log("match start!")
          console.log(match)
          
          if (match) {
              console.log("matched!")
              const [_, sem, subject, index] = match;
            const entry = updated[key];

            console.log(db, userId, entry, sem, subject);
            
            await notifyUser(db, userId, entry, sem, subject);
          }
          
          // Handle array push operations (if applicable)
          const arrayMatch = key.match(/^attendance\.(\d+)\.(\w+)$/);
          if (arrayMatch && Array.isArray(updated[key])) {
            const [_, sem, subject] = arrayMatch;
            const newEntries = updated[key];
            
            // The last entry is likely the newly added one
            if (newEntries.length > 0) {
              const latestEntry = newEntries[newEntries.length - 1];
              console.log("notify!")
              await notifyUser(db, userId, latestEntry, sem, subject);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error processing attendance change:', error);
    }
  });
  
  console.log('Attendance change stream watcher started');
}

async function notifyUser(db, userId, entry, sem, subject) {
  try {
    const user = await db.collection('users').findOne({ _id: userId });
    if (user?.expoPushToken) {
        console.log(user.expoPushToken)
      await sendPushNotification(user.expoPushToken, entry, sem, subject);
      console.log(`Notification sent to ${userId} for ${subject} (Sem ${sem})`);
    }
  } catch (error) {
    console.error(`Failed to notify user ${userId}:`, error);
  }
}

module.exports = startWatch;