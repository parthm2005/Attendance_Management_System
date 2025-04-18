# 🧠 AI-Based Attendance Management System using Face Recognition

A smart, automated, and contactless **Attendance Management System** built with **AI, Raspberry Pi, React Native, and Cloud Services** to streamline classroom attendance using face recognition.

> 🚀 Developed with the goal of improving accuracy and saving time in managing attendance — powered by HOG-based facial embeddings and real-time student detection.

---

## 📸 Project Highlights

- 🎯 Face Recognition using HOG embeddings
- 🤖 Raspberry Pi with Camera Module 3 for real-time student detection
- 📱 Two React Native apps — for students and teachers
- ☁️ Firebase Auth, MongoDB, Cloudinary, Flowise AI chatbot integration
- 🔒 Contactless and secure attendance marking, reports, and academic chatbot support

---

## 🧰 Tech Stack

**Frontend:** React Native  
**Backend:** Node.js, Express.js  
**AI/ML:** Python, face_recognition (HOG-based)
**Hardware:** Raspberry Pi 4, Camera Module 3  
**Auth:** Firebase Authentication  
**Storage:** Cloudinary (image), MongoDB (records)  
**Hosting:** Render, Cloudflare Tunneling  
**Chatbot:** Flowise (Gemini & Groq integration)

---

## 🔗 Resources

- 📊 [PPT Presentation](https://drive.google.com/file/d/1w-EfLw-9p_ZB5dFQ27CJZW27uu9GTGi_/)
- 🎥 [Demo Video]([https://youtu.be/MIksAG1sAJk](https://youtu.be/b00f7xp_1C4)

---

## ⚙️ Setup Instructions

### 🎛️ Raspberry Pi Setup

<details>
<summary>Click to expand Raspberry Pi Instructions</summary>

#### Part 1: Install Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Insert a 16GB+ SD card
3. In Imager:
   - Choose OS: Raspberry Pi OS (32-bit)
   - Choose Storage: Your SD card
   - Click ⚙️ (Advanced Options):
     - Enable SSH
     - Set Wi-Fi SSID & password
     - Set username & password
     - Choose timezone, locale
4. Click "Write" and wait
5. Insert SD into Pi and power it on

#### Part 2: Access Raspberry Pi

- Use `raspberrypi.local` in PuTTY or RealVNC if mDNS is enabled
- Or find Pi IP in your router admin panel

#### Part 3: SSH Access with PuTTY

- Hostname: `raspberrypi.local` or IP
- Port: `22`
- Login with username/password set earlier

#### Part 4: GUI Access via RealVNC

1. SSH into Pi and run:  
   `sudo raspi-config` → Interface Options → Enable VNC
2. Download [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/)
3. Connect with `raspberrypi.local` or Pi IP

#### Part 5: Update Raspberry Pi

```bash
sudo apt update
sudo apt upgrade -y
```

</details>

---

## 🔌 Deploying Code to Raspberry Pi

1. Place all required Python files and the Bash script on your Raspberry Pi.
2. Edit the Bash script with your:
   - Correct file paths
   - API URLs and keys
3. Make the Bash script executable:

```bash
chmod +x tunnel.sh
```

4. To run the script automatically on boot, refer to this guide:  
   [Run Bash Script on Startup – squash.io](https://www.squash.io/executing-bash-script-at-startup-in-ubuntu-linux/)  
   *(It works on Raspberry Pi OS as well since it’s Debian-based.)*
5. Ensure Raspberry Pi is connected to power and internet (via Wi-Fi or LAN).
6. That’s it! The script runs in the background. Once a teacher creates a session, the Pi handles recognition and attendance.

---

## 🧪 Python Script Overview

| File                     | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `amain.py`               | Master script that runs the complete pipeline                               |
| `encode_recognition_rpi.py` | Generates face encodings and starts Pi camera for real-time recognition |
| `fetch_images.py`        | Downloads student images from Cloudinary using Firebase authentication      |
| `fetch.py`               | Sets up server endpoint to receive and update attendance records            |
| `withwebcam.py`          | Script to test recognition using a connected USB webcam                     |
| `config.py`              | Contains environment variables like MongoDB URI                             |
| `encodings/`             | Stores facial encodings organized division-wise                             |
| `processed_dataset/`     | Stores processed face images downloaded from Cloudinary                     |
| `database/`              | Responsible for updating attendance in MongoDB after session ends           |

---

## 🌍 Backend Server Setup (Hosted on Render)

### 📁 `Notification/` Server

- Add your MongoDB URI to a `.env` file.
- Handles:
  - Attendance notification services
  - Report generation APIs for teachers

### 📁 `Attendance/` Server

- Add MongoDB URI in `.env`
- Responsible for:
  - Receiving Cloudflare public URL from Raspberry Pi
  - Fetching attendance records for students

> 📝 You may also combine both servers with small changes, and host them on the same domain.

---

## 👨‍🏫 Teacher App Setup (`Teacher_App/`)

1. Place your `firebaseConfig.json` in the `config/` folder.
2. Install dependencies:

```bash
npm install
```

3. Update the following URLs in source files:
   - `API_BASE_URL`: Your attendance server’s endpoint in `attendance.tsx`
   - `urlResponse`: Server endpoint for Pi URL sync in `mark-attend.tsx`

4. Build the app for Android using Expo EAS:

```bash
eas login
eas build:configure
eas build -p android --profile production
```

### Teacher App Workflow

- Register and verify email
- Set teaching department
- Choose subjects
- Schedule or start a session
- Generate attendance reports by subject and date

---

## 👨‍🎓 Student App Setup (`Student_App/`)

1. Place your `firebaseConfig.json` in the `config/` folder.
2. Install dependencies:

```bash
npm install
```

3. Update the following in the source:
   - `getAttendanceById` API in `attendance.tsx`
   - `CLOUDINARY_URL` and `UPLOAD_PRESET` in `profile.tsx`
   - Flowise API key in `chatbot.tsx`
   - Notification server URLs in `profile.tsx` and `hooks/useNotifications.tsx`
   - Update `app.json` as per inline comments

4. Build the app:

```bash
eas login
eas build:configure
eas build -p android --profile production
```

### Student App Workflow

- Register using institute email ID and verify
- App auto-fills degree, department, and semester
- Student selects division manually
- Capture face dataset from multiple angles
- View subject-wise, date-wise attendance in the app
- Chat with AI bot for academic help

---

## 🤖 Chatbot Setup with Flowise

1. Sign up / log in to [Flowise](https://flowiseai.com)
2. Create a new Chatflow and import the provided `.json` file
3. Add your:
   - Gemini API Key in the Gemini node
   - Groq API Key in the Groq node
4. Use Text Splitter nodes to upload your reference academic files
5. Click **"Preset"** to vectorize content for semantic search
6. Save and test the chatbot in the Flowise interface
7. Use the `</>` embed button (top-right) to get integration code

---

---


## 🙌 Team Credits

- **Nevil Vataliya** – Team Lead  
  🔗 [LinkedIn](https://www.linkedin.com/in/nevilvataliya) | 💻 [GitHub](https://github.com/nevilv123)

- **Prankit Vishwakarma**  
  🔗 [LinkedIn](https://www.linkedin.com/in/prankit-vishwakarma-b49246268/) | 💻 [GitHub](https://github.com/prank-vish)

- **Parth Modi**  
  🔗 [LinkedIn](https://www.linkedin.com/in/parth-modi-26208928a/) | 💻 [GitHub](https://github.com/parthm2005/)

- **Yash Jethva**  
  🔗 [LinkedIn](https://www.linkedin.com/in/yash-jethva-058336281/) | 💻 [GitHub](https://github.com/)

- **Charan Banda**  
  🔗 [LinkedIn](https://www.linkedin.com/in/charanbanda/) | 💻 [GitHub](https://github.com/)

- **Prof. Chandra Prakash** – Project Mentor  
  🎓 AI Professor at SVNIT Surat - [LinkedIn](https://www.linkedin.com/in/chandraprakash86/)

---

## 📬 Contact & Contributions

Feel free to open issues, fork the repo, or suggest improvements.

🔗 [Connect with me on LinkedIn](https://www.linkedin.com/in/nevilvataliya)

Always excited to collaborate on AI, IoT, or student-centric tech projects!
