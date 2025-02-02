from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os.path
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_gdrive_service():
    """Gets an authorized Google Drive service instance."""
    creds = None
    
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def upload_file(filename, mimetype='text/csv'):
    """Uploads a file to Google Drive and returns the file ID."""
    try:
        service = get_gdrive_service()
        
        file_metadata = {'name': os.path.basename(filename)}
        media = MediaFileUpload(filename, mimetype=mimetype, resumable=True)
        
        # Check if file already exists
        results = service.files().list(
            q=f"name='{file_metadata['name']}' and trashed=false",
            fields="files(id)").execute()
        existing_files = results.get('files', [])
        
        if existing_files:
            # Update existing file
            file_id = existing_files[0]['id']
            file = service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id').execute()
        else:
            # Create new file
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id').execute()
            
            # Make the file publicly readable
            service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()
        
        return file.get('id')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None 