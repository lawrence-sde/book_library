from fastapi import FastAPI
import app.database as database
from router import router  
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Create database engine
database.Base.metadata.create_all(bind=database.engine)

# Include the router
app.include_router(router)
