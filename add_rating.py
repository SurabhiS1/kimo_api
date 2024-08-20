from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["course_db"]
courses_collection = db["courses"]

# Update each course document
for course in courses_collection.find():
    updated_chapters = []
    for chapter in course["chapters"]:
        # Add ratings field if it doesn't exist
        if "ratings" not in chapter:
            chapter["ratings"] = {"positive": 0, "negative": 0}
        updated_chapters.append(chapter)
    
    # Update the document in the database
    courses_collection.update_one(
        {"_id": course["_id"]},
        {"$set": {"chapters": updated_chapters}}
    )

print("Schema updated successfully!")
