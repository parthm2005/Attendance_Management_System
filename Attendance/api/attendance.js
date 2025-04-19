import mongoose from 'mongoose';

const MONGO_URI = process.env.MONGO_URI;

if (!MONGO_URI) {
  throw new Error('MONGO_URI is not defined. Please set it properly.');
}

export default async function handler(req, res) {
  console.log("req.body"); // Log the request body
  console.log(req.body); // Log the request body
  const { student, subject, division } = req.body; // Use req.body instead of req.query

  if (!student || !subject || !division) {
    return res.status(400).json({ error: 'Missing required body parameters' });
  }

  try {
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect(MONGO_URI, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
      });
    }

    const collectionName = `${division.toUpperCase()}_attendance`; // Always uppercase division
    console.log('Using collection:', collectionName);

    const Attendance = mongoose.models[collectionName] || mongoose.model(
      collectionName,
      new mongoose.Schema({}, { strict: false }),
      collectionName
    );

    console.log("student", student);
    console.log("subject", subject);
    console.log("division", division);
    console.log("collectionName", collectionName);

    const records = await Attendance.find({
      subject: subject,
      students_present: student,
    });

    console.log('Request Body:', req.body);
    console.log('Fetched Records:', records);

    if (records.length === 0) {
      return res.status(404).json({ error: 'No attendance records found.' });
    }

    res.status(200).json(records);
  } catch (error) {
    console.error('Error occurred:', error);
    res.status(500).json({ error: 'Server Error', details: error.message });
  }
}