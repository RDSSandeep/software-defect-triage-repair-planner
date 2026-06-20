Feature: Submit Bug Report

As a Developer
I want to submit bug reports
So that issues are tracked in the system

Background:
  Given the Issue Intake Service is running
  And the user is authenticated

# Scenario 1 - Happy path
Scenario: Successfully submit a valid bug report
  When the developer submits a bug report with:
    | title        | Login failure |
    | description  | Login crashes on submit |
    | environment  | Chrome |
    | steps        | Open login page and click submit |
  Then the system should create a bug record
  And the system should assign a unique issue ID
  And the response time should be under 3 seconds

# Scenario 2 - Missing title
Scenario: Reject bug report when title is missing
  When the developer submits a bug report with:
    | description  | Login crashes on submit |
    | environment  | Chrome |
  Then the system should return a validation error
  And no bug record should be created

# Scenario 3 - Missing description
Scenario: Reject bug report when description is missing
  When the developer submits a bug report with:
    | title        | Login failure |
    | environment  | Chrome |
  Then the system should return a validation error
  And no bug record should be created

# Scenario 4 - Invalid environment
Scenario: Reject bug report with invalid environment
  When the developer submits a bug report with:
    | title        | Login failure |
    | description  | Login crashes |
    | environment  | "" |
  Then the system should return an error message
  And no bug record should be created
