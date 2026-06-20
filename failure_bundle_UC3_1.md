# Failure Bundle — UC3.1 Submit Bug Report

## Use Case

UC3.1 — Submit Bug Report

## Failed Scenario

Reject bug report when title is missing

## Feature File

features/UC3_1_submit_bug_report.feature

## Failure Summary

The acceptance test failed when the system received a bug report request without a title field.
Instead of returning a validation error response, the application raised an unhandled exception during string processing.

## Expected Behavior

* The system should validate required fields consistently.
* A validation error response should be returned when the title field is missing.
* No bug record should be created.

## Actual Behavior

* The application attempted to call `.strip()` on a `NoneType` object.
* The request caused an internal server exception.
* The acceptance scenario failed.

## Error Details

```text
AttributeError: 'NoneType' object has no attribute 'strip'
```

## Stack Trace Location

```text
File: app/services/bug_service.py
Function: validate_and_create_bug
```

Problematic code path:

```python
(bug_id, title.strip(), description.strip(), environment.strip(), steps.strip() if steps else None)
```

## Root Cause Hypothesis

The validation logic did not check whether `title` was `None` before attempting string normalization using `.strip()`.

## Acceptance Contract Violated

* Required fields are validated consistently.
* Validation errors must be returned instead of server crashes.

## Impact

* Invalid requests can terminate request processing unexpectedly.
* The API does not satisfy deterministic acceptance behavior for missing required fields.

## Verification Evidence

### Failed Test Output

* 1 feature error
* 1 scenario error
* Scenario:
  Reject bug report when title is missing

### Successful Re-test After Fix

* 1 feature passed
* 4 scenarios passed
* 21 steps passed

## Recommended Minimal Patch

* Add explicit null/empty validation before calling `.strip()`
* Return controlled validation response instead of allowing runtime exception
* Preserve deterministic behavior and BUG-XXXXX sequential ID generation