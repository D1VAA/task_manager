from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()


def create_gdrive_file(file_name: str, file_path: str) -> str:
    drive = GoogleDrive(gauth)
    file = drive.CreateFile({"title": file_name})
    file.SetContentFile(file_path)
    file.Upload()
    return file["alternateLink"]
