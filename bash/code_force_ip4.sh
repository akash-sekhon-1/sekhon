# --code_force_ip4 (works for any dnf/apt-based system)

#!/usr/bin/env bash
set -euo pipefail

# Purpose:
#   Force curl, dnf/apt, and all Microsoft-repo-related traffic
#   to use IPv4 only (workaround for IPv6 stalls/hangs).
#
# Idempotent:
#   Will not duplicate lines, always safe to rerun.


# FEDORA
if command -v dnf >/dev/null 2>&1; then
    echo -e "\nDNF Based System Detected\n"

    ###############################################################################
    # 1. Force system resolver to prefer IPv4 (via gai.conf)
    ###############################################################################

    GAI_CONF="/etc/gai.conf"
    LINE="precedence ::ffff:0:0/96  100"

    if ! grep -qF -- "$LINE" "$GAI_CONF"; then
        echo "$LINE" | sudo tee -a "$GAI_CONF" >/dev/null
    fi

    ###############################################################################
    # 2. Force curl to always use IPv4 unless overridden
    ###############################################################################

    CURL_CONF="/etc/curlrc"
    CURL_LINE="--ipv4"

    sudo touch "$CURL_CONF"
    if ! grep -qF -- "$CURL_LINE" "$CURL_CONF"; then
        echo "$CURL_LINE" | sudo tee -a "$CURL_CONF" >/dev/null
    fi

    ###############################################################################
    # 3. Patch Microsoft yum repo definitions to enforce IPv4 explicitly
    ###############################################################################

    REPO_PATH="/etc/yum.repos.d"
    REPO_PATTERN="packages.microsoft.com"

    for f in "$REPO_PATH"/*.repo; do
        [ -e "$f" ] || continue
        if grep -qF "$REPO_PATTERN" "$f"; then
            # Ensure dnf resolves repo hosts to IPv4 for this repo
            if ! grep -qF "ip_resolve=4" "$f"; then
                sudo sed -i '/^baseurl=/a ip_resolve=4' "$f"
            fi
        fi
    done

    ###############################################################################
    # 4. Reload dnf metadata (freshly forced into IPv4 mode)
    ###############################################################################
    sudo dnf clean all >/dev/null 2>&1 || true

    echo "✔ Microsoft repo forced to IPv4 for curl + dnf."
    echo "✔ System resolver prefers IPv4. Idempotent changes applied."


    
# UBUNTU
elif command -v apt-get >/dev/null 2>&1; then
    echo -e "\nDebian/Ubuntu Based System Detected\n"

    ###############################################################################
    # 1. Force system resolver to prefer IPv4 (via gai.conf)
    ###############################################################################

    GAI_CONF="/etc/gai.conf"
    LINE="precedence ::ffff:0:0/96  100"

    if ! grep -qF -- "$LINE" "$GAI_CONF"; then
        echo "$LINE" | sudo tee -a "$GAI_CONF" >/dev/null
    fi

    ###############################################################################
    # 2. Force curl to always use IPv4 unless overridden
    ###############################################################################

    CURL_CONF="/etc/curlrc"
    CURL_LINE="--ipv4"

    sudo touch "$CURL_CONF"
    if ! grep -qF -- "$CURL_LINE" "$CURL_CONF"; then
        echo "$CURL_LINE" | sudo tee -a "$CURL_CONF" >/dev/null
    fi

    ###############################################################################
    # 3. Force APT to prefer IPv4 for all HTTP(S) acquisition
    ###############################################################################

    APT_CONF_DIR="/etc/apt/apt.conf.d"
    FORCE_FILE="$APT_CONF_DIR/99force-ipv4"
    FORCE_LINE='Acquire::ForceIPv4 "true";'

    sudo mkdir -p "$APT_CONF_DIR"

    if [ -f "$FORCE_FILE" ]; then
        if ! grep -qF -- "$FORCE_LINE" "$FORCE_FILE"; then
            echo "$FORCE_LINE" | sudo tee "$FORCE_FILE" >/dev/null
        fi
    else
        echo "$FORCE_LINE" | sudo tee "$FORCE_FILE" >/dev/null
    fi

    ###############################################################################
    # 4. Optional: touch Microsoft list entries if present (no-op if absent)
    ###############################################################################
    MS_PATTERN="packages.microsoft.com"
    for f in /etc/apt/sources.list /etc/apt/sources.list.d/*.list; do
        [ -e "$f" ] || continue
        if grep -qF "$MS_PATTERN" "$f"; then
            echo "→ Microsoft APT source detected in: $f"
        fi
    done

    ###############################################################################
    # 5. Reload apt metadata (now IPv4 forced)
    ###############################################################################
    sudo apt-get update -y || true

    echo "✔ APT forced to IPv4 via Acquire::ForceIPv4."
    echo "✔ curl/system resolver adjusted. Idempotent changes applied."


else
    echo -e "\nThis action only supports DNF and Debian-based (apt) systems.\n"
fi