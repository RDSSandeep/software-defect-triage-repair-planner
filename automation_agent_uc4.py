import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000/api/bugs"


# -----------------------------
# Helper: Pretty print logs
# -----------------------------
def log(step, data=None):
    print("\n" + "=" * 60)
    print(f"🤖 {step}")
    print("=" * 60)
    if data:
        print(json.dumps(data, indent=2))


# -----------------------------
# Step 1: Create Bug (UC3.1)
# -----------------------------
def create_bug():
    payload = {
        "title": "Login crashes on submit button",
        "description": "System crash when user clicks submit after login",
        "environment": "Chrome 124 - Windows 11",
        "steps": "1. Open login page\n2. Enter credentials\n3. Click submit"
    }

    res = requests.post(BASE_URL, json=payload)

    if res.status_code in [200, 201]:
        bug = res.json()
        log("BUG CREATED", bug)
        return bug["id"]
    else:
        log("BUG CREATION FAILED", res.text)
        return None


# -----------------------------
# Step 2: Fetch Bug (UC3.2)
# -----------------------------
def get_bug(bug_id):
    res = requests.get(f"{BASE_URL}/{bug_id}")

    if res.status_code == 200:
        bug = res.json()
        log("BUG FETCHED", bug)
        return bug
    else:
        log("BUG FETCH FAILED", res.text)
        return None


# -----------------------------
# Step 3: Classify Priority (UC3.3 AI)
# -----------------------------
def classify_bug(bug):
    payload = {
        "title": bug["title"],
        "description": bug["description"],
        "environment": bug["environment"],
        "steps": bug.get("steps")
    }

    res = requests.post(f"{BASE_URL}/classify", json=payload)

    if res.status_code == 200:
        result = res.json()
        log("AI CLASSIFICATION RESULT", result)
        return result["priority"]
    else:
        log("CLASSIFICATION FAILED", res.text)
        return "Low"


# -----------------------------
# Step 4: Assign Priority
# -----------------------------
def assign_priority(bug_id, priority):
    payload = {"priority": priority}

    res = requests.patch(f"{BASE_URL}/{bug_id}/priority", json=payload)

    if res.status_code == 200:
        result = res.json()
        log("PRIORITY ASSIGNED", result)
        return result
    else:
        log("PRIORITY ASSIGN FAILED", res.text)
        return None


# -----------------------------
# MAIN AUTOMATION FLOW (UC4)
# -----------------------------
def run_agent():
    log("STARTING AUTOMATION AGENT (UC4)")

    # Step 1
    bug_id = create_bug()
    if not bug_id:
        return

    time.sleep(1)

    # Step 2
    bug = get_bug(bug_id)
    if not bug:
        return

    time.sleep(1)

    # Step 3
    priority = classify_bug(bug)

    time.sleep(1)

    # Step 4
    assign_priority(bug_id, priority)

    log("FINAL RESULT", {
        "bug_id": bug_id,
        "final_priority": priority,
        "status": "COMPLETED SUCCESSFULLY"
    })


if __name__ == "__main__":
    run_agent()