## User Story

As a maintainer relying on this toolkit, I need the public APIs, settings, and documentation to use inclusive
allowlist/blocklist terminology instead of allow/blacklist so that the feature surface stays aligned with our inclusive
language policy and existing functionality remains easy to configure.

## Context

We currently ship a `WhitelistEmailBackend`, `StructureTestValidator` settings named
`TEST_STRUCTURE_VALIDATOR_*_WHITELIST`, and a utility helper with `blacklisted_fields`. All of these expose the outdated
whitelist/blacklist terms through module names, class names, settings constants, and docs (`docs/features/mail.md`,
`docs/features/tests.md`, `docs/features/utils/model.md`).

## Business Value

Updating the terminology keeps our public API consistent with the stated language policy, prevents confusion for
adopters, and ensures documentation matches the code shipped in the latest release.

## Acceptance Criteria

- [ ] Search results for “whitelist”/“blacklist” in code, settings, and docs still in user-facing areas now talk about
  allowlist/blocklist instead.
- [ ] The email backend is shipped (and documented) as `AllowlistEmailBackend` with `EMAIL_BACKEND_DOMAIN_ALLOWLIST`
  while continuing to accept the old settings/class name for one release.
- [ ] The structure validator services/settings expose `TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST` and
  `..._MISPLACED_TEST_FILE_ALLOWLIST` along with safe fallbacks to the old settings for backward compatibility, and
  their docs describe the new names.
- [ ] The `object_to_dict` helper and its doc/tests now talk about `blocklisted_fields` and accept the old
  `blacklisted_fields` argument without breaking callers.

## Technical Tasks

- Backend:
    - Renamed mail backend: create `ambient_toolbox/mail/backends/allowlist_smtp.py` with `AllowlistEmailBackend`,
      rename helper methods/regex to reference “allowlist”, and update tests (`tests/mail/test_mail_backends.py`) and
      docs; keep the old `whitelist_smtp.py` module/class as a thin shim that re-exports the new backend while warning (
      if feasible) about the rename and still honors `EMAIL_BACKEND_DOMAIN_WHITELIST` for one release before
      deprecation.
    - Structure validator: update `ambient_toolbox/tests/structure_validator/test_structure_validator.py`, default
      settings (`ambient_toolbox/tests/structure_validator/settings.py`), and all tests (
      `tests/tests/structure_validator/test_test_structure_validator.py`) to use `allowlist` terminology for the
      file/misplaced settings and helpers; make the helper methods look for `TEST_STRUCTURE_VALIDATOR_*_ALLOWLIST` first
      and fall back to the old `*_WHITELIST`; add a small migration/adjustment in `settings.py` or service to keep
      existing installations working.
    - Utils helper: change `ambient_toolbox/utils/model.py` so it accepts `blocklisted_fields` (and internally maps the
      deprecated `blacklisted_fields` parameter to the new name), adjust `tests/test_utils_model.py` to assert the new
      parameter, and update any related imports.
- Frontend:
    - Update documentation: `docs/features/mail.md`, `docs/features/tests.md`, and `docs/features/utils/model.md` (plus
      any other affected docs) to describe the allowlist/blocklist names, the legacy aliases, and the configuration
      examples matching the renamed constants.
- Other:
    - Add a short note to `CHANGES.md` (or another release notes file) describing the terminology switch and the
      compatibility accommodations so integrators know what to update.

## Open Questions / Risks

- Risk: we need a smooth rename for the email backend import path. Decision: keep `ambient_toolbox.mail.backends.whitelist_smtp`
  as a shim for at least the next release and add deprecation warnings before removing it.
- Question resolved: we will emit deprecation warnings in code when old `*_WHITELIST` settings still appear so adopters know
  about the updated names.
- Coordination risk: no extra release-branch or automation work is expected because we assume existing deployments will continue
  honoring the legacy names during the transition.
