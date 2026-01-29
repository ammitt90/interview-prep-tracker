import json
import pytest
from datetime import datetime
from app import app, db, Problem
from sqlalchemy.exc import SQLAlchemyError

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            yield client
@pytest.fixture(scope="module")
def init_db():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
def test_get_all_problems(test_client, init_db):
    # Insert a problem directly into the database
    problem = Problem(
        title="GET Test Problem",
        topic="Array",
        difficulty=1,
        status="Not Started",
        deadline_date=datetime.strptime("12-31-2025", "%m-%d-%Y").date()
    )

    db.session.add(problem)
    db.session.commit()

    # Make GET request
    response = test_client.get("/problems")

    # Assertions
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Verify inserted problem exists
    assert any(p["title"] == "GET Test Problem" for p in data)
def test_update_problem_status(test_client, init_db):
    problem = Problem(
        title="PUT Test Problem",
        topic="Array",
        difficulty=2,
        status="Not Started",
        deadline_date=datetime.strptime("12-31-2025", "%m-%d-%Y").date()
    )

    db.session.add(problem)
    db.session.commit()

    response = test_client.put(
        f"/problems/updatestatus/{problem.id}",
        json={"status": "Completed"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "Completed"

def test_update_problem_invalid_status(test_client, init_db):
    problem = Problem(
        title="Invalid Status Test",
        topic="Array",
        difficulty=1,
        status="Not Started",
        deadline_date=datetime.strptime("12-31-2025", "%m-%d-%Y").date()
    )

    db.session.add(problem)
    db.session.commit()

    response = test_client.put(
        f"/problems/updatestatus/{problem.id}",
        json={"status": "WrongStatus"}
    )

    assert response.status_code == 400