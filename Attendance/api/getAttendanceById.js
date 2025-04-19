// /api/getAttendanceById.js
import mongoose from 'mongoose';
import dotenv from 'dotenv';
dotenv.config();
const MONGO_URI = process.env.MONGO_URI;
if (!MONGO_URI) {
  throw new Error('MONGO_URI is not defined. Please set it properly.');
}
// Define Student Schema
const attendanceSchema = new mongoose.Schema({
  _id: { type: String, required: true },
  attendance: {
    type: Map,
    of: new mongoose.Schema({
      type: Map,
      of: [
        {
          teacher: { type: String, required: true },
          date: { type: String, required: true },
          time: { type: String, required: true },
          status: { 
            type: String, 
            enum: ["present", "absent"], 
            required: true 
          }
        }
      ]
    })
  }
});
const Attendance = mongoose.models.Attendance || mongoose.model('Attendance', attendanceSchema, 'Attendance');
export default async function handler3(req, res) {


  res.setHeader('Access-Control-Allow-Origin', '*'); // allow all apps/websites
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Only POST method allowed' });
  }

  const { studentId, semester, subject } = req.body;
  console.log("Received request with:", { studentId, semester, subject });

  if (!studentId) {
    return res.status(400).json({ error: 'Missing studentId' });
  }

  try {
    // Ensure database connection
    if (mongoose.connection.readyState !== 1) {
      await mongoose.connect(MONGO_URI);
      console.log('Connected to MongoDB');
    }else if(mongoose.connection.readyState == 1){
       console.log("already connected")
    }

    const count = await Attendance.countDocuments();
    console.log("Total documents in collection:", count);

    const student = await Attendance.findOne({ _id: studentId });
    console.log("Database query result:", student);

    if (!student) {
      return res.status(404).json({ error: 'Student not found' });
    }

    if (semester && subject) {
      return res.status(200).json(student.attendance?.get(semester)?.get(subject) || []);
    } else if (semester) {
      return res.status(200).json(student.attendance?.get(semester) || {});
    } else {
      return res.status(200).json(student.attendance || {});
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Server error' });
  }
}
