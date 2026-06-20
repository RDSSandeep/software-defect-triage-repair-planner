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
