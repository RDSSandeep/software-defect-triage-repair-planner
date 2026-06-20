from app.models.database import get_db_connection

class ValidationError(ValueError):
    pass

def validate_and_create_bug(title: str, description: str, environment: str, steps: str = None) -> dict:
    # Validate title
    if not title or not title.strip():
        raise ValidationError("Title is required and cannot be empty")
        
    # Validate description
    if not description or not description.strip():
        raise ValidationError("Description is required and cannot be empty")
        
    # Validate environment
    # Scenario 4 provides environment as literal '""' or empty
    if not environment or environment.strip() in ("", '""', '"'):
        raise ValidationError("Environment is invalid and cannot be empty")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Determine next BUG-XXXXX ID deterministically
        cursor.execute("SELECT COUNT(*) FROM bugs")
        count = cursor.fetchone()[0]
        bug_id = f"BUG-{count + 1:05d}"
        
        # Insert the bug
        cursor.execute(
            "INSERT INTO bugs (id, title, description, environment, steps) VALUES (?, ?, ?, ?, ?)",
            (bug_id, title.strip(), description.strip(), environment.strip(), steps.strip() if steps else None)
        )
        conn.commit()
        
        # Retrieve the inserted record
        cursor.execute("SELECT * FROM bugs WHERE id = ?", (bug_id,))
        row = cursor.fetchone()
        
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "environment": row["environment"],
            "steps": row["steps"],
            "created_at": row["created_at"]
        }
    finally:
        conn.close()
