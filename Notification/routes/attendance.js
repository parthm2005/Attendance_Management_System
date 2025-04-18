const express = require('express');
const router = express.Router();
const { getDB } = require('../mongo');

/**
 * Get attendance report based on provided criteria
 */
router.post('/getAttendanceReport', async (req, res) => {
  try {
    const { subject, startDate, endDate, studentIds, semester, division } = req.body;

    // Validate required parameters
    if (!subject) {
      return res.status(400).json({ error: 'Subject code is required' });
    }

    if (!startDate || !endDate) {
      return res.status(400).json({ error: 'Date range is required' });
    }

    if (!studentIds?.length && !semester) {
      return res.status(400).json({ error: 'Either student IDs or semester must be provided' });
    }

    const db = getDB();
    let query = {};

    // Build query based on filters
    if (studentIds && studentIds.length > 0) {
      query._id = { $in: studentIds };
    } else if (semester) {
      query[`attendance.${semester}`] = { $exists: true };
    }

    console.log("Query:", JSON.stringify(query));

    // Get students matching the query
    const students = await db.collection('Attendance').find(query).toArray();
    console.log(`Found ${students.length} students matching query`);

    if (!students || students.length === 0) {
      return res.status(200).json([]);
    }

    // Convert date strings to Date objects once for efficiency
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    console.log(`Date range: ${start.toISOString()} to ${end.toISOString()}`);
    
    // For each student, get their attendance records and process them
    const attendanceData = students.map(student => {
      // Access the attendance array for this semester and subject
      const attendanceArray = student.attendance?.[semester]?.[subject];
      
      if (!attendanceArray || !Array.isArray(attendanceArray)) {
        console.log(`No attendance records found for student ${student._id}, semester ${semester}, subject ${subject}`);
        
        // Return student with empty records
        const studentInfo = parseStudentId(student._id);
        return {
          studentId: student._id,
          name: student.name || 'Unknown',
          degree: studentInfo.degree,
          department: studentInfo.department,
          year: studentInfo.year,
          rollNumber: studentInfo.rollNumber,
          attendanceRecords: [],
          statistics: { totalClasses: 0, present: 0, absent: 0, percentage: 0 }
        };
      }
      console.log(attendanceArray)
      
      console.log(`Found ${attendanceArray.length} raw attendance records for student ${student._id}`);
      
      // Filter records by date range
      const filteredRecords = [];
      
      for (const record of attendanceArray) {
        if (!record.date) continue;
        
        try {
          // Try to parse the date - simplified approach
          const recordDate = new Date(record.date);
          
          // Check if the date is valid
          if (isNaN(recordDate.getTime())) {
            console.warn(`Invalid date format in record: ${record.date}`);
            continue;
          }
          
          // Compare just the date part (ignoring time)
          if (recordDate >= start && recordDate <= end) {
            filteredRecords.push(record);
          }
        } catch (error) {
          console.error(`Error processing record date ${record.date}:`, error);
        }
      }
      
      console.log(`After date filtering: ${filteredRecords.length} records remain for student ${student._id}`);

      // Parse student ID to get additional information
      const studentInfo = parseStudentId(student._id);

      // Calculate attendance statistics from filtered records
      const stats = calculateAttendanceStats(filteredRecords);
      console.log(`Attendance stats for ${student._id}: ${JSON.stringify(stats)}`);

      return {
        studentId: student._id,
        name: student.name || 'Unknown',
        degree: studentInfo.degree,
        department: studentInfo.department,
        year: studentInfo.year,
        rollNumber: studentInfo.rollNumber,
        attendanceRecords: filteredRecords,
        statistics: stats
      };
    });

    res.status(200).json(attendanceData);
  } catch (error) {
    console.error('Error getting attendance report:', error);
    res.status(500).json({ error: 'Failed to retrieve attendance data' });
  }
});

/**
 * Get detailed attendance for a specific student and subject
 */
router.post('/getAttendanceById', async (req, res) => {
  try {
    const { studentId, semester, subject } = req.body;

    if (!studentId || !semester || !subject) {
      return res.status(400).json({ error: 'Student ID, semester and subject are required' });
    }

    const db = getDB();
    const student = await db.collection('Attendance').findOne({ _id: studentId });

    if (!student) {
      return res.status(404).json({ error: 'Student not found' });
    }

    const attendance = student.attendance?.[semester]?.[subject] || [];
    console.log(`Found ${attendance.length} attendance records for ${studentId}, semester ${semester}, subject ${subject}`);

    // Parse student ID to get additional information
    const studentInfo = parseStudentId(studentId);

    // Calculate attendance statistics
    const stats = calculateAttendanceStats(attendance);

    res.status(200).json({
      studentId,
      // name: student.name || 'Unknown',
      degree: studentInfo.degree,
      department: studentInfo.department,
      year: studentInfo.year,
      rollNumber: studentInfo.rollNumber,
      attendance,
      subject,
      semester,
      statistics: stats,
    });
  } catch (error) {
    console.error('Error getting student attendance details:', error);
    res.status(500).json({ error: 'Failed to retrieve student attendance data' });
  }
});

// Helper functions for parsing student IDs and attendance data
function parseStudentId(id) {
  if (!id || typeof id !== 'string') return {};

  const degreeMap = {
    'u': "B.Tech",
    'p': "M.Tech",
    'i': "Integrated",
    'm': "MBA",
    'd': "Ph.D",
  };

  const departmentMap = {
    'cs': "Computer Science and Engineering",
    'ai': "Artificial Intelligence",
    'ec': "Electrical Engineering",
    'me': "Mechanical Engineering",
    'ce': "Civil Engineering",
  };

  const degree = degreeMap[id.charAt(0).toLowerCase()] || 'Unknown';
  const year = '20' + id.substring(1, 3);
  const deptCode = id.substring(3, 5).toLowerCase();
  const department = departmentMap[deptCode] || 'Unknown';
  const rollNumber = id.substring(5);

  return { degree, year, department, rollNumber };
}

function parseAttendanceDate(dateStr) {
  if (!dateStr) return null;

  try {
    // First try direct parsing (should work for YYYY-MM-DD format)
    const directDate = new Date(dateStr);
    if (!isNaN(directDate.getTime())) {
      return directDate;
    }
    
    // Otherwise try to parse as YY-MM-DD
    const parts = dateStr.split('-');
    if (parts.length === 3) {
      // Make sure all parts are numbers
      const year = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10) - 1; // JS months are 0-indexed
      const day = parseInt(parts[2], 10);
      
      // Determine century (20xx for years < 50, 19xx otherwise)
      const fullYear = year < 50 ? 2000 + year : 1900 + year;
      
      return new Date(fullYear, month, day);
    }
    
    console.warn(`Unrecognized date format: ${dateStr}`);
    return null;
  } catch (error) {
    console.error(`Error parsing date ${dateStr}:`, error);
    return null;
  }
}

function calculateAttendanceStats(records) {
  if (!records || !Array.isArray(records)) {
    return { totalClasses: 0, present: 0, absent: 0, percentage: 0 };
  }

  const totalClasses = records.length;
  const presentCount = records.filter(record => 
    record.status && record.status.toLowerCase() === 'present'
  ).length;
  const absentCount = totalClasses - presentCount;
  const percentage = totalClasses > 0 ? (presentCount / totalClasses) * 100 : 0;

  return {
    totalClasses,
    present: presentCount,
    absent: absentCount,
    percentage: Math.round(percentage * 100) / 100
  };
}

module.exports = router;
