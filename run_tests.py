# =============================================================================
# CodeCraftHub — Automated API Test Suite
# =============================================================================
# This script tests every endpoint in app.py automatically.
# No manual curl commands needed — just run: python run_tests.py
#
# Prerequisites:
#   1. pip install requests
#   2. Make sure app.py is running: python app.py
#   3. Then in a NEW terminal: python run_tests.py
# =============================================================================

import requests   # For making HTTP requests (pip install requests)
import json       # For pretty-printing responses
import sys        # For exiting with an error code if tests fail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

BASE_URL = "http://127.0.0.1:5000"   # Where your Flask app is running

# Counters to track how many tests pass or fail
passed = 0
failed = 0

# We'll store the ID of a created course here so later tests can use it
created_course_id = None


# =============================================================================
# HELPER FUNCTIONS
# These make the test output readable and keep test logic DRY (Don't Repeat Yourself)
# =============================================================================

def print_header(title):
    """Prints a formatted section header to the terminal."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_test(name):
    """Prints the name of the test currently being run."""
    print(f"\n  >> {name}")


def assert_test(condition, success_msg, failure_msg, response=None):
    """
    Checks whether a test condition is True or False.
    Increments the global pass/fail counters accordingly.

    Args:
        condition    (bool): The thing we're checking (e.g. status_code == 201)
        success_msg   (str): Message to print if the test passes
        failure_msg   (str): Message to print if the test fails
        response: Optional requests.Response object to print on failure
    """
    global passed, failed

    if condition:
        print(f"     PASS  {success_msg}")
        passed += 1
    else:
        print(f"     FAIL  {failure_msg}")
        if response is not None:
            # Print the actual response so you can debug what went wrong
            try:
                print(f"            Response: {json.dumps(response.json(), indent=12)}")
            except Exception:
                print(f"            Response text: {response.text}")
        failed += 1


def print_response(response):
    """Pretty-prints a JSON response. Useful for debugging."""
    try:
        print(f"     Body: {json.dumps(response.json(), indent=12)}")
    except Exception:
        print(f"     Body: {response.text}")


def check_server():
    """
    Makes sure the Flask server is running before we start testing.
    Exits early with a helpful message if it's not.
    """
    print("\nChecking server is running...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=3)
        print(f"  Server is up! Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("\n  ERROR: Could not connect to the server.")
        print("  Make sure app.py is running: python app.py")
        sys.exit(1)   # Exit with error code 1


# =============================================================================
# TEST GROUPS
# Each function tests one category of behavior.
# =============================================================================

# -----------------------------------------------------------------------------
# GROUP 1 — Happy Path: Creating Courses (POST /api/courses)
# -----------------------------------------------------------------------------

def test_create_courses():
    """Tests the POST /api/courses endpoint with valid data."""
    global created_course_id

    print_header("GROUP 1 — Create Courses (POST /api/courses)")

    # ---- Test 1: Create first course ----------------------------------------
    print_test("Create course 1 — Flask for Beginners")
    payload = {
        "name": "Flask for Beginners",
        "description": "Learn REST APIs with Python and Flask",
        "target_date": "2025-08-01",
        "status": "Not Started"
    }
    r = requests.post(f"{BASE_URL}/api/courses", json=payload)

    assert_test(r.status_code == 201, "Status code is 201 Created", f"Expected 201, got {r.status_code}", r)

    data = r.json()
    assert_test("course" in data,          "Response contains 'course' key",         "Missing 'course' key", r)
    assert_test(data["course"]["id"] >= 1, "Course has a valid auto-generated ID",   "ID is missing or invalid", r)
    assert_test("created_at" in data["course"], "Course has a 'created_at' timestamp", "Missing 'created_at'", r)

    # Save the ID so later tests can use it (e.g. GET, PUT, DELETE)
    created_course_id = data["course"]["id"]
    print(f"     Note: Created course ID = {created_course_id}")

    # ---- Test 2: Create second course ----------------------------------------
    print_test("Create course 2 — Python Data Structures")
    payload2 = {
        "name": "Python Data Structures",
        "description": "Master lists, dicts, sets and more",
        "target_date": "2025-10-15",
        "status": "In Progress"
    }
    r2 = requests.post(f"{BASE_URL}/api/courses", json=payload2)
    assert_test(r2.status_code == 201, "Status code is 201 Created", f"Expected 201, got {r2.status_code}", r2)
    assert_test(r2.json()["course"]["status"] == "In Progress", "'In Progress' status saved correctly", "Status mismatch", r2)

    # ---- Test 3: Create third course ----------------------------------------
    print_test("Create course 3 — status 'Completed'")
    payload3 = {
        "name": "Git & GitHub Essentials",
        "description": "Version control for developers",
        "target_date": "2025-06-01",
        "status": "Completed"
    }
    r3 = requests.post(f"{BASE_URL}/api/courses", json=payload3)
    assert_test(r3.status_code == 201, "Status code is 201 Created", f"Expected 201, got {r3.status_code}", r3)
    assert_test(r3.json()["course"]["status"] == "Completed", "'Completed' status saved correctly", "Status mismatch", r3)


# -----------------------------------------------------------------------------
# GROUP 2 — Happy Path: Reading Courses (GET /api/courses)
# -----------------------------------------------------------------------------

def test_get_courses():
    """Tests the GET /api/courses and GET /api/courses/<id> endpoints."""

    print_header("GROUP 2 — Get Courses (GET /api/courses)")

    # ---- Test 4: Get all courses --------------------------------------------
    print_test("Get all courses")
    r = requests.get(f"{BASE_URL}/api/courses")
    assert_test(r.status_code == 200,           "Status code is 200 OK",            f"Expected 200, got {r.status_code}", r)
    assert_test("courses" in r.json(),          "Response has 'courses' key",        "Missing 'courses' key", r)
    assert_test(r.json()["total"] >= 3,         "At least 3 courses returned",       f"Expected >= 3, got {r.json().get('total')}", r)

    # ---- Test 5: Filter by status "In Progress" -----------------------------
    print_test("Filter courses by status=In Progress")
    r = requests.get(f"{BASE_URL}/api/courses", params={"status": "In Progress"})
    assert_test(r.status_code == 200, "Status code is 200 OK", f"Expected 200, got {r.status_code}", r)
    data = r.json()
    all_in_progress = all(c["status"] == "In Progress" for c in data["courses"])
    assert_test(all_in_progress, "All returned courses have status 'In Progress'", "Some courses have wrong status", r)

    # ---- Test 6: Filter by status "Completed" -------------------------------
    print_test("Filter courses by status=Completed")
    r = requests.get(f"{BASE_URL}/api/courses", params={"status": "Completed"})
    assert_test(r.status_code == 200, "Status code is 200 OK", f"Expected 200, got {r.status_code}", r)
    completed = r.json()["courses"]
    assert_test(len(completed) >= 1, "At least 1 completed course found", "No completed courses returned", r)

    # ---- Test 7: Get a specific course by ID ---------------------------------
    print_test(f"Get course by ID ({created_course_id})")
    r = requests.get(f"{BASE_URL}/api/courses/{created_course_id}")
    assert_test(r.status_code == 200, "Status code is 200 OK", f"Expected 200, got {r.status_code}", r)
    assert_test(r.json()["course"]["id"] == created_course_id, "Returned correct course ID", "Wrong course returned", r)
    assert_test(r.json()["course"]["name"] == "Flask for Beginners", "Returned correct course name", "Wrong name", r)


# -----------------------------------------------------------------------------
# GROUP 3 — Happy Path: Updating Courses (PUT /api/courses/<id>)
# -----------------------------------------------------------------------------

def test_update_courses():
    """Tests the PUT /api/courses/<id> endpoint — partial and full updates."""

    print_header("GROUP 3 — Update Courses (PUT /api/courses/<id>)")

    # ---- Test 8: Partial update — status only --------------------------------
    print_test("Partial update — change status to 'In Progress'")
    r = requests.put(f"{BASE_URL}/api/courses/{created_course_id}", json={"status": "In Progress"})
    assert_test(r.status_code == 200, "Status code is 200 OK", f"Expected 200, got {r.status_code}", r)
    assert_test(r.json()["course"]["status"] == "In Progress", "Status updated to 'In Progress'", "Status not updated", r)

    # Verify the name was NOT changed (partial update should leave other fields alone)
    assert_test(r.json()["course"]["name"] == "Flask for Beginners", "Other fields unchanged", "Partial update overwrote other fields!", r)

    # ---- Test 9: Partial update — name only ----------------------------------
    print_test("Partial update — change name only")
    r = requests.put(f"{BASE_URL}/api/courses/{created_course_id}", json={"name": "Flask — Advanced"})
    assert_test(r.status_code == 200, "Status code is 200 OK", f"Expected 200, got {r.status_code}", r)
    assert_test(r.json()["course"]["name"] == "Flask — Advanced", "Name updated correctly", "Name not updated", r)
    # Status should still be "In Progress" from Test 8
    assert_test(r.json()["course"]["status"] == "In Progress", "Status preserved from previous update", "Status was reset!", r)

    # ---- Test 10: Full update — all fields -----------------------------------
    print_test("Full update — all fields at once")
    full_payload = {
        "name": "Flask for Beginners",           # Reset name back
        "description": "Updated description!",
        "target_date": "2025-12-31",
        "status": "Completed"
    }
    r = requests.put(f"{BASE_URL}/api/courses/{created_course_id}", json=full_payload)
    assert_test(r.status_code == 200,                                   "Status code is 200 OK",          f"Expected 200, got {r.status_code}", r)
    assert_test(r.json()["course"]["status"] == "Completed",            "Status updated to 'Completed'",   "Status not updated", r)
    assert_test(r.json()["course"]["description"] == "Updated description!", "Description updated",        "Description not updated", r)
    assert_test(r.json()["course"]["target_date"] == "2025-12-31",      "Target date updated",             "Date not updated", r)


# -----------------------------------------------------------------------------
# GROUP 4 — Happy Path: Deleting Courses (DELETE /api/courses/<id>)
# -----------------------------------------------------------------------------

def test_delete_courses():
    """Tests the DELETE /api/courses/<id> endpoint."""

    print_header("GROUP 4 — Delete Courses (DELETE /api/courses/<id>)")

    # ---- Test 11: Delete the third course (Git & GitHub) --------------------
    # First, get all courses to find a course ID to delete
    print_test("Delete a course by ID")
    all_courses = requests.get(f"{BASE_URL}/api/courses").json()["courses"]
    delete_target = next((c for c in all_courses if c["name"] == "Git & GitHub Essentials"), None)

    if delete_target:
        delete_id = delete_target["id"]
        r = requests.delete(f"{BASE_URL}/api/courses/{delete_id}")
        assert_test(r.status_code == 200, "Status code is 200 OK", f"Expected 200, got {r.status_code}", r)
        assert_test("deleted_course" in r.json(), "Response contains 'deleted_course'", "Missing 'deleted_course' key", r)
        assert_test(r.json()["deleted_course"]["id"] == delete_id, "Correct course was deleted", "Wrong course deleted", r)

        # ---- Test 12: Verify it's gone ---------------------------------------
        print_test("Verify deleted course no longer exists")
        r2 = requests.get(f"{BASE_URL}/api/courses/{delete_id}")
        assert_test(r2.status_code == 404, "Deleted course returns 404", f"Expected 404, got {r2.status_code}", r2)
    else:
        print("     SKIP  Could not find 'Git & GitHub Essentials' to delete (may have already been deleted)")


# -----------------------------------------------------------------------------
# GROUP 5 — Error Handling
# -----------------------------------------------------------------------------

def test_error_handling():
    """Tests that the API returns proper errors for bad requests."""

    print_header("GROUP 5 — Error Handling")

    # ---- Test 13: POST with no body -----------------------------------------
    print_test("POST with no JSON body")
    r = requests.post(f"{BASE_URL}/api/courses", data="not json", headers={"Content-Type": "text/plain"})
    assert_test(r.status_code == 400, "Returns 400 for non-JSON body", f"Expected 400, got {r.status_code}", r)

    # ---- Test 14: POST with missing fields ----------------------------------
    print_test("POST with missing required fields")
    r = requests.post(f"{BASE_URL}/api/courses", json={"name": "Incomplete Course"})
    assert_test(r.status_code == 400, "Returns 400 for missing fields", f"Expected 400, got {r.status_code}", r)
    assert_test("missing" in r.json(), "Error response lists missing fields", "No 'missing' key in error", r)

    # ---- Test 15: POST with invalid status ----------------------------------
    print_test("POST with invalid status value")
    r = requests.post(f"{BASE_URL}/api/courses", json={
        "name": "Bad Status Course",
        "description": "This has a bad status",
        "target_date": "2025-08-01",
        "status": "Pending"   # Not a valid status
    })
    assert_test(r.status_code == 400, "Returns 400 for invalid status", f"Expected 400, got {r.status_code}", r)
    assert_test("Invalid status" in r.json().get("error", ""), "Error message mentions 'Invalid status'", "Error message unclear", r)

    # ---- Test 16: POST with bad date format ---------------------------------
    print_test("POST with wrong date format (MM/DD/YYYY instead of YYYY-MM-DD)")
    r = requests.post(f"{BASE_URL}/api/courses", json={
        "name": "Bad Date Course",
        "description": "Wrong date format",
        "target_date": "08/01/2025",   # Wrong format
        "status": "Not Started"
    })
    assert_test(r.status_code == 400, "Returns 400 for bad date format", f"Expected 400, got {r.status_code}", r)
    assert_test("target_date" in r.json().get("error", ""), "Error message mentions 'target_date'", "Error message unclear", r)

    # ---- Test 17: POST with empty name -------------------------------------
    print_test("POST with blank name (spaces only)")
    r = requests.post(f"{BASE_URL}/api/courses", json={
        "name": "    ",    # Only whitespace — should be rejected
        "description": "Blank name test",
        "target_date": "2025-08-01",
        "status": "Not Started"
    })
    assert_test(r.status_code == 400, "Returns 400 for blank name", f"Expected 400, got {r.status_code}", r)

    # ---- Test 18: GET course that doesn't exist -----------------------------
    print_test("GET /api/courses/99999 — non-existent ID")
    r = requests.get(f"{BASE_URL}/api/courses/99999")
    assert_test(r.status_code == 404, "Returns 404 for missing course", f"Expected 404, got {r.status_code}", r)
    assert_test("not found" in r.json().get("error", "").lower(), "Error message says 'not found'", "Unclear error message", r)

    # ---- Test 19: PUT course that doesn't exist -----------------------------
    print_test("PUT /api/courses/99999 — non-existent ID")
    r = requests.put(f"{BASE_URL}/api/courses/99999", json={"status": "Completed"})
    assert_test(r.status_code == 404, "Returns 404 for missing course", f"Expected 404, got {r.status_code}", r)

    # ---- Test 20: DELETE course that doesn't exist --------------------------
    print_test("DELETE /api/courses/99999 — non-existent ID")
    r = requests.delete(f"{BASE_URL}/api/courses/99999")
    assert_test(r.status_code == 404, "Returns 404 for missing course", f"Expected 404, got {r.status_code}", r)

    # ---- Test 21: PUT with invalid status -----------------------------------
    print_test("PUT with invalid status value on existing course")
    r = requests.put(f"{BASE_URL}/api/courses/{created_course_id}", json={"status": "Abandoned"})
    assert_test(r.status_code == 400, "Returns 400 for invalid status on update", f"Expected 400, got {r.status_code}", r)

    # ---- Test 22: GET with invalid status filter ----------------------------
    print_test("GET with invalid ?status filter")
    r = requests.get(f"{BASE_URL}/api/courses", params={"status": "Unknown"})
    assert_test(r.status_code == 400, "Returns 400 for bad status filter", f"Expected 400, got {r.status_code}", r)


# =============================================================================
# MAIN — Run all test groups and print summary
# =============================================================================

def print_summary():
    """Prints the final test results summary."""
    total = passed + failed
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    print(f"  Total tests : {total}")
    print(f"  Passed      : {passed}")
    print(f"  Failed      : {failed}")
    print("=" * 60)

    if failed == 0:
        print("\n  All tests passed! Your API is working correctly.")
    else:
        print(f"\n  {failed} test(s) failed. Review the output above to debug.")
        print("  Tip: Make sure app.py is running and courses.json is writable.")

    print()


if __name__ == "__main__":
    print("\n  CodeCraftHub API Test Suite")
    print("  ================================")

    # Step 1: Make sure the server is up
    check_server()

    # Step 2: Run all test groups in order
    # Order matters — create must run before get/update/delete
    test_create_courses()
    test_get_courses()
    test_update_courses()
    test_delete_courses()
    test_error_handling()

    # Step 3: Print the final summary
    print_summary()

    # Step 4: Exit with code 1 if any tests failed (useful for CI pipelines)
    if failed > 0:
        sys.exit(1)
