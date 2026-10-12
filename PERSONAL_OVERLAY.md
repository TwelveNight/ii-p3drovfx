# Personal overlay

This branch tracks the upstream `dev` branch plus the local desktop customizations.

Keep upstream changes on `origin/dev`; keep personal behavior in `dots/.config/hypr/custom/`.
Alt+Tab uses the upstream `WindowSwitcher`; the personal switcher has been removed.
Update this branch with:

```bash
git fetch origin dev
git rebase origin/dev
```

If a conflict occurs, preserve personal behavior in `dots/.config/hypr/custom/` and
integrate upstream changes by intent. Keep the upstream window switcher.

The overlay is not installed directly by this branch; deploy it through the personal
chezmoi repository after reviewing the diff.

## Quickshell installer ownership

Both the legacy `./setup install-files --core` path and the experimental file
installer sync only `~/.config/quickshell/ii`. Their `rsync --delete` removes
obsolete II files while preserving sibling shells such as `inir`, along with
shared parent files. Keep this boundary when merging upstream installer changes.
The `setup-ii-p3drovfx.sh` wrapper already deploys to the II subdirectory.

Regression check (requires Python 3, Bash, rsync, yq and envsubst):

```sh
python3 scripts/test-quickshell-install-boundary.py
```
