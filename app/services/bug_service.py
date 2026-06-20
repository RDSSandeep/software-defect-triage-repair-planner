from app.models.database import get_db_connection

VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}

class ValidationError(ValueError):
    pass

def validate_and_create_bug(title: str, description: str, environment: str, steps: str = None) -> dict:
    # Validate title
    if title is None or not isinstance(title, str) or not title.strip():
        raise ValidationError("Title is required and cannot be empty")
        
    # Validate description
    if description is None or not isinstance(description, str) or not description.strip():
        raise ValidationError("Description is required and cannot be empty")
        
    # Validate environment
    # Scenario 4 provides environment as literal '""' or empty
    if environment is None or not isinstance(environment, str) or environment.strip() in ("", '""', '"'):
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
            (
                bug_id,
                title.strip(),
                description.strip(),
                environment.strip(),
                steps.strip() if (steps and isinstance(steps, str)) else None
            )
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
            "priority": row["priority"],
            "created_at": row["created_at"]
        }
    finally:
        conn.close()


def get_all_bugs() -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM bugs ORDER BY created_at ASC")
        rows = cursor.fetchall()
        bugs = []
        for row in rows:
            bugs.append({
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "environment": row["environment"],
                "steps": row["steps"],
                "priority": row["priority"],
                "created_at": row["created_at"]
            })
        return bugs
    finally:
        conn.close()


def get_bug_by_id(bug_id: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM bugs WHERE id = ?", (bug_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "environment": row["environment"],
            "steps": row["steps"],
            "priority": row["priority"],
            "created_at": row["created_at"]
        }
    finally:
        conn.close()


def assign_bug_priority(bug_id: str, priority: str) -> dict:
    """Assign a priority level to an existing bug.

    Returns:
        dict with id, priority, message on success.
        None if the bug_id does not exist.

    Raises:
        ValidationError: if priority is not one of the valid values.
    """
    if priority not in VALID_PRIORITIES:
        raise ValidationError("Invalid priority value")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verify bug exists
        cursor.execute("SELECT id FROM bugs WHERE id = ?", (bug_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        # Persist the priority
        cursor.execute("UPDATE bugs SET priority = ? WHERE id = ?", (priority, bug_id))
        conn.commit()

        return {
            "id": bug_id,
            "priority": priority,
            "message": "Priority updated successfully"
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Classification rules (mirrors the prompt template exactly)
# ---------------------------------------------------------------------------

_CLASSIFY_RULES = [
    (
        "Critical",
        ["crash", "data loss", "security", "breach", "corruption", "exploit",
         "unrecoverable", "system down", "outage", "unauthorized access"],
        "Matches critical rule: system crash, data loss, or security failure detected"
    ),
    (
        "High",
        ["broken", "not working", "fails", "failure", "unavailable", "cannot",
         "blocked", "does not work", "major", "won't load", "not loading"],
        "Matches high rule: major feature broken or unavailable"
    ),
    (
        "Medium",
        ["partial", "workaround", "intermittent", "sometimes", "slow",
         "degraded", "occasionally", "inconsistent", "timeout"],
        "Matches medium rule: partial failure or workaround exists"
    ),
]


def classify_bug_priority(title: str, description: str,
                           environment: str = None, steps: str = None) -> dict:
    """Apply rule-based classification to determine bug priority.

    Rules (checked in order):
        Critical → crash / data loss / security failure
        High     → major feature broken
        Medium   → partial failure / workaround exists
        Low      → default fallback (cosmetic / minor)

    Returns:
        { "priority": str, "reason": str }

    Raises:
        ValidationError: if all provided text fields are empty.
    """
    # Build a single lowercase blob from all text fields
    parts = [title or "", description or "", environment or "", steps or ""]
    blob = " ".join(parts).lower().strip()

    if not blob:
        raise ValidationError("At least one field (title, description) must be provided")

    for priority_label, keywords, reason in _CLASSIFY_RULES:
        if any(kw in blob for kw in keywords):
            return {"priority": priority_label, "reason": reason}

    return {
        "priority": "Low",
        "reason": "No critical, high, or medium indicators detected; classified as minor/cosmetic"
    }
