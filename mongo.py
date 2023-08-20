from pymongo import MongoClient
from config import MONGO_DB_URL
from pymongo.errors import ServerSelectionTimeoutError
import asyncio
import sys 
from motor import motor_asyncio

MONGO_PORT = 27017
MONGO_DB = "BuildYourHaremBot"

mclient = MongoClient()
mclient = MongoClient(MONGO_DB_URL,MONGO_PORT)[MONGO_DB]
motor = motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL, MONGO_PORT)
db = motor[MONGO_DB]
db = mclient["BYH"]
try:
  asyncio.get_event_loop().run_until_complete(motor.server_info())
except ServerSelectionTimeoutError:
  print("Can't connect to mongodb! Exiting...")

