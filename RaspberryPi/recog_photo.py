# import cv2
# import face_recognition
# import os
# import pickle
# import numpy as np
# from database import create_db, store_face, get_faces  # Import database functions

# # Encode faces and store them in the database
# def encode_faces(dataset_path="processed_dataset/"):
#     """Encodes all faces from the dataset and stores them in the database."""
#     create_db()  # Ensure the database exists

#     # Get already stored encodings from the database
#     stored_faces = get_faces()
#     stored_names = {name for name, _ in stored_faces}  # Set of names already in DB

#     for person_name in os.listdir(dataset_path):
#         person_path = os.path.join(dataset_path, person_name)

#         if person_name in stored_names:
#             print(f"🔄 Skipping {person_name}, already encoded.")
#             continue  # Skip already encoded people

#         for img_name in os.listdir(person_path):
#             img_path = os.path.join(person_path, img_name)
#             image = face_recognition.load_image_file(img_path)
#             face_locations = face_recognition.face_locations(image, model="hog")
#             face_encodings = face_recognition.face_encodings(image, face_locations)
           
#             if face_encodings:
#                 encoding = face_encodings[0]  # Take the first detected face
#                 store_face(person_name, encoding)  # Store only new faces
#                 print(f"✅ Stored encoding for {person_name}")
#             else:
#                 print(f"❌ No encoding generated for image {img_name}")
#     print("🎉 Encoding process completed! Only new faces were added.")

# def recognize_faces(photo_path):
#     """Recognizes faces from a given photo."""
#     known_faces = get_faces()  # Load all stored face encodings from the database
#     if not known_faces:
#         print("❌ No encoded faces found! Run encode_faces() first.")
#         return

#     known_names = [face[0] for face in known_faces]  # Extract names
#     known_encodings = [face[1] for face in known_faces]  # Extract encodings

#     # Load the given photo
#     image = cv2.imread(photo_path)
#     if image is None:
#         print(f"❌ Failed to load image from {photo_path}.")
#         return

#     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     face_locations = face_recognition.face_locations(rgb_image)
#     face_encodings = face_recognition.face_encodings(rgb_image, face_locations, num_jitters=1, model="small")

#     for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#         matches = face_recognition.compare_faces(known_encodings, face_encoding)
#         face_distances = face_recognition.face_distance(known_encodings, face_encoding)

#         best_match_index = np.argmin(face_distances)
#         name = "Unknown"

#         if matches[best_match_index] and face_distances[best_match_index] < 0.5:
#             name = known_names[best_match_index]
#             print(f"✅ Matched: {name} (Distance: {face_distances[best_match_index]:.4f})")

#         # Display result on the image
#         cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
#         cv2.putText(image, f"{name} ({face_distances[best_match_index]:.2f})",
#                     (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#     # Display the final image with recognized faces
#     cv2.imshow("Face Recognition from Photo", image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     print("🛠 Encoding faces from dataset...")
#     encode_faces()  # First, encode faces and store them
#     print("✅ Encoding completed. Starting real-time recognition...")
#     # recognize_faces("path_to_your_photo.jpg")  # Uncomment to test with a specific photo
#     path="checkdata/img9.jpeg"
#     recognize_faces(path)  # Then, start face recognition


import cv2
import face_recognition
import os
import pickle
import numpy as np
from database import create_db, store_face, get_faces  # Import database functions

# Encode faces and store them in the database
def encode_faces(dataset_path="processed_dataset/"):
    """Encodes all faces from the dataset and stores them in the database."""
    create_db()  # Ensure the database exists

    # Get already stored encodings from the database
    stored_faces = get_faces()
    stored_names = {name for name, _ in stored_faces}  # Set of names already in DB

    for person_name in os.listdir(dataset_path):
        person_path = os.path.join(dataset_path, person_name)

        if person_name in stored_names:
            print(f"🔄 Skipping {person_name}, already encoded.")
            continue  # Skip already encoded people

        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)
            image = face_recognition.load_image_file(img_path)
            face_locations = face_recognition.face_locations(image, model="hog")
            face_encodings = face_recognition.face_encodings(image, face_locations)

            if face_encodings:
                encoding = face_encodings[0]  # Take the first detected face
                store_face(person_name, encoding)  # Store only new faces
                print(f"✅ Stored encoding for {person_name}")
            else:
                print(f"❌ No encoding generated for image {img_name}")
    print("🎉 Encoding process completed! Only new faces were added.")

def recognize_faces_from_video(video_path):
    """Recognizes faces from a given video."""
    known_faces = get_faces()  # Load all stored face encodings from the database
    if not known_faces:
        print("❌ No encoded faces found! Run encode_faces() first.")
        return

    known_names = [face[0] for face in known_faces]  # Extract names
    known_encodings = [face[1] for face in known_faces]  # Extract encodings

    # Open the given video file
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print(f"❌ Failed to load video from {video_path}.")
        return

    framecount = 0
    recognition_count = {}  # Dictionary to track frame count for each person
    confirmed_recognitions = set()  # Set to keep track of already saved names

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("🔄 End of video or error reading frame.")
            break

        if framecount % 5 == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=1, model="small")

            current_frame_names = []  # Track names in the current frame

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)

                best_match_index = np.argmin(face_distances)
                name = "Unknown"

                if matches[best_match_index] and face_distances[best_match_index] < 0.5:
                    name = known_names[best_match_index]

                    # Increment the count for this person or initialize it
                    recognition_count[name] = recognition_count.get(name, 0) + 1
                    print(f"✅ Matched: {name}, Count: {recognition_count[name]}, Distance: {face_distances[best_match_index]:.4f}")

                    # Save to file if confirmed and not already saved
                    if recognition_count[name] >= 10 and name not in confirmed_recognitions:
                        print(f"✅ Confirmed: {name} recognized consistently for 10 frames.")
                        with open("recognized_names.txt", "a") as file:
                            file.write(f"{name}\n")
                        confirmed_recognitions.add(name)

                # Display result on screen
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"{name} ({face_distances[best_match_index]:.2f})",
                            (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Add to the current frame names list
                current_frame_names.append(name)

            # Reset the recognition count for names not seen in the current frame
            for registered_name in list(recognition_count.keys()):
                if registered_name not in current_frame_names:
                    recognition_count[registered_name] = 0

            cv2.imshow("Face Recognition from Video", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        framecount += 1

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("🛠 Encoding faces from dataset...")
    encode_faces()  # First, encode faces and store them
    print("✅ Encoding completed. Starting video recognition...")
    video_path = "checkdata/vid1.mp4"  # Replace with your video file path
    recognize_faces_from_video(video_path)  # Then, start face recognition from video
