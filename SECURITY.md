# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security fixes only |
| < 0.5   | no        |

## Reporting a vulnerability

Email `security@synthetic-persona-forge.dev` with a PGP-encrypted report if
you can. Include: affected version, a minimal repro, and whether the issue is
in the persona pipeline, the backend adapters, or the native sidecars.

We aim to acknowledge within 72 hours and ship a patch within 14 days for
high-severity issues.

## Threat model

The forge handles:

- **API credentials** for voice/face/LLM backends. Stored in `config/local.toml`
  (gitignored) or the Windows Credential Manager via `keyring`. Never logged.
- **Generated persona assets** — face LoRAs, voice clones, image batches.
  These are treated as sensitive user data. They do not leave the machine
  unless an exporter is explicitly invoked.
- **Outbound calls** to platform APIs. All egress goes through
  `services/backends/` and is logged (URL + method only, never payload).

## Known non-issues

- The forge can generate personas that look like fictional people. That is
  the point. Impersonation of a real, identifiable person is a user
  responsibility and is called out in the CLI's `--acknowledge-impersonation`
  gate.
- Generated content is not moderated by the tool. Downstream platform
  moderation is the operator's problem.

## Hard line

Any use of this tool to generate sexual content involving minors is
prohibited and will not be supported, patched around, or discussed. Reports
of that nature get closed.