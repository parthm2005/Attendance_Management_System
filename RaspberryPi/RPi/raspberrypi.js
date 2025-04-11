const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

app.get('/',(req, res) => {
  res.json({ message: "Server Started!" });
})

app.post('/submit-data', (req, res) => {
  const { subject, teacherName, date, time, division } = req.body;
  
  // Process the data as needed
  console.log('Received data:', req.body);
  
  // You can store this in a database, display it, etc.
  
  res.json({ success: true, message: 'Data received successfully' });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});