from fastapi import FastAPI, Query
from pymongo import MongoClient, ASCENDING, DESCENDING
from typing import List, Optional
from fastapi import HTTPException
from bson import ObjectId

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["course_db"]
courses_collection = db["courses"]

def convert_object_id(course):
    course["_id"] = str(course["_id"])
    return course

def aggregate_ratings(course):
    """Calculate the total rating for a course."""
    for chapter in course.get("chapters", []):
        positive = chapter.get("ratings", {}).get("positive", 0)
        negative = chapter.get("ratings", {}).get("negative", 0)
        if "total_rating" not in course:
            course["total_rating"] = 0
        course["total_rating"] += positive - negative
    return course

# Endpoint to get a list of all available courses
@app.get("/courses")
async def get_courses(
    sort_by: str = Query("alphabetical", enum=["alphabetical", "date", "rating"]),
    domain: Optional[List[str]] = Query(None)
):
    sort_mapping = {
        "alphabetical": ("name", ASCENDING),
        "date": ("date", DESCENDING),
        "rating": ("total_rating", DESCENDING)
       
    }

    sort_field, sort_order = sort_mapping[sort_by]
    
    query = {}
    if domain:
        query["domain"] = {"$in": domain}

    # Fetch courses
    courses = list(courses_collection.find(query))
    
    # Calculate total rating for each course
    courses = [aggregate_ratings(course) for course in courses]

    # Sort courses by the chosen field
    courses.sort(key=lambda x: x.get(sort_field, 0), reverse=(sort_order == DESCENDING))
    
    courses = [convert_object_id(course) for course in courses]

    return {"courses": courses}

# Endpoint to fetch and return a specific course overview by its name
@app.get("/courses/overview")
async def get_course_overview_by_name(course_name: str):
    # Search for the course by name (case-insensitive)
    course = courses_collection.find_one({"name": {"$regex": course_name, "$options": "i"}})
    
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Convert ObjectId to string for the response
    course = convert_object_id(course)
    
    return {"course": course}

# Endpoint to fetch chapter details
@app.get("/courses/chapter")
async def get_chapter_info(
    course_name: str = Query(..., description="Name of the course"),
    chapter_name: str = Query(..., description="Name of the chapter")
):
    course = courses_collection.find_one({"name": course_name})
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    chapter = next((ch for ch in course["chapters"] if ch["name"] == chapter_name), None)
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return {"chapter": chapter}

#Endpoint to rate courses
@app.post("/courses/{course_name}/chapters/{chapter_name}/rate")
async def rate_chapter(course_name: str, 
                       chapter_name: str, 
                       rating: str = Query(..., description="Rating must be 'positive' or 'negative'")):
    print(f"Received rating: {rating}") 
    valid_ratings = ["positive", "negative"]
    
    # Check if rating is valid
    if rating not in valid_ratings:
        raise HTTPException(status_code=400, detail=f"Rating must be one of {valid_ratings}.")

    # Find the course by name
    course = courses_collection.find_one({"name": {"$regex": course_name, "$options": "i"}})
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    
    # Find the chapter by name
    chapter_found = False
    for chapter in course["chapters"]:
        if chapter_name.lower() in chapter["name"].lower():
            if "ratings" not in chapter:
                chapter["ratings"] = {"positive": 0, "negative": 0}
            chapter["ratings"][rating] += 1
            chapter_found = True
            break
    
    if not chapter_found:
        raise HTTPException(status_code=404, detail="Chapter not found.")
    
    # Update the course document with the new rating
    courses_collection.update_one(
        {"_id": course["_id"], "chapters.name": chapter["name"]},
        {"$set": {"chapters.$.ratings": chapter["ratings"]}}
    )

    return {"message": "Rating added successfully.", "chapter": chapter["name"], "ratings": chapter["ratings"]}