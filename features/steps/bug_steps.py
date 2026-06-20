import time
import re
from behave import given, when, then
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import get_db_connection, init_db

# Initialize the test client
client = TestClient(app)

@given('the Issue Intake Service is running')
def step_impl_service_running(context):
    # Initialize the database
    init_db()
    
    # Clear the database before each scenario to guarantee determinism
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bugs")
    conn.commit()
    conn.close()
    
    # Attach client to context
    context.client = client

@given('the user is authenticated')
def step_impl_authenticated(context):
    # Setup mock authentication headers if needed
    context.headers = {
        "X-User-Authenticated": "true"
    }

@when('the developer submits a bug report with:')
def step_impl_submit_bug(context):
    # Parse Gherkin vertical key-value table
    # The first row is treated as headings by Behave.
    data = {}
    if context.table:
        # First row key-value
        key = context.table.headings[0].strip()
        val = context.table.headings[1].strip()
        data[key] = val
        
        # Subsequent rows key-value
        for row in context.table.rows:
            data[row[0].strip()] = row[1].strip()
            
    # Measure request response time
    start_time = time.time()
    response = context.client.post("/api/bugs", json=data, headers=getattr(context, 'headers', {}))
    end_time = time.time()
    
    context.response = response
    context.response_time = end_time - start_time

@then('the system should create a bug record')
def step_impl_check_record_created(context):
    assert context.response.status_code == 201, f"Expected 201 Created, got {context.response.status_code}"
    res_data = context.response.json()
    assert "id" in res_data
    
    # Verify persistence in SQLite
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bugs WHERE id = ?", (res_data["id"],))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None, "Bug record was not found in the SQLite database"
    assert row["title"] == res_data["title"]
    assert row["description"] == res_data["description"]

@then('the system should assign a unique issue ID')
def step_impl_check_unique_id(context):
    res_data = context.response.json()
    bug_id = res_data.get("id", "")
    # Check BUG-XXXXX format
    assert re.match(r"^BUG-\d{5}$", bug_id), f"Bug ID {bug_id} does not match expected format BUG-XXXXX"

@then('the response time should be under 3 seconds')
def step_impl_check_response_time(context):
    assert context.response_time < 3.0, f"Response time was {context.response_time} seconds, which is over 3 seconds"

@then('the system should return a validation error')
def step_impl_check_validation_error(context):
    # Expecting 400 Bad Request for validation errors
    assert context.response.status_code == 400, f"Expected 400 Bad Request, got {context.response.status_code}"
    res_data = context.response.json()
    assert "detail" in res_data, "Response body should contain a validation error detail"

@then('no bug record should be created')
def step_impl_check_no_record_created(context):
    # Database should be empty
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bugs")
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 0, f"Expected 0 bug records in database, found {count}"

@then('the system should return an error message')
def step_impl_check_error_message(context):
    # Expecting 400 Bad Request
    assert context.response.status_code == 400, f"Expected 400 Bad Request, got {context.response.status_code}"
    res_data = context.response.json()
    assert "detail" in res_data, "Response body should contain error message detail"


@given('the system has existing bug reports')
def step_impl_has_existing_bugs(context):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Insert a few mock bugs
    cursor.execute(
        "INSERT INTO bugs (id, title, description, environment, steps) VALUES (?, ?, ?, ?, ?)",
        ("BUG-00001", "Login crash", "Crashes on click", "Chrome", "Click login")
    )
    cursor.execute(
        "INSERT INTO bugs (id, title, description, environment, steps) VALUES (?, ?, ?, ?, ?)",
        ("BUG-00002", "Session timeout", "Timeout after 1m", "Safari", "Wait 1m")
    )
    conn.commit()
    conn.close()


@when('the developer requests all bug reports')
def step_impl_requests_all_bugs(context):
    start_time = time.time()
    response = context.client.get("/api/bugs", headers=getattr(context, 'headers', {}))
    end_time = time.time()
    context.response = response
    context.response_time = end_time - start_time


@then('the system should return a list of bugs')
def step_impl_returns_list_of_bugs(context):
    assert context.response.status_code == 200, f"Expected 200, got {context.response.status_code}"
    assert isinstance(context.response.json(), list), "Expected list in response"


@then('the list should contain all persistent bug reports')
def step_impl_list_contains_all(context):
    bugs = context.response.json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bugs")
    count = cursor.fetchone()[0]
    conn.close()
    assert len(bugs) == count, f"Expected {count} bugs, got {len(bugs)}"


@given('a bug exists with ID "{bug_id}"')
def step_impl_bug_exists_with_id(context, bug_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bugs WHERE id = ?", (bug_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            "INSERT INTO bugs (id, title, description, environment, steps) VALUES (?, ?, ?, ?, ?)",
            (bug_id, "Temporary title", "Temporary desc", "Chrome", "Steps")
        )
        conn.commit()
    conn.close()


@when('the developer requests bug with ID "{bug_id}"')
def step_impl_request_bug_by_id(context, bug_id):
    start_time = time.time()
    response = context.client.get(f"/api/bugs/{bug_id}", headers=getattr(context, 'headers', {}))
    end_time = time.time()
    context.response = response
    context.response_time = end_time - start_time


@then('the system should return the bug details')
def step_impl_returns_bug_details(context):
    assert context.response.status_code == 200, f"Expected 200, got {context.response.status_code}"
    data = context.response.json()
    assert "id" in data
    assert "title" in data


@then('the retrieved bug details should match the expected ID "{bug_id}"')
def step_impl_details_match_id(context, bug_id):
    data = context.response.json()
    assert data["id"] == bug_id, f"Expected {bug_id}, got {data['id']}"


@given('no bug exists with ID "{bug_id}"')
def step_impl_no_bug_exists(context, bug_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bugs WHERE id = ?", (bug_id,))
    conn.commit()
    conn.close()


@then('the system should return a not found error')
def step_impl_returns_not_found(context):
    assert context.response.status_code == 404, f"Expected 404, got {context.response.status_code}"
    res_data = context.response.json()
    assert "detail" in res_data


@when('the developer requests the bug using the generated issue ID')
def step_impl_request_generated_id(context):
    res_data = context.response.json()
    bug_id = res_data["id"]
    start_time = time.time()
    response = context.client.get(f"/api/bugs/{bug_id}", headers=getattr(context, 'headers', {}))
    end_time = time.time()
    context.response = response
    context.response_time = end_time - start_time


@then('the retrieved bug details should match the submitted report')
def step_impl_retrieved_matches_submitted(context):
    assert context.response.status_code == 200, f"Expected 200, got {context.response.status_code}"
    retrieved = context.response.json()
    assert retrieved["title"] == "Read failure"
    assert retrieved["description"] == "Cannot retrieve records"
    assert retrieved["environment"] == "Firefox"

