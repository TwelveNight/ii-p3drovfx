#!/usr/bin/env bash
# Keep reconnecting across daemon restarts; skwd-walld remains the only renderer.
set -Eeuo pipefail

# Quickshell and Hyprland can be started from a display manager without the
# variables inherited by a terminal. skwd-helm's socket lives in this runtime.
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-1}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
export ILLOGICAL_IMPULSE_VIRTUAL_ENV="${ILLOGICAL_IMPULSE_VIRTUAL_ENV:-$XDG_STATE_HOME/quickshell/.venv}"

hook="$HOME/.config/quickshell/ii/scripts/colors/skwd-wall-theme-hook.sh"
while true; do
    current="$(skwd-helm current --json 2>/dev/null | jq -r '.outputs[0].path // empty' || true)"
    [[ -n "$current" ]] && "$hook" "$current" || true
    skwd-helm watch --exec "$hook %path%" || true
    sleep 3
done
