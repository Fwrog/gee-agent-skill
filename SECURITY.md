# Security Policy

## Supported Versions

`gee-agent-skill` is currently a pre-1.0 research and portfolio project. Security fixes should target the current `main` branch unless a release branch is created.

## Credential Boundary

This repository does not provide Google accounts, Earth Engine access, Google Cloud projects, OAuth tokens, service account JSON, private keys, refresh tokens, client secrets, or credential paths.

Never commit or share:

- `.env` files;
- Earth Engine OAuth credentials;
- Google application-default credentials;
- service account JSON;
- refresh tokens;
- private keys, PEM files, or P12 files;
- local credential paths;
- exported run traces that contain credential material.

Dry-run and planning commands should work without credentials. Live Earth Engine commands require user-owned local authentication, a Google Cloud project, and explicit `--confirm-live`.

## Live Execution Safety

Live export commands must remain gated by:

```bash
--project <project-id> --confirm-live
```

Preflight may contact Earth Engine but must not create export tasks. Treat export submission as workflow evidence, not scientific validation.

## Reporting A Vulnerability

Open a private report or contact the maintainers with:

- affected command or file;
- minimal reproduction steps;
- whether any credential material may have been exposed;
- expected and actual behavior.

Do not include secrets in the report. Redact project ids, account identifiers, credential paths, tokens, and private keys.

## Maintainer Checklist

- Confirm the issue without requesting secrets.
- Add or update tests when the issue affects CLI boundaries, trace writing, or live export gating.
- Check generated traces for credential leakage.
- Update README, SKILL.md, or docs when the safe operating boundary changes.
