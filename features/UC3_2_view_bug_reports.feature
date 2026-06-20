Feature: View Bug Reports

  Background:
    Given the Issue Intake Service is running
    And the user is authenticated

  # Scenario 1 - Happy Path (Retrieve All)
  Scenario: Retrieve all bug reports successfully
    Given the system has existing bug reports
    When the developer requests all bug reports
    Then the system should return a list of bugs
    And the list should contain all persistent bug reports

  # Scenario 2 - Happy Path (Retrieve by ID)
  Scenario: Retrieve a bug by valid ID
    Given a bug exists with ID "BUG-00001"
    When the developer requests bug with ID "BUG-00001"
    Then the system should return the bug details
    And the retrieved bug details should match the expected ID "BUG-00001"

  # Scenario 3 - Failure Scenario (Invalid/Non-existent ID)
  Scenario: Retrieve a bug by invalid ID
    Given no bug exists with ID "BUG-99999"
    When the developer requests bug with ID "BUG-99999"
    Then the system should return a not found error

  # Scenario 4 - Dependency Scenario (Dependency on UC3.1 Submission)
  Scenario: Retrieve a newly submitted bug report
    When the developer submits a bug report with:
      | title        | Read failure |
      | description  | Cannot retrieve records |
      | environment  | Firefox |
      | steps        | View records page |
    And the developer requests the bug using the generated issue ID
    Then the retrieved bug details should match the submitted report

  # Scenario 5 - NFR Scenario (Performance Limit)
  Scenario: View bug reports under performance limits
    Given the system has existing bug reports
    When the developer requests all bug reports
    Then the response time should be under 3 seconds