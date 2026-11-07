# Release v1.0.12: Automated GitHub Release Workflow Permissions

## Summary
Version 1.0.12 grants `contents: write` permissions to `.github/workflows/docker-publish.yml`, enabling automated GitHub Release creation upon pushing version tags.

## Highlights
- **CI Permissions Fix**: Resolves HTTP 403 Forbidden (`Resource not accessible by integration`) by providing explicit write permissions to `${{ secrets.GITHUB_TOKEN }}` for the `softprops/action-gh-release@v2` step.
- All `v1.0.11` upstream reliability improvements (positional-only API arguments, guest agent argv tokenization, client-side cluster tasks slicing, and raw API lockdown toggle) are bundled.

## Docker Container
Built automatically by GitHub Actions:
- `ghcr.io/jelmervdm/proxmox-mcp:v1.0.12`
- `ghcr.io/jelmervdm/proxmox-mcp:latest`

