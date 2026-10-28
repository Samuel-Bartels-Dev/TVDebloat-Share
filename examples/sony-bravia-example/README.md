# Sony BRAVIA profile example

This folder is a **documentation example only**.

It is not a validated profile and must not be applied to a real TV.

The purpose is to show what TVDebloat should produce while an operator walks through the first Sony BRAVIA pilot.

## Files

- `discovery.json` — example output from live discovery
- `profile.toml` — example candidate profile built from discovery + operator review
- `NOTES.md` — example evidence/validation log

## How this becomes a real profile

On the real TV:

1. run preflight and probe;
2. discover the live packages;
3. create `profiles/sony/<real-model>/profile.toml`;
4. review packages with the operator;
5. keep uncertain packages in `review`;
6. preview the exact diff;
7. apply to one pilot only after approval;
8. physically validate;
9. record results in `NOTES.md`;
10. promote only after reboot/drift validation.

Real profiles belong under `profiles/sony/<model>/`, not in `examples/`.
