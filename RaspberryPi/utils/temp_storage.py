import json
import atexit

TEMP_FILE = "recognized_faces.json"
from config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME, COLLECTION_ENCODING
collection = COLLECTION_NAME # Placeholder for MongoDB collection
from database.database import get_collection

def save_to_temp(name, division):
    """Saves recognized name and division to a temporary file."""
    try:
        with open(TEMP_FILE, "r") as file:
            recognized_faces = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        recognized_faces = []

    recognized_faces.append({
        "name": name,
        "division": division
    })

    with open(TEMP_FILE, "w") as file:
        json.dump(recognized_faces, file, indent=2)
        
import json
def send_data_to_mongodb(collection, teacher, division, subject, date, time, semester):
    try:
        with open(TEMP_FILE, "r") as file:
            recognized_faces = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        recognized_faces = []
    
    try:
        with open(f"encodings/{division}.json", "r") as file:
            encodings_data = json.load(file)
        all_students = list(encodings_data.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        all_students = []
    
    filtered_faces = [face for face in recognized_faces if face.get("division") == division]
    students_present = list({face["name"] for face in filtered_faces})
    
    db_collection = get_collection(collection)
    
    try:
        with open(TEMP_FILE, "w") as file:
            file.write("")
        print("tempfile cleaned")
            
    except (FileNotFoundError, json.JSONDecodeError):
        print("unable to open")
    
    for student in all_students:
        status = "present" if student in students_present else "absent"
        
        # Check if student document exists
        student_doc = db_collection.find_one({"_id": student})
        
        if not student_doc:
            # Insert new document for student with _id as student name
            db_collection.insert_one({
                "_id": student,
                "attendance": {
                    semester: {
                        subject: [
                            {
                                "teacher": teacher,
                                "date": date,
                                "time": time,
                                "status": status
                            }
                        ]
                    }
                }
            })
        else:
            # Update nested structure for existing student
            update_query = {
                f"attendance.{semester}.{subject}": {
                    "$each": [{
                        "teacher": teacher,
                        "date": date,
                        "time": time,
                        "status": status
                    }]
                }
            }
            db_collection.update_one(
                {"_id": student},
                {"$push": update_query}
            )
    
    print("Attendance updated successfully.")
