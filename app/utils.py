from fastapi.params import Form
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse
from app.config import settings
from pathlib import Path
from app import schemas
import json
import requests

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM_NAME=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates" 
)


async def send_mail(mail_data: schemas.MailData) -> JSONResponse:

    message = MessageSchema(
        subject=mail_data.model_dump().get("subject"),
        recipients=mail_data.model_dump().get("emails"),
        template_body=mail_data.model_dump().get("body"),
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(
        message, template_name=mail_data.model_dump().get("template")
    )
    return JSONResponse(status_code=200, content={"message": "email has been sent"})


def convert_to_createCategorySchema(category:str = Form(...))->schemas.CategoryCreate:
    category_data= json.loads(category)
    return schemas.CategoryCreate(**category_data)

def convert_to_updateCategorySchema(category:str = Form(...))->schemas.CategoryUpdate:
    category_data= json.loads(category)
    return schemas.CategoryUpdate(**category_data)


def get_location_from_ip(ip: str):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        if data.get("status") == "success":
            return {
                "country": data.get("country"),
                "region": data.get("regionName"),
                "city": data.get("city"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
            }
    except Exception as e:
        pass
    return None
