#!/usr/bin/env bash
# Invoked by skwd-helm after skwd-walld has committed a wallpaper change.
set -Eeuo pipefail

path="${1:-}"
[[ -n "$path" ]] || exit 0
path="${path#file://}"

state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/quickshell/user/generated"
lock_file="$state_dir/skwd-wall-theme.lock"
last_file="$state_dir/skwd-wall-theme-path"
mkdir -p "$state_dir"

exec 9>"$lock_file"
flock -x 9
[[ "$(cat "$last_file" 2>/dev/null || true)" == "$path" ]] && exit 0

script="$HOME/.config/quickshell/ii/scripts/colors/switchwall.sh"
[[ -x "$script" ]] || exit 1
"$script" --skwd-wall --image "$path"
printf '%s' "$path" > "$last_file"
