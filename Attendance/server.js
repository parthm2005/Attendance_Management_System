import express from 'express';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import handler from './api/attendance.js';
import handler3 from './api/getAttendanceById.js';
import cors from 'cors';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;
let currentURL = "";

app.use(cors());
app.use(express.json());

app.post('/api/attendance', handler);
app.post('/api/getAttendanceById', handler3);


app.post("/api/update-url", (req, res) => {
  const { url } = req.body;
  if (url && url.startsWith("https://")) {
    currentURL = url;
    return res.json({ message: "URL updated", url });
  }
  res.status(400).json({ message: "Invalid URL" });
});

app.get("/api/get-url", (req, res) => {
  if (currentURL) {
    return res.json({ url: currentURL });
  }
  res.status(404).json({ message: "No URL available" });
});

app.get('/', (req, res) => {
  res.send('Welcome to the Attendance API');
});

mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
}).then(() => {
  app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
  });
}).catch((error) => {
  console.error('Error connecting to MongoDB', error);
});
