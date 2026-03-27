# ibm-ai-vibecoded
Practicing vibe coding

# CodeCraftHub

A lightweight REST API for developers to track the courses they want to learn.
Built with Python and Flask. No database required — data is stored in a local JSON file.

---

## What It Does

CodeCraftHub lets you manage a personal list of learning goals:

- Add courses you want to study
- Track their status (Not Started → In Progress → Completed)
- Set target completion dates
- Update or remove courses as you progress

---

## Project Structure

```
CodeCraftHub/
├── app.py            # Flask app — all routes and logic live here
├── courses.json      # Auto-created on first run — your data store
├── run_tests.py      # Automated test suite for all endpoints
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## Requirements

- Python 3.8 or higher
- pip (comes with Python)

Check your version:
```bash
python --version
```

---

## Setup

**1. Clone or download the project**
```bash
git clone https://github.com/your-username/CodeCraftHub.git
cd CodeCraftHub
```

**2. (Recommended) Create a virtual environment**

A virtual environment keeps your project's dependencies isolated from the rest of your system.

```bash
# Create the environment
python -m venv venv

# Activate it — Mac/Linux:
source venv/bin/activate

# Activate it — Windows:
venv\Scripts\activate
```

You'll see `(venv)` in your terminal prompt when it's active.

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Start the server**
```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

The `courses.json` file will be created automatically the first time the server starts.

---

## API Endpoints

All endpoints are prefixed with `/api`. The server runs at `http://127.0.0.1:5000`.

| Method   | Endpoint              | Description              |
|----------|-----------------------|--------------------------|
| `GET`    | `/api/courses`        | List all courses         |
| `POST`   | `/api/courses`        | Add a new course         |
| `GET`    | `/api/courses/<id>`   | Get one course by ID     |
| `PUT`    | `/api/courses/<id>`   | Update a course          |
| `DELETE` | `/api/courses/<id>`   | Delete a course          |

---

## Course Fields

| Field          | Type     | Required | Notes                                            |
|----------------|----------|----------|--------------------------------------------------|
| `name`         | string   | Yes      | Name of the course                               |
| `description`  | string   | Yes      | What the course covers                           |
| `target_date`  | string   | Yes      | Format: `YYYY-MM-DD`                             |
| `status`       | string   | Yes      | One of: `Not Started`, `In Progress`, `Completed`|
| `id`           | integer  | Auto     | Auto-assigned, starts at 1                       |
| `created_at`   | string   | Auto     | ISO 8601 timestamp, set on creation              |

---

## Usage Examples

### Add a course

```bash
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Flask for Beginners",
    "description": "Learn REST APIs with Python and Flask",
    "target_date": "2025-08-01",
    "status": "Not Started"
  }'
```

**Response (201 Created):**
```json
{
  "message": "Course created successfully!",
  "course": {
    "id": 1,
    "name": "Flask for Beginners",
    "description": "Learn REST APIs with Python and Flask",
    "target_date": "2025-08-01",
    "status": "Not Started",
    "created_at": "2025-03-27T10:30:00.123456"
  }
}
```

---

### List all courses

```bash
curl http://127.0.0.1:5000/api/courses
```

**Filter by status (optional):**
```bash
curl "http://127.0.0.1:5000/api/courses?status=In Progress"
```

Valid filter values: `Not Started`, `In Progress`, `Completed`

---

### Get one course

```bash
curl http://127.0.0.1:5000/api/courses/1
```

---

### Update a course

You only need to send the fields you want to change:

```bash
# Update status only
curl -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "In Progress"}'
```

```bash
# Update multiple fields
curl -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Flask — Intermediate",
    "target_date": "2025-09-01",
    "status": "In Progress"
  }'
```

---

### Delete a course

```bash
curl -X DELETE http://127.0.0.1:5000/api/courses/1
```

---

## Running the Tests

The test suite spins up 22 automated tests covering every endpoint and error scenario.

**Prerequisites:** the Flask server must be running in one terminal before you run tests in another.

**Terminal 1 — start the server:**
```bash
python app.py
```

**Terminal 2 — run the tests:**
```bash
pip install requests   # only needed once
python run_tests.py
```

**Sample output:**
```
  CodeCraftHub API Test Suite
  ================================
  Server is up! Status: 200

  ============================================================
    GROUP 1 — Create Courses (POST /api/courses)
  ============================================================

    >> Create course 1 — Flask for Beginners
       PASS  Status code is 201 Created
       PASS  Response contains 'course' key
       PASS  Course has a valid auto-generated ID
       PASS  Course has a 'created_at' timestamp

  ...

  ============================================================
    TEST SUMMARY
  ============================================================
    Total tests : 22
    Passed      : 22
    Failed      : 0
  ============================================================

  All tests passed! Your API is working correctly.
```

---

## Error Responses

The API returns descriptive errors for invalid requests.

| Scenario                      | Status | Example Response                                          |
|-------------------------------|--------|-----------------------------------------------------------|
| Missing required fields       | 400    | `{"error": "Missing required fields", "missing": [...]}` |
| Invalid status value          | 400    | `{"error": "Invalid status. Must be one of: [...]"}`     |
| Wrong date format             | 400    | `{"error": "Invalid 'target_date' format..."}`            |
| Blank name or description     | 400    | `{"error": "'name' cannot be empty"}`                     |
| Course ID not found           | 404    | `{"error": "Course with ID 99 not found"}`                |
| Server/file error             | 500    | `{"error": "Error reading courses file: ..."}`            |

---

## How the JSON File Works

Instead of a database, all data is stored in `courses.json`:

```json
{
  "next_id": 3,
  "courses": [
    {
      "id": 1,
      "name": "Flask for Beginners",
      "description": "Learn REST APIs with Python and Flask",
      "target_date": "2025-08-01",
      "status": "In Progress",
      "created_at": "2025-03-27T10:30:00.123456"
    }
  ]
}
```

`next_id` is a counter that increments each time a new course is added, ensuring IDs are always unique. The file is created automatically on first run — you don't need to create it manually.

> **Note:** This approach works great for learning and small projects. For a production app with many users, you'd want a proper database like SQLite or PostgreSQL.

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'flask'`**
```bash
pip install flask
```

**`ConnectionError` when running tests**
Make sure `python app.py` is running in a separate terminal first.

**`courses.json` has bad data / want a fresh start**
Simply delete `courses.json` and restart the server — it will be recreated empty.

**Port 5000 already in use**
Another process is using port 5000. Either stop that process, or change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```

---

## What You'll Learn from This Project

- How Flask routes map to HTTP methods (GET, POST, PUT, DELETE)
- The meaning of HTTP status codes (200, 201, 400, 404, 500)
- How to read and write JSON files with Python
- REST API design conventions
- Input validation and error handling patterns
- How to write automated API tests with the `requests` library

---

## Next Steps

Once you're comfortable with this project, here are some ways to extend it:

- **Add a frontend** — build a simple HTML/JS interface that calls your API
- **Switch to SQLite** — replace `courses.json` with a real database using `flask-sqlalchemy`
- **Add authentication** — protect endpoints with Flask-Login or JWT tokens
- **Deploy it** — host your API on Render, Railway, or Fly.io (all have free tiers)
- **Add pagination** — handle large lists with `?page=1&limit=10` query params

---

## License

APACHE 2.0 — free to use, modify, and share.
