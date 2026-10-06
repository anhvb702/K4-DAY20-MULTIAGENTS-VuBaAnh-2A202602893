---
name: error-logging-structure
description: Use this skill to ensure error logs are structured and sorted according to specifications.
---
1. Parse log entries to extract relevant fields: `timestamp_utc`, `service`, `level`, `message`, `exception`, and `repeat_count`.
2. Convert all timestamps to UTC format and ensure they are correctly formatted.
3. Replace hyphens in service names with underscores and convert to lower case.
4. Sort the error entries first by `service`, then by `timestamp_utc` in ascending order.
5. Ensure the output includes a top-level object with `schema_version` and `generated_by` fields.
