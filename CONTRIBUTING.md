# Contributing to proxmox-mcp

> **Note**: This is a fork maintained by `@jelmervdm`. If you are looking to contribute to the original upstream project, please visit [GethosTheWalrus/proxmox-mcp](https://github.com/GethosTheWalrus/proxmox-mcp).

Thanks for your interest in contributing! This document covers everything you need to get started.

## Getting Started

```bash
git clone https://github.com/jelmervdm/proxmox-mcp.git
cd proxmox-mcp

python3 -m venv venv
source venv/bin/activate

pip install -e .
pip install -r requirements-dev.txt
pip install pre-commit
pre-commit install
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Quality

This project enforces linting, type checking, and formatting via pre-commit hooks. They run automatically on `git commit` once installed. You can also run them manually:

```bash
pre-commit run --all-files
```

Individual tools:

```bash
flake8 src/proxmox_mcp/   # linting
mypy src/proxmox_mcp/     # type checking
black src/proxmox_mcp/    # formatting
```

## Submitting a Pull Request

1. Fork the repo and create a branch from `main`
2. Make your changes, including tests for any new behaviour
3. Ensure all checks pass (`pytest`, `flake8`, `mypy`, `black`)
4. Open a PR against `main`

## Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for clean git history. Please follow the format:

| Prefix | When to use |
|--------|-------------|
| `fix:` | A bug fix |
| `feat:` | A new feature |
| `feat!:` or `BREAKING CHANGE:` in footer | A breaking API change |
| `chore:`, `docs:`, `test:`, `ci:`, `refactor:` | Everything else |

Examples:

```
feat: add support for Ceph pool management
fix: handle missing SSL cert gracefully
feat!: rename PROXMOX_HOST env var to PROXMOX_ADDRESS

BREAKING CHANGE: PROXMOX_HOST has been renamed to PROXMOX_ADDRESS
```

## Releasing

Releases and Docker container images (`ghcr.io/jelmervdm/proxmox-mcp`) are created for this repository via GitHub Releases and GitHub Actions:

1. Tag the release or run `gh release create vX.Y.Z`
2. The GitHub Action workflow (`docker-publish.yml`) builds and publishes the multi-platform Docker container image to GHCR automatically when tags or updates to `main` are pushed.

## Security

Please do not open public issues for security vulnerabilities. See [SECURITY.md](SECURITY.md) for the responsible disclosure process.
