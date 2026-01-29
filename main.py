from datetime import datetime

from flask import Flask, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///problems.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    topic = db.Column(db.Text)
    difficulty = db.Column(db.Integer)
    status = db.Column(db.String(50), default="Not Started")
    deadline_date = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "status": self.status,
            "deadline_date": self.deadline_date.strftime("%Y-%m-%d") if self.deadline_date else '2026-01-01',
        }

def handle_db_errors(e):
    db.session.rollback()
    print("Database Error:", str(e))

with app.app_context():
    db.create_all()

    # Example data
    problems = [
        Problem(
            title="Two Sum",
            topic="Arrays",
            difficulty=1,
            status="Completed",
            deadline_date=datetime.today(),
        ),
        Problem(
            title="Binary Search",
            topic="Searching",
            difficulty=2,
            status="In Progress",
            deadline_date=datetime.today(),
        )
    ]

    try:
        db.session.add_all(problems)
        db.session.commit()
    except SQLAlchemyError as e:
        handle_db_errors(e)

@app.route('/problems', methods=['GET'])
def get_problems():
    try:
        problems = (
            db.session.query(Problem)
            .order_by(
                Problem.difficulty.asc(),
                Problem.deadline_date.asc()
            )
            .all()
        )

        return jsonify([problem.to_dict() for problem in problems]), 200

    except SQLAlchemyError as e:
        return handle_db_errors(e)

@app.route('/problems/problemid/<int:id>', methods=['GET'])
def get_problem_by_id(id):
    try:
        problem = Problem.query.get(id)

        if not problem:
            return jsonify({
                "error": "Problem not found"
            }), 404

        return jsonify(problem.to_dict()), 200

    except SQLAlchemyError as e:
        return handle_db_errors(e)


@app.route('/problems/add', methods=['POST'])
def add_problem():
    try:
        data = request.get_json()

        # 1. Validate required fields
        if not data or 'title' not in data:
            return jsonify({
                "error": "Title is required"
            }), 400

        title = data.get('title')
        topic = data.get('topic')
        difficulty = data.get('difficulty')
        status = data.get('status', 'Not Started')
        deadline_date = None

        # 2. Validate deadline date format if provided
        if 'deadline_date' in data and data['deadline_date']:
            try:
                deadline_date = datetime.strptime(
                    data['deadline_date'], "%Y-%m-%d"
                ).date()
            except ValueError:
                return jsonify({
                    "error": "Invalid deadline_date format. Use YYYY-MM-DD"
                }), 400

        # 3. Create new problem object
        new_problem = Problem(
            title=title,
            topic=topic,
            difficulty=difficulty,
            status=status,
            deadline_date=deadline_date
        )

        # 4. Save to database
        db.session.add(new_problem)
        db.session.commit()

        # 5. Return response with Location header
        response = jsonify(new_problem.to_dict())
        response.status_code = 201
        response.headers['Location'] = url_for(
            'get_problem_by_id',
            id=new_problem.id,
            _external=True
        )

        return response

    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_db_errors(e)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/problems/delete/<int:id>', methods=['DELETE'])
def delete_problem(id):
    try:
        # 1. Retrieve the problem by ID
        problem = Problem.query.get(id)

        # 2. Handle non-existent problem
        if not problem:
            return jsonify({
                "error": "Problem not found"
            }), 404

        # 3. Delete the problem
        db.session.delete(problem)
        db.session.commit()

        # 4. Return 204 No Content
        return '', 204

    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_db_errors(e)



@app.route('/problems/updatestatus/<int:id>', methods=['PUT'])
def update_problem_status(id):
    try:
        data = request.get_json()

        # 1. Validate input
        if not data or 'status' not in data:
            return jsonify({
                "error": "Status is required"
            }), 400

        valid_statuses = ["Not Started", "In Progress", "Completed"]
        new_status = data.get('status')

        # 2. Validate status value
        if new_status not in valid_statuses:
            return jsonify({
                "error": f"Invalid status. Allowed values: {valid_statuses}"
            }), 400

        # 3. Retrieve problem by ID
        problem = Problem.query.get(id)
        if not problem:
            return jsonify({
                "error": "Problem not found"
            }), 404

        # 4. Update status
        problem.status = new_status
        db.session.commit()

        # 5. Return updated problem
        return jsonify(problem.to_dict()), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_db_errors(e)

if __name__ == '__main__':
    app.run(debug=True,port=5000)