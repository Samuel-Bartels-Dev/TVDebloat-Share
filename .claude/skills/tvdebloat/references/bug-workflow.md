# Bug workflow

When an unexpected failure occurs:

1. stop additional risky changes
2. preserve recovery data
3. rerun preflight
4. restore if required TV functionality broke
5. generate a local redaction-ready report with tvdebloat bug-report
6. redact network/account/device-identifying secrets
7. submit through the repository bug workflow
8. once understood, add:
   - regression test when practical
   - profile/NOTES update for device-specific behavior
   - preflight/safety detection if the condition is detectable

Do not solve a device-specific failure by blindly broadening exceptions.
