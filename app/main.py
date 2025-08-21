from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
from app.config import settings
from app.routers import user, category, auth, product, refreshToken, order



app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(refreshToken.router) 
app.include_router(order.router)

# CORS config to fix later after completing the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cloudinary.config(
    cloud_name=settings.cloud_name,
    api_key=settings.api_key,
    api_secret=settings.api_secret,
)

@app.get("/")
def root() :
    return {"Hello pharma": "Welcome to the Pharma API"}