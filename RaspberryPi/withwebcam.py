import os
import json
import numpy as np
import face_recognition
import cv2
import threading
import time
from database.database import get_faces_from_local, get_collection
from utils.temp_storage import save_to_temp, send_data_to_mongodb
import matplotlib.pyplot as plt

# URL of the IP Webcam stream (change this!)
IP_CAMERA_URL = "http://192.168.97.110:8080/video" # add you webcam ip here

DATASET_PATH = "./processed_dataset"
ENCODINGS_PATH = "./encodings"

latest_frame = None
frame_lock = threading.Lock()

def capture_frames():
    """Continuously captures frames from IP Webcam."""
    global latest_frame
    cap = cv2.VideoCapture(IP_CAMERA_URL)

    if not cap.isOpened():
        print("❌ Could not open IP camera stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to grab frame from IP camera.")
            continue

        with frame_lock:
            latest_frame = frame

def preprocess_frame(frame):
    """Enhances frame quality using filters for better face recognition."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)

    # Convert back to RGB
    enhanced_frame = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)

    # Apply Bilateral Filtering to remove noise while keeping edges sharp
    filtered_frame = cv2.bilateralFilter(enhanced_frame, d=9, sigmaColor=75, sigmaSpace=75)

    return filtered_frame

flag_check = True

def encode_faces(division):
    global flag_check
    division_path = os.path.join(DATASET_PATH, division)
    encoding_file = os.path.join(ENCODINGS_PATH, f"{division}.json")
    os.makedirs(ENCODINGS_PATH, exist_ok=True)
    limit = 10
    count = 0

    if not os.path.isdir(division_path):
        print(f"❌ Division folder '{division}' not found.")
        return

    if os.path.exists(encoding_file):
        with open(encoding_file, "r") as f:
            existing_encodings = json.load(f)
    else:
        existing_encodings = {}

    person_encodings = existing_encodings.copy()

    for person_name in os.listdir(division_path):
        if count > limit:
            print(f"⚠️ Limit of {limit} persons exceeded")
            flag_check = False
            break

        if person_name in existing_encodings:
            print(f"⏭️ Skipping {person_name}, already encoded.")
            continue

        count += 1
        person_path = os.path.join(division_path, person_name)
        if not os.path.isdir(person_path):
            continue

        encodings = []
        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)
            image = face_recognition.load_image_file(img_path)
            face_encs = face_recognition.face_encodings(image)
            if face_encs:
                encodings.append(face_encs[0].tolist())
                print(f"✅ Encoded {img_name} for {person_name}")
            else:
                print(f"❌ No face found in {img_name}")

        if encodings:
            person_encodings[person_name] = encodings

    with open(encoding_file, "w") as f:
        json.dump(person_encodings, f, indent=2)
    print(f"💾 Saved local encodings to {encoding_file}")

def recognize_faces(teacher, division, subject, date, timing, semester):
    known_faces = get_faces_from_local(division)
    if not known_faces:
        print(f"❌ No encodings found for Division {division}.")
        return

    known_names = [face[0] for face in known_faces]
    known_encodings = [np.array(face[1]) for face in known_faces]

    framecount = 0
    recognition_count = {}
    cooldown_counter = {}
    confirmed_recognitions = set()
    accuracy_log = {}

    print("🎥 Starting recognition. Will run for 2 minutes or until Ctrl+C.")
    start_time = time.monotonic()
    duration_limit = 120  # seconds

    plt.ion()

    try:
        while True:
            if time.monotonic() - start_time >= duration_limit:
                print("⏱️ Time limit reached. Stopping recognition.")
                break

            with frame_lock:
                if latest_frame is None:
                    continue
                frame = latest_frame.copy()

            if framecount % 5 == 0:
                enhanced_frame = preprocess_frame(frame)
                rgb_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB)

                face_locations = face_recognition.face_locations(rgb_frame, model="hog")
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=1)

                current_frame_names = []

                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    name = "Unknown"

                    if face_distances[best_match_index] < 0.5:
                        name = known_names[best_match_index]
                        recognition_count[name] = recognition_count.get(name, 0) + 1
                        cooldown_counter[name] = 0

                        print(f"✅ Matched: {name}, Count: {recognition_count[name]}, Distance: {face_distances[best_match_index]:.4f}")

                        if name not in accuracy_log:
                            accuracy_log[name] = []
                        accuracy_log[name].append(face_distances[best_match_index])

                        if recognition_count[name] >= 10 and name not in confirmed_recognitions:
                            print(f"🎉 Confirmed: {name} recognized consistently.")
                            save_to_temp(name, division)
                            confirmed_recognitions.add(name)
                            recognition_count[name] = 10

                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, f"{name} ({face_distances[best_match_index]:.2f})",
                                (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    current_frame_names.append(name)

                for registered_name in list(recognition_count.keys()):
                    if registered_name not in confirmed_recognitions:
                        if registered_name not in current_frame_names:
                            cooldown_counter[registered_name] = cooldown_counter.get(registered_name, 0) + 1
                            if cooldown_counter[registered_name] >= 5:
                                recognition_count[registered_name] = 0
                                cooldown_counter[registered_name] = 0
                        else:
                            cooldown_counter[registered_name] = 0

                # Show frame using matplotlib
                plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                plt.axis("off")
                plt.title("Live Recognition (Close this window or press Ctrl+C to stop)")
                plt.pause(0.001)
                plt.clf()

            framecount += 1
            time.sleep(0.02)

    except KeyboardInterrupt:
        print("🛑 Ctrl+C pressed by user.")

    finally:
        print("💾 Saving data to MongoDB...")
        plt.ioff()
        plt.close()
        collection = get_collection(division)
        send_data_to_mongodb(collection, teacher, division, subject, date, timing, semester)

def handle_data(data):
    teacher = data['teacherName']
    division = data['division']
    subject = data['subject']
    date = data['date']
    timing = data['time']
    semester = data['semester']

    encode_faces(division)
    if flag_check:
        recognize_faces(teacher, division, subject, date, timing, semester)
    else:
        print("⚠️ Skipped recognition due to encoding limit.")

# Start frame capture in background
camera_thread = threading.Thread(target=capture_frames, daemon=True)
camera_thread.start()

# For testing purpose (remove or comment when integrating with actual frontend)
data = {"teacherName": "ChandraPrakash", "division": "B", "subject": "CS232", "date": "2025-04-23", "time": "10 AM", "semester": "4"}
handle_data(data)
