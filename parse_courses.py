import json
from pymongo import MongoClient

# Load courses from JSON file
with open('courses.json') as f:
    courses = json.load(f)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["course_db"]
courses_collection = db["courses"]

# Insert courses into MongoDB
courses_collection.insert_many(courses)
print("Courses inserted successfully!")
