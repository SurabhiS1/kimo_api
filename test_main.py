import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_courses_alphabetical():
    response = client.get("/courses?sort_by=alphabetical")
    assert response.status_code == 200
    data = response.json()
    assert "courses" in data
    
def test_get_courses_by_date():
    response = client.get("/courses?sort_by=date")
    assert response.status_code == 200
    data = response.json()
    assert "courses" in data
    

def test_get_courses_with_domain_filter():
    response = client.get("/courses?sort_by=alphabetical&domain=artificial%20intelligence")
    assert response.status_code == 200
    data = response.json()
    assert "courses" in data
    
def test_get_course_overview():
    response = client.get("/courses/overview?course_name=Computer%20Vision%20Course")
    assert response.status_code == 200
    data = response.json()
    assert "course" in data
   
def test_get_chapter_info():
    response = client.get("/courses/chapter?course_name=Computer%20Vision%20Course&chapter_name=Introduction%20to%20Convolutional%20Neural%20Networks%20for%20Visual%20Recognition")
    assert response.status_code == 200
    data = response.json()
    assert "chapter" in data
   
def test_rate_chapter_positive():
    response = client.post("/courses/Computer%20Vision%20Course/chapters/Introduction%20to%20Convolutional%20Neural%20Networks%20for%20Visual%20Recognition/rate?rating=positive")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Rating added successfully."
    assert data["ratings"]["positive"] > 0  

def test_rate_chapter_negative():
    response = client.post("/courses/Computer%20Vision%20Course/chapters/Introduction%20to%20Convolutional%20Neural%20Networks%20for%20Visual%20Recognition/rate?rating=negative")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Rating added successfully."
    assert data["ratings"]["negative"] > 0  


