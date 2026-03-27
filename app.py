# =============================================================================
# CodeCraftHub - A Personalized Learning Platform for Developers
# =============================================================================
# This file contains the entire Flask REST API for managing learning courses.
# We use a simple JSON file as our "database" — no SQL or external DB needed!
#
# To run this app:
#   1. pip install flask
#   2. python app.py
#   3. Visit http://127.0.0.1:5000
# =============================================================================

import json                  # For reading/writing JSON data
import os                    # For checking if files exist
from datetime import datetime  # For generating timestamps
from flask import Flask, jsonify, request  # Core Flask tools

# -----------------------------------------------------------------------------
# App Setup
# -----------------------------------------------------------------------------

# Create the Flask application instance
# __name__ tells Flask where to look for resources (templates, static files, etc.)
app = Flask(__name__)

# The name of our JSON "database" file
# This file will be created automatically if it doesn't exist
COURSES_FILE = "courses.json"

# The only valid values for a course's status field
VALID_STATUSES = ["Not Started", "In Progress", "Completed"]


# =============================================================================
# JSON FILE HELPER FUNCTIONS
# These two functions are the backbone of our data layer.
# Every route will use them to read and write course data.
# =============================================================================

def read_courses():
    """
    Reads all courses from the JSON file and returns them as a Python dict.

    If the file doesn't exist yet, it creates a fresh one with an empty
    courses list and a course ID counter starting at 1.

    Returns:
        dict: e.g. {"next_id": 1, "courses": [...]}
    """
    # Check if the JSON file exists on disk
    if not os.path.exists(COURSES_FILE):
        # File doesn't exist — create a blank data structure
        initial_data = {
            "next_id": 1,        # Auto-incrementing ID counter
            "courses": []        # Empty list to hold course objects
        }
        # Write this blank structure to disk so the file now exists
        write_courses(initial_data)
        return initial_data

    # File exists — open it and parse the JSON into a Python dict
    try:
        with open(COURSES_FILE, "r") as file:
            data = json.load(file)  # json.load() parses JSON text → Python dict
        return data

    except (json.JSONDecodeError, IOError) as e:
        # Something went wrong reading or parsing the file
        # Raise an exception with a clear message so routes can catch it
        raise Exception(f"Error reading courses file: {str(e)}")


def write_courses(data):
    """
    Saves the given data dict to the JSON file on disk.

    Args:
        data (dict): The full data structure to save, e.g.
                     {"next_id": 3, "courses": [...]}
    """
    try:
        with open(COURSES_FILE, "w") as file:
            # json.dump() converts Python dict → JSON text
            # indent=4 makes the file human-readable (pretty-printed)
            json.dump(data, file, indent=4)

    except IOError as e:
        raise Exception(f"Error writing to courses file: {str(e)}")


# =============================================================================
# ROUTE 1 — POST /api/courses
# Create a brand-new course
# =============================================================================

@app.route("/api/courses", methods=["POST"])
def create_course():
    """
    Adds a new course to our JSON file.

    Expects a JSON body like:
    {
        "name": "Flask for Beginners",
        "description": "Learn REST APIs with Python and Flask",
        "target_date": "2025-08-01",
        "status": "Not Started"
    }

    Returns the newly created course with its auto-generated ID and timestamp.
    """
    # request.get_json() parses the incoming JSON body into a Python dict
    # If the body isn't valid JSON, it returns None
    body = request.get_json()

    # Guard: make sure the request actually included a JSON body
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    # -------------------------------------------------------------------------
    # Validate required fields
    # -------------------------------------------------------------------------

    # Define which fields we absolutely need
    required_fields = ["name", "description", "target_date", "status"]

    # Check each required field — collect any that are missing
    missing_fields = [field for field in required_fields if field not in body]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing": missing_fields
        }), 400  # 400 = Bad Request

    # -------------------------------------------------------------------------
    # Validate field values
    # -------------------------------------------------------------------------

    # Check that 'name' and 'description' are non-empty strings
    if not body["name"].strip():
        return jsonify({"error": "'name' cannot be empty"}), 400

    if not body["description"].strip():
        return jsonify({"error": "'description' cannot be empty"}), 400

    # Validate the target_date format — must be YYYY-MM-DD
    try:
        datetime.strptime(body["target_date"], "%Y-%m-%d")
    except ValueError:
        return jsonify({
            "error": "Invalid 'target_date' format. Use YYYY-MM-DD (e.g. 2025-08-01)"
        }), 400

    # Validate that the status is one of the three allowed values
    if body["status"] not in VALID_STATUSES:
        return jsonify({
            "error": f"Invalid status. Must be one of: {VALID_STATUSES}"
        }), 400

    # -------------------------------------------------------------------------
    # Build and save the new course
    # -------------------------------------------------------------------------

    try:
        data = read_courses()  # Load existing courses from file

        # Build the new course object
        new_course = {
            "id": data["next_id"],                          # Auto-incremented ID
            "name": body["name"].strip(),                   # Course name
            "description": body["description"].strip(),     # Course description
            "target_date": body["target_date"],             # Target completion date
            "status": body["status"],                       # Current status
            "created_at": datetime.now().isoformat()        # Timestamp (e.g. "2025-03-27T10:30:00")
        }

        data["courses"].append(new_course)  # Add course to the list
        data["next_id"] += 1                # Increment the ID counter for next time
        write_courses(data)                 # Save everything back to the file

        # Return the created course with HTTP 201 (Created)
        return jsonify({
            "message": "Course created successfully!",
            "course": new_course
        }), 201  # 201 = Created

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 500 = Internal Server Error


# =============================================================================
# ROUTE 2 — GET /api/courses
# Retrieve all courses
# =============================================================================

@app.route("/api/courses", methods=["GET"])
def get_all_courses():
    """
    Returns a list of all courses stored in our JSON file.

    Optionally filter by status using a query parameter:
        GET /api/courses?status=In Progress

    Returns an empty list [] if no courses exist yet.
    """
    try:
        data = read_courses()
        courses = data["courses"]

        # Optional: filter by status if provided as a query param
        # e.g. GET /api/courses?status=Completed
        status_filter = request.args.get("status")  # request.args reads query params

        if status_filter:
            # Validate the filter value before using it
            if status_filter not in VALID_STATUSES:
                return jsonify({
                    "error": f"Invalid status filter. Must be one of: {VALID_STATUSES}"
                }), 400

            # Filter courses down to only those matching the requested status
            courses = [c for c in courses if c["status"] == status_filter]

        return jsonify({
            "total": len(courses),
            "courses": courses
        }), 200  # 200 = OK

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# ROUTE 3 — GET /api/courses/<id>
# Retrieve a single course by its ID
# =============================================================================

@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    """
    Returns the course that matches the given ID.

    <int:course_id> tells Flask to capture the ID from the URL
    and automatically convert it to a Python integer.

    Example: GET /api/courses/3  → returns course with id=3
    """
    try:
        data = read_courses()

        # Search through all courses for the one with the matching ID
        # next() returns the first match, or None if nothing is found
        course = next((c for c in data["courses"] if c["id"] == course_id), None)

        if course is None:
            return jsonify({
                "error": f"Course with ID {course_id} not found"
            }), 404  # 404 = Not Found

        return jsonify({"course": course}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# ROUTE 4 — PUT /api/courses/<id>
# Update an existing course
# =============================================================================

@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    """
    Updates one or more fields of an existing course.

    You only need to send the fields you want to change — any field
    not included in the request body will keep its current value.

    Example body (partial update):
    {
        "status": "In Progress"
    }

    Full update example:
    {
        "name": "Advanced Flask",
        "description": "Deep dive into Flask",
        "target_date": "2025-09-01",
        "status": "Not Started"
    }
    """
    body = request.get_json()

    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Make sure the request isn't completely empty
    if not body:
        return jsonify({"error": "No fields provided to update"}), 400

    # -------------------------------------------------------------------------
    # Validate any provided fields
    # -------------------------------------------------------------------------

    # If 'name' was provided, make sure it's not blank
    if "name" in body and not body["name"].strip():
        return jsonify({"error": "'name' cannot be empty"}), 400

    # If 'description' was provided, make sure it's not blank
    if "description" in body and not body["description"].strip():
        return jsonify({"error": "'description' cannot be empty"}), 400

    # If 'target_date' was provided, validate the format
    if "target_date" in body:
        try:
            datetime.strptime(body["target_date"], "%Y-%m-%d")
        except ValueError:
            return jsonify({
                "error": "Invalid 'target_date' format. Use YYYY-MM-DD"
            }), 400

    # If 'status' was provided, make sure it's one of the valid values
    if "status" in body and body["status"] not in VALID_STATUSES:
        return jsonify({
            "error": f"Invalid status. Must be one of: {VALID_STATUSES}"
        }), 400

    # -------------------------------------------------------------------------
    # Find and update the course
    # -------------------------------------------------------------------------

    try:
        data = read_courses()

        # Find the index of the course we want to update
        course_index = next(
            (i for i, c in enumerate(data["courses"]) if c["id"] == course_id),
            None
        )

        if course_index is None:
            return jsonify({
                "error": f"Course with ID {course_id} not found"
            }), 404

        # Get a reference to the existing course dict
        course = data["courses"][course_index]

        # Update only the fields that were provided in the request
        # We use .get() so that missing keys don't overwrite existing values
        if "name" in body:
            course["name"] = body["name"].strip()
        if "description" in body:
            course["description"] = body["description"].strip()
        if "target_date" in body:
            course["target_date"] = body["target_date"]
        if "status" in body:
            course["status"] = body["status"]

        # Save the updated data back to the file
        data["courses"][course_index] = course
        write_courses(data)

        return jsonify({
            "message": "Course updated successfully!",
            "course": course
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# ROUTE 5 — DELETE /api/courses/<id>
# Remove a course permanently
# =============================================================================

@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    """
    Permanently deletes a course by its ID.

    Example: DELETE /api/courses/2  → removes course with id=2

    Returns the deleted course so the user knows what was removed.
    """
    try:
        data = read_courses()

        # Find the course we want to delete
        course = next((c for c in data["courses"] if c["id"] == course_id), None)

        if course is None:
            return jsonify({
                "error": f"Course with ID {course_id} not found"
            }), 404

        # Remove the course from the list using a list comprehension
        # This keeps every course EXCEPT the one with the matching ID
        data["courses"] = [c for c in data["courses"] if c["id"] != course_id]

        write_courses(data)  # Save the updated list back to the file

        return jsonify({
            "message": f"Course '{course['name']}' deleted successfully!",
            "deleted_course": course
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# BONUS ROUTE — GET /
# A simple welcome message so the API isn't a blank page
# =============================================================================

@app.route("/", methods=["GET"])
def home():
    """
    A friendly landing page for the API root.
    Useful for quickly checking that the server is running.
    """
    return jsonify({
        "message": "Welcome to CodeCraftHub API! 🚀",
        "description": "Your personalized developer learning tracker",
        "endpoints": {
            "GET    /api/courses":          "List all courses (optional: ?status=...)",
            "POST   /api/courses":          "Create a new course",
            "GET    /api/courses/<id>":     "Get a single course",
            "PUT    /api/courses/<id>":     "Update a course",
            "DELETE /api/courses/<id>":     "Delete a course"
        }
    }), 200


# =============================================================================
# App Entry Point
# =============================================================================

# This block only runs when you execute `python app.py` directly.
# It won't run if the file is imported as a module.
if __name__ == "__main__":
    print("🚀 CodeCraftHub API is starting...")
    print("📚 Visit http://127.0.0.1:5000 to explore the API")
    print("📁 Course data will be saved to:", COURSES_FILE)
    print("=" * 50)

    # debug=True enables:
    # - Auto-reload when you save changes to this file
    # - Detailed error messages in the browser
    # ⚠️  Always set debug=False in production!
    app.run(debug=True)
