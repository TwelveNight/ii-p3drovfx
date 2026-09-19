# Personal overlay

This branch tracks the upstream `dev` branch plus the local desktop customizations.

Keep upstream changes on `origin/dev`; keep personal behavior in `dots/.config/hypr/custom/`
and the `AltTabSwitcher.qml` module. Update this branch with:

```bash
git fetch origin dev
git rebase origin/dev
```

If a conflict occurs, prefer the upstream version for files outside the overlay and
the personal version for `dots/.config/hypr/custom/` and `AltTabSwitcher.qml`.

The overlay is not installed directly by this branch; deploy it through the personal
chezmoi repository after reviewing the diff.
