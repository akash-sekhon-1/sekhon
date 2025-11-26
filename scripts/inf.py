

"""
inf.py

1. This module is available publically at curl -O https://raw.githubusercontent.com/akash-sekhon-1/sekhon/main/scripts/cl9.py

So I can download it from anywhere globally and set up my system in seconds.


2. It offers multiple linux system scripts for auto installing many packages through options --basics and --ull_sekhon

"""

# ===========================
# IMPORTS
# ===========================

import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from textwrap import fill
from typing import Optional



# ===========================
# MARK: GLOBAL
# ===========================

HOME = os.path.expanduser("~")

SCRIPTER_NAME: str = "inf.py"
CURRENT_PATH = os.path.abspath(os.path.realpath(__file__))

SCRIPTER_DIR = os.path.join(HOME, ".local", "sekhon")
LOCAL_BASH_DIR = os.path.join(SCRIPTER_DIR, "bash")
LOCAL_TMP_DIR = os.path.join(SCRIPTER_DIR, "tmp")  # for atomic writes and tmp data

for _dir in (LOCAL_BASH_DIR, LOCAL_TMP_DIR):
    if not os.path.exists(_dir):
        os.makedirs(_dir, exist_ok=True)

# =========================
# MARK: GitHub 
# =========================

GITHUB_OWNER = "akash-sekhon-1"
GITHUB_REPO = "sekhon"
GITHUB_BRANCH = "main"

# Raw content base URL
GITHUB_RAW_BASE = (
    f"https://raw.githubusercontent.com/"
    f"{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/"
)

# Paths in repo
SELF_REMOTE_PATH = f"scripts/{SCRIPTER_NAME}"
CHECKSUMS_REMOTE_PATH = "checksums.json"



# ===========================
# MARK: UTILS CONST
# ===========================

COLOR_RESET = '\x1b[0m'
COLOR_MAP = {
    'blue':   '\x1b[38;5;33m',
    'cyan':   '\x1b[38;5;39m',
    'yellow': '\x1b[38;5;226m',
    'orange': '\x1b[38;5;208m',
    'red':    '\x1b[38;5;196m',
    'green':  '\x1b[38;5;46m',  # Bright lime green    
    'purple': '\x1b[38;5;93m',
    'violet': '\x1b[38;5;99m',
    'magenta': '\x1b[38;5;201m'

}





# =========================
# MARK: Internal helpers
# =========================

# ----------------------------------
def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# -----------------------------
def _fetch_checksums() -> dict:
    """
    Fetch checksums.json from the GitHub repo.
    Format: {"scripts/inf.py": "<hex>", "bash/ull.sh": "<hex>", ...}
    """
    url = GITHUB_RAW_BASE + CHECKSUMS_REMOTE_PATH
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "inf-self-update/1.0"}
    )
    try:
        with urllib.request.urlopen(req) as r:
            data = r.read()
    except urllib.error.URLError as e:
        raise RuntimeError(f"failed to fetch checksums: {e}") from e

    try:
        obj = json.loads(data.decode("utf-8"))
    except Exception as e:
        raise RuntimeError("checksums.json is invalid JSON") from e

    if not isinstance(obj, dict):
        raise RuntimeError("checksums.json must be a JSON object")

    return obj


# --------------------------------
def _atomic_download_with_sha256(
    url: str,
    expected_sha256_hex: str,
    dest_path: str,
    make_executable: bool = False
) -> None:
    """
    Download a file from `url` to `dest_path` atomically:
      - stream to tmp file in LOCAL_TMP_DIR
      - compute SHA-256 during download
      - verify checksum against expected_sha256_hex
      - verify Content-Length if present
      - fsync file and directory
      - os.replace into dest_path
      - optional chmod 0o755
    """

    # Ensure dest directory exists
    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

    tmp_path = os.path.join(
        LOCAL_TMP_DIR,
        os.path.basename(dest_path) + ".tmp"
    )

    # Prepare request
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "inf-self-update/1.0"}
    )

    # Preallocate buffer
    buf = bytearray(65536)
    mv = memoryview(buf)

    # Open tmp file atomically
    try:
        fd = os.open(tmp_path,
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                     0o600)
    except FileExistsError:
        # Stale file from previous crash
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        fd = os.open(tmp_path,
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                     0o600)

    h = hashlib.sha256()
    total = 0
    try:
        with os.fdopen(fd, "wb", closefd=True) as tmp_fp:
            try:
                with urllib.request.urlopen(req) as r:
                    cl_header = r.getheader("Content-Length")
                    expected_len = int(cl_header) if cl_header is not None else None

                    while True:
                        n = r.readinto(mv)
                        if not n:
                            break
                        chunk_view = mv[:n]
                        h.update(chunk_view)
                        tmp_fp.write(chunk_view)
                        total += n
            except Exception as e:
                raise RuntimeError(f"download failed: {e}") from e

            tmp_fp.flush()
            os.fsync(tmp_fp.fileno())

        # Content length check (if available)
        if expected_len is not None and total != expected_len:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise RuntimeError(
                f"incomplete download from {url}: got {total} bytes, "
                f"expected {expected_len}"
            )

        # SHA-256 check
        digest_hex = h.hexdigest()
        if digest_hex.lower() != expected_sha256_hex.lower():
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise RuntimeError(
                f"sha256 mismatch for {url}: got {digest_hex}, "
                f"expected {expected_sha256_hex}"
            )

        # fsync containing directory
        dir_fd = os.open(dest_dir or ".", os.O_DIRECTORY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)

        # Atomic replace
        os.replace(tmp_path, dest_path)

        if make_executable:
            os.chmod(dest_path, 0o755)

    except Exception:
        # Ensure tmp cleanup on any failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# =========================
# MARK: Public API 
# =========================

# ----------------------------
def update_self(checksums: Optional[dict[str, str]]=None, stats: bool=True) -> str:
    """
    Update inf.py from GitHub, using checksums.json for sha256 integrity.
    Returns the path to the updated script.
    """
    if checksums is None:
        checksums = _fetch_checksums()
    expected_sha = checksums.get(SELF_REMOTE_PATH)
    if not expected_sha:
        raise RuntimeError(
            f"no checksum entry for {SELF_REMOTE_PATH} in checksums.json"
        )

    # If already up to date, skip network
    if os.path.exists(CURRENT_PATH):
        local_sha = _sha256_file(CURRENT_PATH)
        if local_sha.lower() == expected_sha.lower():
            if stats:
                crint("Already the Latest version", 'green')
            return CURRENT_PATH

    remote_url = GITHUB_RAW_BASE + SELF_REMOTE_PATH
    _atomic_download_with_sha256(
        remote_url,
        expected_sha,
        CURRENT_PATH,
        make_executable=True
    )
    crint("Please restart the Program to use the latest version", 'orange')
    sys.exit(0)


# -----------------------------------------
def ensure_bash_script(repo_rel_path: str, checksums: dict[str, str]) -> Optional[str]:
    """
    Given a label in BASH_SCRIPTS, ensure the script is present locally
    under LOCAL_BASH_DIR, verified by sha256 from checksums.json.

    Returns the local absolute path.
    """
    expected_sha = checksums.get(repo_rel_path)
    if not expected_sha:
        return None

    dest_path = os.path.join(LOCAL_BASH_DIR, os.path.basename(repo_rel_path))

    # If exists and matches sha, just return
    if os.path.exists(dest_path):
        local_sha = _sha256_file(dest_path)
        if local_sha.lower() == expected_sha.lower():
            return dest_path

    remote_url = GITHUB_RAW_BASE + repo_rel_path
    _atomic_download_with_sha256(
        remote_url,
        expected_sha,
        dest_path,
        make_executable=True
    )

    return dest_path








# ===========================
# MARK: BASH DISPATCH
# ===========================

# -----------------------------
def launch_bash(path: str):
    try:
        os.chmod(path, 0o755)
        try:
            subprocess.run(["bash", path], check=False)
        except (KeyboardInterrupt, EOFError):
            crint("Exitting safely", 'orange')
    except Exception as e:
        crint(e, 'red')




# ===========================
# MARK: INPUT
# ===========================

def get_input(text, strip: bool = True, lower:bool=True) -> Optional[str]:
    """
    - If this returns None means you have to end the program immediately (gracefully)
    - Never use input directly in the program.
    - Raise SystemExit if the program left open for a whole day (like in some bg terminal) to prevent corruption and all
    - Handle Ctrl + C and Ctrl + D, offering graceful exit.
    """
    try: 
        from prompt_toolkit import PromptSession
        ptk_present = True
    except ModuleNotFoundError:
        ptk_present = False

    try:
        if ptk_present:
            r: str = PromptSession().prompt(text)
        else:
            r: str = input(text)

        if strip:
            r = r.strip()
        if lower:
            r = r.lower()

    except (KeyboardInterrupt, EOFError):
        return None
    return r






# ===========================
# MARK: OUTPUT
# ===========================

# -----------------------------------------
def clz(text: str, color: str) -> str:
    color_code = COLOR_MAP.get(color.strip().lower())
    return f"{color_code}{text}{COLOR_RESET}" if color_code else text


#--------------------------------------------------
def output(text: str, end='\n'):
    # Split on existing newlines and wrap each line independently
    _w = os.get_terminal_size().columns
    for paragraph in text.split('\n'):
        # Avoid wrapping empty lines (preserves spacing)
        if paragraph.strip() == '':
            print('', end=end)
        else:
            print(fill(paragraph, width=_w), end=end)             


# ---------------------------------------------------------
def crint(text: str, color: str='white', end='\n') -> None:
    """
    Colored print

    Accepted colors:
        - blue
        - cyan
        - yellow
        - orange
        - red
        - green
        - white
        - purple
        - violet
        - magenta

    If an invalid color is provided, the text is returned unmodified.
    """
    if color=='white':
        output(text, end=end)
    else:
        output(clz(text, color), end=end)
    return




# ===========================
# MARK: VALIDATION
# ===========================

def _validate_OPTS():
    for o in OPTS:
        vals = OPTS[o].keys()
        for f in MUST_FIELDS:
            if f not in vals:
                crint(f"[Invalid] {f} not present; OPTS -> {o}", 'red')
                sys.exit(1)

        if not isinstance(OPTS[o]['d'], str):
            crint(f"[INVALID] The d (description) must be a string; OPTS -> {o}", 'red')
            sys.exit(1)
        if not (isinstance(OPTS[o]['p'], str) or callable(OPTS[o]['p'])):
            crint(f"[INVALID] p (path) must a path or a callable; OPTS -> {o}", 'red')
            sys.exit(1)
        if OPTS[o]['w'] is not None and not isinstance(OPTS[o]['w'], str):
            crint(f"[INVALID] w (warning) must be None or string; OPTS -> {o}", 'red')
            sys.exit(1)

        dep = OPTS[o]['dep']
        if dep is not None and not isinstance(OPTS[o]['dep'], list):
            crint(f"[INVALID] d (dependencies) must be None or list[str]; OPTS -> {o}", 'red')
            sys.exit(1)
        
        if dep:
            for d in dep:
                if d not in OPTS:
                    crint(f"[INVALID] {d} is not a valid option. OPTS -> {o} -> {d}", 'red')
                    sys.exit(1)



# -----------------------------------------------
def _get_dep(option: str) -> Optional[list[str]]:
    return OPTS[option]['dep']

# --------------------------
def _help():
    for _o in OPTS:
        output(f"{clz(_o, 'magenta')} : {OPTS[_o]['d']}")



# ===========================
# MARK: ENTRY
# ===========================

# -------------------------------------------
def main():
    checksums = _fetch_checksums()
    update_self(checksums)

    _validate_OPTS()
    args = sys.argv[1:]

    # Filter args into valid_opts in OPTS order (canonical order)
    valid_opts: list[str] = []
    for o in OPTS:
        if o in args:
            valid_opts.append(o)
            args.remove(o)

    if args:
        crint(f"Discarding Invalid options: {' '.join(args)}", 'red')

    if not valid_opts:
        _help()
        sys.exit(1)

    # Dependency-aware resolution
    final_order: list[str] = []
    cancelled: set[str] = set()
    state: dict[str, int] = {opt: 0 for opt in valid_opts}  # 0 = unvisited, 1 = visiting, 2 = done

    # build a hierarychy table 
    def warn_check(opt) -> bool:
        """ 
        Only proceed if this returns True, otherwise user has cancelled 
        """ 
        warn = OPTS[opt]['w']
        if not warn:
            return True
        if get_input(f"{warn} Proceed? (y/n): ").strip().lower() != 'y':
            crint(f"Skipping {opt}", 'yellow')
            return False
        return True
    

    def visit(opt: str) -> bool:
        """
        DFS over dependencies restricted to valid_opts.

        Returns:
            True  -> opt scheduled or already scheduled successfully
            False -> opt (or one of its deps) was cancelled; caller should skip
        """
        st = state.get(opt, 0)

        # Already fully processed
        if st == 2:
            return opt not in cancelled

        # Visiting again while in-progress => cycle
        if st == 1:
            crint(f"[INVALID] Dependency cycle detected involving {opt}", 'red')
            sys.exit(1)

        # If already cancelled, propagate
        if opt in cancelled:
            return False

        state[opt] = 1  # mark visiting

        # Process deps first
        deps = _get_dep(opt) or []
        for d in deps:
            # Only enforce deps that are actually requested
            if d not in valid_opts:
                continue

            # If dep already cancelled, this opt must be cancelled too
            if d in cancelled:
                crint(f"Skipping {opt} because dependency {d} was cancelled", 'orange')
                cancelled.add(opt)
                state[opt] = 2
                return False

            # Recurse into dep
            if not visit(d):
                crint(f"Skipping {opt} because dependency {d} failed/cancelled", 'orange')
                cancelled.add(opt)
                state[opt] = 2
                return False

        # All deps handled successfully; now schedule this option (if not done)
        if opt not in final_order and opt not in cancelled:
            if not warn_check(opt):
                cancelled.add(opt)
                state[opt] = 2
                return False
            final_order.append(opt)

        state[opt] = 2
        return True

    # Resolve for each requested option in canonical order
    for opt in valid_opts:
        if opt in cancelled:
            continue
        if state.get(opt, 0) != 2:
            visit(opt)

    # Execute in resolved order
    for opt in final_order:
        p = OPTS[opt]['p']
        if callable(p):
            p()
            continue

        r = ensure_bash_script(p, checksums)
        if r is None:
            crint(f"no checksum entry for {p} in checksums.json; Skipping it", 'red')
            continue

        launch_bash(r)




# ===========================
# MARK: OPTS
# ===========================

MUST_FIELDS = [
    'd', # The description of the options, used in help
    'p', # Either a path to the script or a function that can called directly.
    'w', # [Warning] if not None, provides a warning with a custom message within, proceeds only if pressed y, other wise fails along with all child options, parent options still work
    'dep' # It is the dependencies of the options on the other options, if both are given together. Value is Optional[list[str]]
]

OPTS = {
    # ===================================================================
    # Core & Meta
    # ===================================================================
    '--help': {
        'd': "Show this help message and exit",
        'p': _help,
        'w': None,
        'dep': None
    },

    '--update': {
        'd': "Securely update inf.py to the latest version (SHA-256 verified from GitHub)",
        'p': update_self,
        'w': None,
        'dep': None
    },

    # ===================================================================
    # System Foundations
    # ===================================================================
    '--basics': {
        'd': "Install essential daily-driver tools: neovim, htop, tilix/terminator, "
             "gparted, tree, ripgrep, fd, xclip, curl/wget, 7zip, and more",
        'p': "bash/basics.sh",
        'w': None,
        'dep': None
    },

    '--ull_sekhon': {
        'd': "Install 150+ ultra-low-latency & systems-dev packages — full compiler toolchain, "
             "kernel headers, BPF/eBPF ecosystem, RDMA, DPDK, perf, bpftrace, clang+lldb, "
             "valgrind, systemtap, hwloc, numa, and debug symbols",
        'p': "bash/ull.sh",
        'w': "Extremely heavy install (~5-10 GB). Only enable if you're doing kernel/BPF/network/RDMA development.",
        'dep': None
    },

    '--code_force_ip4': {
        'd': "Force curl, dnf/apt, and all Microsoft repositories to use IPv4 only "
             "(fixes hanging downloads on broken IPv6 networks) (Fully idempotent)",
        'p': "bash/code_force_ip4.sh",
        'w': None,
        'dep': None
    },

    '--install_vscode': {
        'd': "Install or update Visual Studio Code (official Microsoft build) - "
             "works on Fedora, Ubuntu, Arch, and derivatives. Fully idempotent. Run --code_force_ip4 first if downloads hang or time out",
        'p': "bash/vscode.sh",
        'w': None,
        'dep': ['--code_force_ip4']
    },

    # ===================================================================
    # GNOME Enhancements
    # ===================================================================
    '--clipboard': {
        'd': "Install Clipboard Indicator GNOME extension — persistent clipboard history "
             "with search (the one everyone actually uses) (Fully idempotent)",
        'p': "bash/clipboard_indicator.sh",
        'w': None,
        'dep': None
    },

    '--dash-to-panel': {
        'd': "Install Dash to Panel GNOME extension — Windows-like taskbar with app icons, "
             "window titles, system tray, and workspace indicator (Fully idempotent)",
        'p': "bash/dash-to-panel.sh",
        'w': None,
        'dep': None
    },

    # ===================================================================
    # Browsers (all official repos, signed, updatable via package manager)
    # ===================================================================
    '--chrome': {
        'd': "Install Google Chrome Stable (official Google repository, auto-updating) (Fully idempotent)",
        'p': "bash/chrome.sh",
        'w': None,
        'dep': None
    },

    '--edge': {
        'd': "Install Microsoft Edge Stable (official Microsoft repository, auto-updating) (Fully idempotent)",
        'p': "bash/edge.sh",
        'w': None,
        'dep': None
    },

    '--vivaldi': {
        'd': "Install Vivaldi Browser (official Vivaldi repository, auto-updating — "
             "best for power users and tab hoarding) (Fully idempotent)",
        'p': "bash/vivaldi.sh",
        'w': None,
        'dep': None
    },
}

# ------------------------
if __name__ == "__main__":
    main()



