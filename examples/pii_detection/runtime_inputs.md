# PII Detection Runtime Inputs

Use these in the runtime textarea.

## Regex: Expected Blocked With Default Rules

```text
Please contact Jordan at jordan.lee@example.com or 555-321-7788.
```

```text
The submitted tax form contains 123-45-6789.
```

## Regex: Expected Blocked With Custom Rules

```text
The onboarding record belongs to employee EMP-48291.
```

```text
Please review account ACCT-DEL-7842 before sending the report.
```

```text
The private support ticket is PRIV-928441.
```

## Regex: Expected Allowed

```text
The customer asked for store hours and general product availability.
```

```text
Please summarize the support case without names, emails, phone numbers, or IDs.
```

