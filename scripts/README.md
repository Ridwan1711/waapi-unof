# scripts

Cross-platform helper scripts for setup and maintenance. Keep scripts small,
documented, and safe to re-run (idempotent where possible).

> Populated as needed across later phases.

## Intended contents

```
scripts/
├── setup.sh / setup.ps1     # bootstrap a dev environment / .env
├── seed.py                  # seed demo workspace, user, API key
└── backup.sh                # back up postgres + session volumes
```

## Conventions

- Shell scripts use LF endings and a `set -euo pipefail` preamble.
- PowerShell variants (`.ps1`) are provided where Windows support matters.
- No secrets in scripts — read from environment variables.
