!/bin/bash

# Define log file paths
CLOUDFLARED_LOG=$(mktemp)
PYTHON_LOG="/home/pi/python.log"

# Start cloudflared and write logs to file
cloudflared tunnel --url http://localhost:8000 > "$CLOUDFLARED_LOG" 2>&1 &
CLOUDFLARED_PID=$!
echo "Started cloudflared (PID $CLOUDFLARED_PID), logging to $CLOUDFLARED_LOG"

# Wait for the tunnel to start
sleep 30

# Extract public URL from the log
TUNNEL_URL=$(grep -o 'https://[a-z0-9.-]*\.trycloudflare\.com' "$CLOUDFLARED_LOG" | head -n 1)

# Send tunnel URL to your Render-hosted API
curl -X POST <add your server link and with post request url where update-url function is called(source of server is in attendance folder, server.py file)> \
 -H "Content-Type: application/json"
 -d "{\"url\": \"$TUNNEL_URL\"} "
echo "Sent tunnel URL: $TUNNEL_URL"

# Activate virtual environment
#source /home/pi/<path containg python virtual environment>/activate
cd /home/pi/<path/containg/python/virtual/environment>/activate
source bin/activate #set python virtual environment

# Go to project directory
cd <path/to/project/source/code>

# Run your Python script and log output
python amain.py >> "$PYTHON_LOG" 2>&1

#PYTHON_PID=$!
echo "Started amain.py (PID $PYTHON_PID), logging to $PYTHON_LOG"

# Let both processes run for 30 seconds
sleep 120 #camera will run for 2 minutes(120 sec)

# Kill both processes
kill $CLOUDFLARED_PID

#kill $PYTHON_PID
echo "Stopped cloudflared and amain.py"