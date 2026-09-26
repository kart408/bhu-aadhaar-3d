# Phase 16 — Generic property intake

Date: 2026-09-26

## Outcome

Property intake is no longer restricted to ABC Complex and Shop G-12. It accepts:

- any non-empty owner, property type, address and unit label;
- any valid 14-digit parent ULPIN;
- whole-number floors from `-5` through `100`;
- positive decimal length, width and height measurements.

Known demo units retain their directory placement. Unknown addresses and units
receive a stable position derived from their normalized text so repeated input
produces the same model. The UI and stored provenance label this
`DETERMINISTIC_OFFLINE_DEMO_PLACEMENT`; it is not presented as real geocoding,
surveying or proof that the property lies at that coordinate.

After registrar approval, a new ULPIN with no seed data receives its own stored
registration and becomes available through the isolated 3D model endpoint.
Tests cover arbitrary address/unit input, numeric floor conversion, deterministic
placement, and creation of a new ULPIN model after approval.
