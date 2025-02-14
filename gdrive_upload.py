from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os.path
import pickle
import logging
from datetime import datetime
from email_notifier import send_notification

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gdrive_upload.log'),
        logging.StreamHandler()
    ]
)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_gdrive_service():
    """Gets an authorized Google Drive service instance."""
    creds = None
    
    try:
        # Check if token.pickle exists
        if os.path.exists('token.pickle'):
            logging.info("Found existing token.pickle")
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        # Check if credentials are valid
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logging.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    error_msg = "credentials.json is required but not found"
                    logging.error(error_msg)
                    send_notification("Error", error_msg)
                    raise FileNotFoundError(error_msg)
                    
                logging.info("Getting new credentials")
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Save the credentials
            logging.info("Saving credentials to token.pickle")
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('drive', 'v3', credentials=creds)
    
    except Exception as e:
        error_msg = f"Error in get_gdrive_service: {str(e)}"
        logging.error(error_msg)
        send_notification("Error", error_msg)
        raise

def upload_file(filename, mimetype='text/csv'):
    """Uploads a file to Google Drive and returns the file ID."""
    if not os.path.exists(filename):
        error_msg = f"File not found: {filename}"
        logging.error(error_msg)
        send_notification("Error", error_msg)
        return None
        
    try:
        logging.info(f"Starting upload for file: {filename}")
        service = get_gdrive_service()
        
        file_metadata = {'name': os.path.basename(filename)}
        media = MediaFileUpload(filename, mimetype=mimetype, resumable=True)
        
        # Check if file already exists
        logging.info("Checking for existing file")
        results = service.files().list(
            q=f"name='{file_metadata['name']}' and trashed=false",
            fields="files(id)").execute()
        existing_files = results.get('files', [])
        
        if existing_files:
            # Update existing file
            file_id = existing_files[0]['id']
            logging.info(f"Updating existing file with ID: {file_id}")
            file = service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id').execute()
        else:
            # Create new file
            logging.info("Creating new file")
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id').execute()
            
            # Make the file publicly readable
            logging.info("Setting public read permissions")
            service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()
        
        file_id = file.get('id')
        success_msg = f"Upload successful. File ID: {file_id}"
        logging.info(success_msg)
        
        # Get log content
        with open('gdrive_upload.log', 'r') as log_file:
            log_content = log_file.read().strip()
        
        # Send success notification
        send_notification(
            "Success",
            f"File successfully uploaded to Google Drive.\nFile: {filename}\nFile ID: {file_id}\nPublic URL: https://drive.google.com/uc?export=download&id={file_id}",
            log_content
        )
        
        return file_id
        
    except Exception as e:
        error_msg = f"Upload failed: {str(e)}"
        logging.error(error_msg)
        
        # Get log content
        with open('gdrive_upload.log', 'r') as log_file:
            log_content = log_file.read().strip()
        
        # Send error notification
        send_notification("Error", error_msg, log_content)
        return None 