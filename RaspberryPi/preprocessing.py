import cv2
import face_recognition
import os
import numpy as np
from pathlib import Path
import random

def preprocess_faces(input_path="dataset/", output_path="processed_dataset/"):
    """Preprocesses faces by cropping and augmenting them."""
    Path(output_path).mkdir(parents=True, exist_ok=True)

    for person_name in os.listdir(input_path):
        person_path = os.path.join(input_path, person_name)
        processed_person_path = os.path.join(output_path, person_name)
        Path(processed_person_path).mkdir(parents=True, exist_ok=True)

        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)
            image = face_recognition.load_image_file(img_path)

            # Detect face locations
            face_locations = face_recognition.face_locations(image, model="hog")

            for i, (top, right, bottom, left) in enumerate(face_locations):
                # Crop the face from the image
                face_crop = image[top:bottom, left:right]

                # Apply data augmentation
                augmented_faces = augment_face(face_crop)

                # Save the original cropped face
                original_path = os.path.join(processed_person_path, f"{img_name}_cropped_{i}.jpg")
                cv2.imwrite(original_path, cv2.cvtColor(face_crop, cv2.COLOR_RGB2BGR))

                # Save augmented faces
                for j, aug_face in enumerate(augmented_faces):
                    aug_path = os.path.join(processed_person_path, f"{img_name}_aug_{i}_{j}.jpg")
                    cv2.imwrite(aug_path, cv2.cvtColor(aug_face, cv2.COLOR_RGB2BGR))

                print(f"✅ Processed {img_name}, Face {i} - Saved Augmented Versions")
    
    print("🎉 Preprocessing completed! Cropped and augmented faces saved.")

def augment_face(face_image):
    """Applies augmentation techniques to a cropped face."""
    augmentations = []

    # 1. Horizontal Flip (only if it doesn't distort the face)
    flip = cv2.flip(face_image, 1)
    if is_face_valid(flip):
        augmentations.append(flip)

    # 2. Random Rotation (within a reasonable range)
    for angle in [-10, 10]:  # Slight rotations
        (h, w) = face_image.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        rotated = cv2.warpAffine(face_image, M, (w, h))
        if is_face_valid(rotated):
            augmentations.append(rotated)

    # 3. Brightness Adjustment (not too dark or too bright)
    for factor in [0.9, 1.1]:  # Subtle changes
        brightness = cv2.convertScaleAbs(face_image, alpha=factor, beta=0)
        if is_face_valid(brightness):
            augmentations.append(brightness)

    # 4. Gaussian Blur (mild to preserve features)
    for kernel_size in [3]:
        blurred = cv2.GaussianBlur(face_image, (kernel_size, kernel_size), 0)
        if is_face_valid(blurred):
            augmentations.append(blurred)

    return augmentations

def is_face_valid(image):
    """Checks if the augmented image still contains a detectable face."""
    face_locations = face_recognition.face_locations(image, model="hog")
    return len(face_locations) > 0


if __name__ == "__main__":
    # Example usage
    preprocess_faces(input_path="dataset/", output_path="processed_dataset/")
    # Note: Ensure the dataset directory structure is correct before running.