Feature: Assign Bug Priority

  Background:
    Given the Issue Intake Service is running
    And the user is authenticated

  # Scenario 1 - Happy Path (AC1)
  Scenario: Assign valid priority successfully
    Given a bug exists with ID "BUG-00001"
    When the developer assigns priority "High" to bug "BUG-00001"
    Then the system should update the bug priority successfully
    And the bug priority should be "High"

  # Scenario 2 - Failure Scenario (AC2)
  Scenario: Reject invalid priority value
    Given a bug exists with ID "BUG-00001"
    When the developer assigns priority "Urgent" to bug "BUG-00001"
    Then the system should return a validation error

  # Scenario 3 - Failure Scenario (AC3)
  Scenario: Reject priority assignment for missing bug
    Given no bug exists with ID "BUG-99999"
    When the developer assigns priority "High" to bug "BUG-99999"
    Then the system should return a not found error

  # Scenario 4 - Persistence (AC4)
  Scenario: Persist assigned priority
    Given a bug exists with ID "BUG-00001"
    When the developer assigns priority "Critical" to bug "BUG-00001"
    And the developer retrieves bug "BUG-00001"
    Then the bug priority should be "Critical"

  # Scenario 5 - NFR Scenario (AC5)
  Scenario: Priority assignment under performance limits
    Given a bug exists with ID "BUG-00001"
    When the developer assigns priority "Medium" to bug "BUG-00001"
    Then the response time should be under 3 seconds
