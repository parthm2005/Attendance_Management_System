#!/usr/bin/env python3
import os
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from datetime import datetime
import argparse
import logging

class CloudinaryFirebaseDownloader:
    def __init__(self, credentials_path, download_dir=None):
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("image_downloader.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("CloudinaryDownloader")
        
        # Degree mapping based on first character of email username
        self.degree_mapping = {
            'u': 'B.Tech',
            'p': 'M.Tech',
            'i': 'Integrated',
            'm': 'MBA',
            'd': 'Ph.D'
        }
        
        # Initialize Firebase
        try:
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            # print(self.db.data())
            # print(self.db)
            # print("self.db")
            self.logger.info("Firebase connection initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {e}")
            raise
        
        # Set download directory
        if download_dir:
            self.download_dir = download_dir
        else:
            self.download_dir = os.path.join(os.path.expanduser("~"), "cloudinary_images")
        
        # Create download directory if it doesn't exist
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            self.logger.info(f"Created download directory: {self.download_dir}")
    
    def parse_email_for_path(self, email):
        """
        Parse email address to extract path components for user document
        
        Args:
            email (str): User's email address
            
        Returns:
            dict: Dictionary containing college, degree, department, and batch
        """
        try:
            if not email or '@' not in email:
                self.logger.warning(f"Invalid email format: {email}")
                return None
                
            # Extract username and domain parts
            username, domain = email.split('@')
            
            # Extract college from domain (last part of domain)
            domain_parts = domain.split('.')

            college = domain.split(".")[1]

            print("clg")
            print(college)

            # college = "svnit"  # Default
            # for part in domain_parts:
            #     if part == "svnit":
            #         college = part
            #         break
            
            # Extract degree from first character of username
            first_char = username[0].lower()
            degree = self.degree_mapping.get(first_char)
            if not degree:
                self.logger.warning(f"Unknown degree code in email: {first_char}")
                return None
                
            # Extract department code (characters after first char and before numbers)
            department = ""
            i = 1
            while i < len(username) and not username[i].isdigit():
                department += username[i]
                i += 1
                
            if not department and i < len(username):
                # If we didn't find department before numbers, try to extract after numbers
                digits_end = i
                while digits_end < len(username) and username[digits_end].isdigit():
                    digits_end += 1
                department = username[digits_end:digits_end+2]
            
            # Extract batch year from first two digits
            batch = ""
            for char in username:
                if char.isdigit():
                    batch += char
                    if len(batch) == 2:
                        break
            
            # Convert 2-digit year to 4-digit year
            if len(batch) == 2:
                batch = "20" + batch
                
            return {
                "college": college,
                "degree": degree,
                "department": department,
                "batch": batch
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing email {email}: {e}")
            return None
    
    def find_user_by_id(self, user_id):
        """
        Find a user document by extracting path components from email in dataset
        
        Args:
            user_id (str): Firebase user ID
        
        Returns:
            dict: User document data if found, None otherwise
        """
        try:
            # First check if user exists in datasets and get their email
            dataset_path = f"datasets/{user_id}"
            dataset_images = self.db.collection(f"{dataset_path}/images").limit(1).stream()
            
            email = None
            for image_doc in dataset_images:
                image_data = image_doc.to_dict()
                if 'email' in image_data:
                    email = image_data['email']
                    self.logger.info(f"Found email {email} for user {user_id}")
                    break
            
            if not email:
                self.logger.warning(f"No email found for user {user_id}")
                return None
                
            # Parse email to get path components
            path_info = self.parse_email_for_path(email)
            if not path_info:
                self.logger.warning(f"Could not parse path info from email {email}")
                return None
                
            # Construct the user document path
            user_path = f"users/{path_info['college']}/{path_info['degree']}/{path_info['department']}/{path_info['batch']}/{user_id}"
            self.logger.info(f"Constructed user path: {user_path}")
            
            # Get the user document
            user_doc = self.db.document(user_path).get()
            
            if user_doc.exists:
                self.logger.info(f"Found user {user_id} at path: {user_path}")
                return user_doc.to_dict()
            else:
                self.logger.warning(f"User document not found at path: {user_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in find_user_by_id for {user_id}: {e}")
            return None
    
    def get_collection_name(self, depth):
       
        # We're not using specific collection names, just traversing
        return ""
    
    def get_all_users_ids(self):
        """
        Get all user IDs by traversing the nested structure
        This helps identify which users have images in the database
        """
        try:
            user_ids = set()
            
            # Get datasets collection which contains user IDs directly
            datasets_ref = self.db.collection("datasets")
            user_collections = list(datasets_ref.list_documents())
            
            for user_ref in user_collections:
                user_ids.add(user_ref.id)
                self.logger.info(f"Found user ID in datasets: {user_ref.id}")
            
            self.logger.info(f"Found {len(user_ids)} total users in datasets collection")
            return user_ids
            
        except Exception as e:
            self.logger.error(f"Error getting all user IDs: {e}")
            return set()
    
    def download_user_images(self, user_id):
       
        # Retrieve the user data using the email-based path
        try:
            user_data = self.find_user_by_id(user_id)
            if not user_data:
                self.logger.error(f"User document for {user_id} does not exist")
                # Use default values if we can't find the user
                division = "unknown"
                folder_no = user_id  # Use the user ID as folder name
            else:
                # Extract 'division' and 'no' fields
                division = user_data.get('division', 'unknown')
                folder_no = user_data.get('no', user_id)
                
            # Show what we found
            self.logger.info(f"Using division: {division}, folder_no: {folder_no} for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve user data for {user_id}: {e}")
            division = "unknown"
            folder_no = user_id
        
        # Create directory using the 'division' and 'no' fields
        user_dir = os.path.join(self.download_dir, division, folder_no)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            self.logger.info(f"Created directory for user {user_id}: {user_dir}")
        
        # Get all image documents for the user
        images_ref = self.db.collection(f"datasets/{user_id}/images")
        
        try:
            images = list(images_ref.stream())
            self.logger.info(f"Found {len(images)} images for user {user_id}")
        except Exception as e:
            self.logger.error(f"Error retrieving images for {user_id}: {e}")
            return 0
        
        download_count = 0
        for image in images:
            image_data = image.to_dict()
            
            if 'imageUrl' not in image_data:
                self.logger.warning(f"Image document {image.id} has no imageUrl field")
                continue
            
            image_url = image_data['imageUrl']
            public_id = image_data.get('publicId', 'unknown')
            timestamp = image_data.get('timestamp', datetime.now())
            
            # Log the image data we found
            self.logger.info(f"Image data: {image_data}")
            
            # Convert Firestore timestamp to datetime if needed
            if hasattr(timestamp, 'seconds'):
                timestamp = datetime.fromtimestamp(timestamp.seconds)
            
            # Create filename using public_id and timestamp
            formatted_time = timestamp.strftime('%Y%m%d_%H%M%S')
            filename = f"{public_id}_{formatted_time}.jpg"
            filepath = os.path.join(user_dir, filename)
            
            # Check if the file already exists
            if os.path.exists(filepath):
                self.logger.info(f"Image already exists, skipping download: {filepath}")
                download_count += 1
                continue
                
            # Download the image
            try:
                response = requests.get(image_url, stream=True)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.logger.info(f"Downloaded image: {filepath}")
                download_count += 1
                
            except Exception as e:
                self.logger.error(f"Failed to download image {image_url}: {e}")
            
        self.logger.info(f"Downloaded {download_count} images for user {user_id}")
        return download_count
    
    def download_all_users_images(self):
        """
        Download images for all users in the database
        
        Returns:
            dict: Dictionary with user IDs as keys and number of downloads as values
        """
        results = {}
        
        # Get all dataset collections
        datasets_ref = self.db.collection("datasets")
        user_collections = datasets_ref.list_documents()
        # print("datasets_ref")
        # print(datasets_ref)
        # print("user_collections")
        # print(user_collections)
        
        for user_ref in user_collections:
            user_id = user_ref.id
            # print("user_ref")
            # print(user_ref)
            # print("user_id")
            # print(user_id)
            self.logger.info(f"Processing user: {user_id}")
            download_count = self.download_user_images(user_id)
            results[user_id] = download_count
        
        return results

    def get_sub_collections(self, doc_path):
       
        try:
            doc_ref = self.db.document(doc_path)
            collections = doc_ref.collections()
            collection_ids = [col.id for col in collections]
            self.logger.info(f"Sub-collections for {doc_path}: {collection_ids}")
            return collection_ids
        except Exception as e:
            self.logger.error(f"Error retrieving sub-collections for {doc_path}: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Download Cloudinary images from Firebase Firestore')
    # parser.add_argument('--creds', required=True, help='Path to Firebase service account credentials JSON')
    # parser.add_argument('--user', help='Specific user ID to download images for')
    # parser.add_argument('--output', help='Output directory for downloaded images')
    args = parser.parse_args()
    
    creds = '<your file>.json' # add your json file of firebase
    output = 'processed_dataset' # folder where images are being stored
    
    try:
        downloader = CloudinaryFirebaseDownloader(creds, output)
       
        # Download images for all users
        results = downloader.download_all_users_images()
        total = sum(results.values())
        # print(f"Downloaded {total} images for {len(results)} users")
        
        
    except Exception as e:
        # print(f"Error: {e}")
        return 1
    
    return 0

# if __name__ == "__main__":
#   exit(main())
