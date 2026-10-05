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
