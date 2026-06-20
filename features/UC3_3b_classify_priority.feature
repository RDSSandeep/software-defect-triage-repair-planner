Feature: AI Bug Priority Classification

  Background:
    Given the Issue Intake Service is running
    And the user is authenticated

  # Scenario 1 - Critical: system crash detected
  Scenario: Classify crash bug as Critical
    When the developer classifies a bug with title "App crash on login" description "System crash occurs when submitting login form" environment "Chrome"
    Then the classification result priority should be "Critical"

  # Scenario 2 - High: major feature broken
  Scenario: Classify broken feature as High
    When the developer classifies a bug with title "Payment button broken" description "Payment form does not work and is completely unavailable" environment "Firefox"
    Then the classification result priority should be "High"

  # Scenario 3 - Medium: intermittent / workaround exists
  Scenario: Classify intermittent issue as Medium
    When the developer classifies a bug with title "Dashboard slow" description "Dashboard loads intermittently and a workaround is to refresh the page" environment "Safari"
    Then the classification result priority should be "Medium"

  # Scenario 4 - Low: cosmetic / default fallback
  Scenario: Classify cosmetic issue as Low
    When the developer classifies a bug with title "Button colour misaligned" description "The submit button has a slightly off colour tint on the settings page" environment "Edge"
    Then the classification result priority should be "Low"

  # Scenario 5 - Validation failure: all fields empty
  Scenario: Reject classify request with all empty fields
    When the developer classifies a bug with title "" description "" environment ""
    Then the system should return a validation error
