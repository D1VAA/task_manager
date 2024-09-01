import uvicorn
from fastapi import FastAPI, Form, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from utils.imports import Optional
from pydantic import BaseModel, Field
import os
import tempfile
import redis
from freight_database.get_env import REDIS_PASSWORD, REDIS_URL

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

assert REDIS_PASSWORD is not None, "REDIS_URL cannot be None"
assert REDIS_URL is not None, "REDIS_URL cannot be None"
redis_client = redis.Redis(host=REDIS_URL, port=18955, password=REDIS_PASSWORD)


def authenticate() -> GoogleDrive:
    try:
        creds_path = f"{os.getcwd()}/src/mycreds.txt"
        gauth = GoogleAuth()
        creds = redis_client.get("gdrive_credentials")
        if creds:
            with open(creds_path, "wb") as creds_file:
                creds_file.write(creds)
            gauth.LoadCredentialsFile(creds_path)
        else:
            gauth.LocalWebserverAuth()
            gauth.SaveCredentialsFile(creds_path)
            with open(creds_path, "rb") as creds_file:
                redis_client.set("gdrive_credentials", creds_file.read())
        return GoogleDrive(gauth)

    except Exception as e:
        raise ValueError("Error while Authenticating...", e)


async def create_freight(filename, file_content: bytes):
    drive = authenticate()

    async def uploadFile(temp_file_path):
        file_drive = drive.CreateFile({"title": filename})
        file_drive.SetContentFile(temp_file_path)
        file_drive.Upload()
        return file_drive["alternateLink"]

    try:
        if file_content:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file.flush()
                temp_file_path = temp_file.name

            file_link = await uploadFile(temp_file_path)
            return {"message": "File upload succesfully.",
                    "file_link": file_link}
        else:
            return {"message": "No file uploaded."}
    except Exception as e:
        print("An error occurred: ", e)

    finally:
        os.remove(temp_file_path)


class FreightData(BaseModel):
    origem: Optional[str] = Field(..., alias="origem")
    destino: Optional[str] = Field(..., alias="destino")
    cliente: Optional[str] = Field(..., alias="cliente")
    valorMercadoria: Optional[float] = Field(..., alias="valorMercadoria")
    custoVeiculo: Optional[float] = Field(..., alias="custoVeiculo")
    peso: Optional[float] = Field(..., alias="peso")
    adValorem: Optional[float] = Field(..., alias="adValorem")


@app.post("/freights", status_code=200)
async def api_upload_freight(
    origem: str = Form(...),
    destino: str = Form(...),
    cliente: str = Form(...),
    valorMercadoria: Optional[float] = Form(None),
    custoVeiculo: Optional[float] = Form(None),
    peso: Optional[float] = Form(None),
    adValorem: Optional[float] = Form(None),
    file: UploadFile = File(...),
):
    """
    Método na API para consultar um frete da database.
    """
    FreightData(
        origem=origem,
        destino=destino,
        cliente=cliente,
        valorMercadoria=valorMercadoria,
        custoVeiculo=custoVeiculo,
        peso=peso,
        adValorem=adValorem,
    )
    try:
        file_content = await file.read()
        msg = await create_freight(file.filename, file_content)
        print(msg)

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading the freight: {str(e)}",
        )


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=9999, reload=True)
