---
name: data-formatting-validation
description: Use this skill to validate data formats and ensure compliance with specifications.
---
1. Check that monetary values are represented as integers in cents (e.g., 1606.67 USD should be 160667).
2. Ensure that all date and timestamp formats are consistent and in UTC (YYYY-MM-DDTHH:MM:SSZ).
3. Validate that all required fields in output files (e.g., `meta` object in JSON) are present and correctly formatted.
4. Review the output structure against the specified schema to ensure compliance.
5. Log any discrepancies and correct the data formats before final submission.
