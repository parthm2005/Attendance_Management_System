const express = require('express');
const router = express.Router();
const { getDB } = require('../mongo');

router.post('/save-token', async (req, res) => {
  console.log("123")
  const { userId, expoToken } = req.body;
  console.log("userId")
  console.log(userId)
  console.log(expoToken)
  const db = getDB();

  await db.collection('users').updateOne(
    { _id: userId },
    { $set: { expoPushToken: expoToken } },
    { upsert: true }
  );

  res.status(200).json({ message: 'Token saved' });
});

module.exports = router;
