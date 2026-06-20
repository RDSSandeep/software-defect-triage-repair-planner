# AGENTS.md — AI Execution Rules

## 1. Startup Rules

Before executing any use case:

* Read all project governance files
* Load feature_list.json
* Follow AGENTS.md strictly
* Ensure only ONE use case is processed at a time

## 2. Development Workflow

Each use case MUST follow:

### Step 1: Gherkin Generation

* Convert use case into acceptance scenarios
* Minimum 4 scenarios per use case
* Include happy path, failure, dependency, and NFR scenario

### Step 2: Implementation Design

* Define system boundary
* Create deterministic stubs
* Define API contracts
* Prepare test harness

### Step 3: Implementation

* Write minimal code to pass tests
* Do not over-engineer
* Ensure determinism

### Step 4: Failure Handling

* If tests fail:

  * Create failure bundle
  * Identify root cause
  * Apply minimal patch fix

## 3. Rules

* Do NOT implement multiple use cases at once
* Do NOT change unrelated modules
* All outputs must be traceable to a use case
* All changes must update feature_list.json

## 4. Completion Rules

After completing a use case:

* Mark status = done
* Add evidence (tests passed)
* Commit changes to GitHub