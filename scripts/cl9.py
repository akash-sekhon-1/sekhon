

"""
cl9.py

1. This module is available publically at curl -O https://raw.githubusercontent.com/akash-sekhon-1/sekhon/main/scripts/cl9.py

2. I can download it from anywhere globally and set up my system in seconds. This script is meant to be strictly stand-alone. 

3. This is for PERSONAL USE ONLY
"""

# ===========================
# IMPORTS
# ===========================

import argparse
import base64
import ctypes
import ctypes.util
import datetime
import getpass
import hashlib
import hmac
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from getpass import getuser
from pathlib import Path
from socket import gethostname
from textwrap import fill
from typing import Callable, Dict, Iterable, Mapping, NewType, Optional





# annotate
S3Key = NewType("S3Key", str)



# ===========================
# GLOBAL
# ===========================
DELTA_VERSION: str = "2.1.1"

PC_LOGIN_NAME: str = "akash@n0"
N1_LOGIN_NAME: str = "akash@n1"
HOSTNAME: str = gethostname()
LOGIN_NAME: str = f"{getuser()}@{HOSTNAME}" # fast wifi PC where compaction happens automatically

MAIN_PC: bool = PC_LOGIN_NAME == LOGIN_NAME
N1_PC: bool = N1_LOGIN_NAME == LOGIN_NAME
HOME: Path = Path.home()


THIS_FILE = Path(__file__).resolve()
DEV_ROOT = HOME / "cl9_dev" / "m" / "cl9.py"

if ((MAIN_PC or N1_PC) and (HOME / "cl9_dev").exists() and THIS_FILE == DEV_ROOT):
    print("DEVELOPMENT MODE ON")
    PROGRAM_NAME = 'cl9_dev'
    DEV_PC = True
else:
    PROGRAM_NAME = 'cl9'
    DEV_PC = False

try:
    CPU_COUNT: int = os.cpu_count() or 10
except:
    CPU_COUNT: int = 10



# ===========================
# MARK: PATH CONST
# ===========================

def _discover_main_dir() -> Path:
    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "dispatch.py").is_file() and (candidate / "pyproject.toml").is_file():
            return candidate
    raise RuntimeError(f"Unable to discover repo root from {here}")


# Root
LOCAL_CL9_DIR           = HOME / PROGRAM_NAME
LOCAL_ALIAS_PATH        = HOME / ".cl9"
LOCAL_DUSTBIN           = HOME / "AD" / "AD_4M"


# Core SubDir
LOCAL_MAIN_DIR    = _discover_main_dir()
LOCAL_JSON_DIR    = LOCAL_CL9_DIR / "j"
LOCAL_TMP_DIR     = LOCAL_CL9_DIR / "tmp"
LOCAL_FLAGS_DIR   = LOCAL_CL9_DIR / "flags"
LOCAL_BAK_DIR     = LOCAL_CL9_DIR / "bak"
LOCAL_DEV_DIR     = LOCAL_CL9_DIR / "dev"
LOCAL_MAIN_DEV_DIR = LOCAL_MAIN_DIR / "dev"

# non-cl9 roots
LOCAL_MANY_DIR    = HOME / "many"
LOCAL_SPEECH_DIR  = HOME / ".cache" / "cl9" / "speech"
LOCAL_CL9_NATIVE_DIR = HOME / "cl9" / "native"
SEP_NATIVE_DEV_BUILD_DIR = LOCAL_MAIN_DEV_DIR / "build"
SEP_NATIVE_CMAKE_BUILD_DIR = (
    LOCAL_MAIN_DEV_DIR / "cmake-build" if DEV_PC else LOCAL_CL9_NATIVE_DIR / ".cmake-build"
)
SEP_NATIVE_INSTALL_DIR = SEP_NATIVE_DEV_BUILD_DIR if DEV_PC else LOCAL_CL9_NATIVE_DIR


# Bases
LOCAL_BASES_DIR   = LOCAL_JSON_DIR / "b"
LOCAL_MAIN_BASES_DIR = LOCAL_BASES_DIR / "m"
LOCAL_DELTAS_DIR     = LOCAL_BASES_DIR / "d"
LOCAL_VERSION_DIR    = LOCAL_BASES_DIR / "v"
LOCAL_PENDING_DIR     = LOCAL_BASES_DIR / "p"
LOCAL_SYNC_TS_FILE = LOCAL_BASES_DIR / ".last_sync_ts.txt"

# cache
LOCAL_MAIN_CACHE_PATH = LOCAL_JSON_DIR / ".all_json_cache.json.gz"

# automated backups
LOCAL_BACKUPS_DIR = LOCAL_CL9_DIR / "backups"
LOCAL_FILES_BU_DIR   = LOCAL_CL9_DIR / "automated_backups" / "flashcards_all"
LOCAL_SCRIPTS_BU_DIR = LOCAL_CL9_DIR / "automated_backups" / "scripts"



# Extras
LOCAL_CLEANUP_INFO_FILE = LOCAL_JSON_DIR / "dir_and_prefix_cleanup_info" # contains last ts for bak cleanup and speech cleanup

LOCAL_DUP_CHECK_JSON   = LOCAL_JSON_DIR / "duplication_check_file.json"
LOCAL_T_DUP_CHECK_JSON = LOCAL_JSON_DIR / "task_dup_check.json"
LOCAL_LOG_PATH         = LOCAL_JSON_DIR / "log_err.txt"
LOCAL_CAREER_NEWS      = LOCAL_JSON_DIR / "career_news.json"
LOCAL_CREDS_PATH       = LOCAL_JSON_DIR / ".creds"
LOCAL_BABEL_PATH       = LOCAL_JSON_DIR / "babel_draw.json.gz"
LOCAL_MAKE_OFFLINE_PATH = LOCAL_JSON_DIR / ".make_offline.txt"
LOCAL_S3_LISTING_STATS_PATH = LOCAL_JSON_DIR / ".s3_listing_stats.json"

LOCAL_TEXT_HISTORY = LOCAL_JSON_DIR / ".text_history.json.gz" # THIS path is also mentioned in ins_adder.py (not imported to keep that fast) # has two keys, 'last_sync': ts and 'history': {hash: date}


# Scripts
LOCAL_CL9_NAME = "cl9.py"
LOCAL_INF_NAME = "inf.py"
LOCAL_CL9_PATH = LOCAL_MAIN_DIR / LOCAL_CL9_NAME
LOCAL_INF_PATH = LOCAL_MAIN_DIR / LOCAL_INF_NAME
LOCAL_BASH_DIR = LOCAL_MAIN_DIR / "bash"


# Termux
IS_TERMUX = "com.termux" in str(HOME)
LOCAL_TERMUX_REC_DIR     = HOME / "storage" / "music" / "Recordings"
LOCAL_TERMUX_ST_REC_DIR  = LOCAL_TERMUX_REC_DIR / "Standard Recordings"



# Flags

SEP_NATIVE_PENDING_FLAG = LOCAL_FLAGS_DIR / "sep_native.pending"


DIRS_TO_CREATE: tuple[Path] = (
    LOCAL_BAK_DIR,
    LOCAL_BASES_DIR,
    LOCAL_CL9_DIR,
    LOCAL_DELTAS_DIR,
    LOCAL_DUSTBIN,
    LOCAL_FILES_BU_DIR,
    LOCAL_FLAGS_DIR,
    LOCAL_JSON_DIR,
    LOCAL_MAIN_BASES_DIR,
    LOCAL_MAIN_DIR,
    LOCAL_MAIN_DEV_DIR,
    LOCAL_MANY_DIR,
    LOCAL_PENDING_DIR,
    LOCAL_SCRIPTS_BU_DIR,
    LOCAL_SPEECH_DIR,
    LOCAL_TMP_DIR,
    LOCAL_VERSION_DIR,
    LOCAL_BACKUPS_DIR,
    LOCAL_DEV_DIR
)


for d in DIRS_TO_CREATE:
    if not d.is_dir():
        if d.exists():
            try:
                d.unlink()
            except:
                pass
        d.mkdir(parents=True, exist_ok=True)



# ===========================
# MARK: AWS CONST
# ===========================
AWS_REQ_KEYS = {
    "PRIVATE_AWS_ACCESS_KEY_ID": "The AWS access key id",
    "PRIVATE_AWS_SECRET_ACCESS_KEY": "Secret Access Key",
    "PRIVATE_BUCKET_NAME": "The name of the private bucket where all the modules and flashcards data will be stored",
    "PRIVATE_BUCKET_REGION": "Region of the private bucket. Example: ap-south-1",

    "GROQ_KEY": "API key of Groq LLM",
    "GITHUB_PAT": "GitHub Token for storing a public version of cl9.py and inf.py (and bash sripts)",
    "SUDO_PASSWORD": "The sudo password for this device."
}

CREDS_EXIT_WORDS = {"aban", "end", "exit", "ooo", "q", "quit"}
CREDS_SHOW_FULL_KEYS = {
    "PRIVATE_BUCKET_NAME",
    "PRIVATE_BUCKET_REGION",
}
CREDS_SESSION_TIMEOUT_SEC = 10 * 60


def _normalize_cred_lookup_key(text: str) -> str:
    return text.strip().lower().replace("-", "_").replace(" ", "_")


def _build_cred_aliases() -> dict[str, str]:
    aliases: dict[str, str] = {}
    for key in AWS_REQ_KEYS:
        short = key.removeprefix("PRIVATE_")
        for variant in {key, key.lower(), short, short.lower()}:
            aliases[_normalize_cred_lookup_key(variant)] = key
    aliases[_normalize_cred_lookup_key("aws_access_key")] = "PRIVATE_AWS_ACCESS_KEY_ID"
    aliases[_normalize_cred_lookup_key("aws_secret_key")] = "PRIVATE_AWS_SECRET_ACCESS_KEY"
    aliases[_normalize_cred_lookup_key("bucket")] = "PRIVATE_BUCKET_NAME"
    aliases[_normalize_cred_lookup_key("region")] = "PRIVATE_BUCKET_REGION"
    aliases[_normalize_cred_lookup_key("github")] = "GITHUB_PAT"
    aliases[_normalize_cred_lookup_key("groq")] = "GROQ_KEY"
    aliases[_normalize_cred_lookup_key("sudo")] = "SUDO_PASSWORD"
    return aliases


CREDS_KEY_ALIASES = _build_cred_aliases()


AWS_SCRIPTS_PRE: S3Key  = "scripts/"
AWS_JSON_PRE: S3Key     = "j/"
AWS_BASES_PRE: S3Key    = "j/b/"
AWS_AWS_PRE: S3Key = "aws/"
AWS_SPEECH_PRE: S3Key = "speech/"
AWS_MANY_PRE: S3Key = "many/" # many/n0, many/n1, ...
AWS_DUSTBIN30_PRE: S3Key = "dustbin30/"

AWS_MAIN_PRE: S3Key        = f"{AWS_BASES_PRE}m/"
AWS_DELTAS_PRE: S3Key      = f"{AWS_BASES_PRE}d/"
AWS_VERSION_PRE: S3Key     = f"{AWS_BASES_PRE}v/" # will contain an empty file inside like 1735252.txt

AWS_TEXT_HISTORY: S3Key = f"{AWS_JSON_PRE}.text_history.json.gz"
AWS_CLIP_KEY: S3Key = f"{AWS_JSON_PRE}.clips.json.gz"

AWS_LAST_NEWS_KEY: S3Key = "buffers/last_career_news_saved.txt"
AWS_CAREER_NEWS_KEY: S3Key = "buffers/career_newsv2.json.gz"

# has two keys, 'last_sync': ts and 'history': {hash: date}


AWS_TGZ_KEY: S3Key  = f"{AWS_SCRIPTS_PRE}complete_flashcard_program.tgz"
AWS_CL9_KEY: S3Key = f"{AWS_SCRIPTS_PRE}{LOCAL_CL9_NAME}"
AWS_INF_KEY: S3Key = f"{AWS_SCRIPTS_PRE}{LOCAL_INF_NAME}"


# ===========================
# MARK: TIME CONST
# ===========================

TIME_FMT: str = "%Y-%m-%d_%H:%M:%S"
DATE_FMT: str = "%Y-%m-%d"
MONTH_FMT: str = '%Y-%m'

OFFLINE_DEFAULT_DURATION_MINUTES = 120   # 2 hours
OFFLINE_MAX_DURATION_MINUTES = 1440      # 24 hours max

# ===========================
# MARK: CRYPTO CONST
# ===========================

# ----------------------------------------------
def _cache_path() -> Path:
    run_dir: Path = Path("/run/user") / str(os.getuid())
    if run_dir.is_dir():
        return run_dir / f"{PROGRAM_NAME}_passcache"
    return Path(tempfile.gettempdir()) / f"{PROGRAM_NAME}_passcache" # for termux



MAGIC = b'KVD1'
SALT_LEN = 16
NONCE_LEN = 12
PBKDF2_ITERS = 200_000
KEY_TTL_SEC = 60 * 60 * 12
KEY_CACHE = _cache_path()
SBOX = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
]
_R_GHASH = 0xE1000000000000000000000000000000

# Keyring special IDs (from linux/keyctl.h)
KEY_SPEC_SESSION_KEYRING = -3
KEY_SPEC_USER_KEYRING    = -4

# keyctl commands (from uapi/linux/keyctl.h)
KEYCTL_SEARCH      = 10
KEYCTL_READ        = 11
KEYCTL_SET_TIMEOUT = 15

_KEYRING_DESC = f"cl9_kcache_{PROGRAM_NAME}".encode()
_KEYRING_TYPE = b"user"

_keyring_available_cached: Optional[bool] = None
_libkeyutils = None
_libc = None




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



# ===========================
# MARK: NATIVE DISPATCH
# ===========================

def backup_so_files() -> list[tuple[Path, Path]]:
    """Returns list of (src_path, tmp_path) tuples to preserve structure"""
    backups: list[tuple[Path, Path]] = []
    main_dir = LOCAL_MAIN_DIR
    tmp_dir = LOCAL_TMP_DIR

    # Backup .so files from main_dir
    for file in main_dir.iterdir():
        if file.is_file() and file.name.endswith('.so'):
            tmp_path = tmp_dir / file.name
            try:
                file.copy(tmp_path, preserve_metadata=True)
            except AttributeError:
                shutil.copy2(file, tmp_path)
            backups.append((file, tmp_path))

    return backups


def restore_so_files(backups: list[tuple[Path, Path]]) -> None:
    """Restore each file to its original location"""
    for original_path, tmp_path in backups:
        try:
            tmp_path.copy(original_path, preserve_metadata=True)
        except AttributeError:
            shutil.copy2(tmp_path, original_path)

            

# ----------------------
def get_cl9() -> bool: # --cl9
    if DEV_PC:
        crint("This operation is not allowed on the DEV MODE", 'red')
        return False

    __creds = get_creds()
    S3, BUCKET_NAME = get_s3_bucket(__creds)

    # backup the previous stuff first
    tmp_so_files = backup_so_files()
    before_backup_path = LOCAL_SCRIPTS_BU_DIR / datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    before_backup_path.mkdir(parents=True, exist_ok=True)

    shutil.copytree(LOCAL_MAIN_DIR, before_backup_path, dirs_exist_ok=True)  # Copies everything
    print("Current backup taken")

    print("\n[init] Fetching program archive from S3 ...")
    tgz = _download_bytes_from_s3(BUCKET_NAME, AWS_TGZ_KEY, S3)

    with tempfile.TemporaryDirectory(prefix="flashcards_unpack_") as tmpd:
        tmpd = Path(tmpd)
        print("[init] Extracting archive")
        _extract_tgz_bytes_to_dir(tgz, tmpd) # updated too to handle Path
        managed_roots = _sync_manifest_roots(tmpd)

        print("[init] Cleaning managed roots in target directory:", ", ".join(managed_roots))
        _purge_selected_entries(LOCAL_MAIN_DIR, managed_roots)

        # Copy all extracted contents into main_path
        for src in tmpd.iterdir():
            if src.name == ".cl9_sync_manifest.json":
                continue
            dst = LOCAL_MAIN_DIR / src.name
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)


    restore_so_files(tmp_so_files)
    
    # Remove previous versions
    for v in LOCAL_VERSION_DIR.iterdir():
        if v.is_file():
            v.unlink(missing_ok=True)
        elif v.is_dir():
            shutil.rmtree(v)
        else:
            crint(f"Error! Invalid path: {v}", 'red')


    aws_versions: list[S3Key] = list_s3_objects(AWS_VERSION_PRE, BUCKET_NAME, S3)
    if len(aws_versions) == 1: # usual case
        version_key = aws_versions[0]
    elif len(aws_versions) > 1:
        version_key = max(aws_versions, key=lambda x: float(x.removeprefix('v').split('_')[0]))
    else:
        print(f"[Error] No version file found in S3. Please run update_sep.py from the host device to create one")
        return False

    local_version_dst: Path = LOCAL_VERSION_DIR / version_key.split('/')[-1]
    if get_file_s3(version_key, local_version_dst, BUCKET_NAME, S3):
        print('version updated successfully.')
        print('To install deps and aliases, Run python3 ~/cl9/m/dispatch.py --all')
    else:
        print("[Error] Failed to download the latest version")
        return False

    print("\n[init] Update complete.")
    return True






# ===========================
# MARK: INPUT/CLIP
# ===========================

# -----------------------------
def getclip(warn_tty: bool=True, verbose: bool=False) -> Optional[str]: # copy paste it from utils.py which has the original version
    """
    Robust clipboard getter.

    Priority:
        1. pyperclip.paste
        2. wl-paste
        3. xclip
        4. termux-clipboard-get (Termux)
        5. pbpaste (for Mac OS)
        6. tmux (if running in tmux)
    Returns:
        str on success,
        None on failure.
    Never raises.
    """

    # 1. pyperclip
    try:
        import pyperclip # type: ignore
        data = pyperclip.paste() 
        if verbose:
            print("Using Native Pyperclip")
        return data if isinstance(data, str) else None
    except Exception:
        pass



    # 2. wl-paste
    wlpaste_bin = shutil.which("wl-paste") 
    if wlpaste_bin:
        try:
            proc = subprocess.run(
                [wlpaste_bin],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False
            )
            if proc.returncode == 0:
                if verbose:
                    print("using wl-paste")
                return proc.stdout.decode(errors="replace")
        except Exception:
            pass


    # 3. xclip
    xclip_bin = shutil.which("xclip") 
    if xclip_bin:
        try:
            proc = subprocess.run(
                [xclip_bin, "-selection", "clipboard", "-o"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False
            )
            if proc.returncode == 0:
                if verbose:
                    print("using xclip")
                return proc.stdout.decode(errors="replace")
        except Exception:
            pass

    # 4. Termux
    termux_bin = shutil.which("termux-clipboard-get")
    if termux_bin:
        try:
            proc = subprocess.run(
                [termux_bin],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False
            )
            if proc.returncode == 0:
                if verbose:
                    print("using termux get")
                return proc.stdout.decode(errors="replace")
        except Exception:
            pass

    # 5. Mac OS
    pbpaste_bin = shutil.which("pbpaste")
    if pbpaste_bin:
        try:
            proc = subprocess.run(
                [pbpaste_bin],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False
            )
            if proc.returncode == 0:
                if verbose:
                    print("Using pbpaste")
                return proc.stdout.decode(errors="replace")
        except Exception:
            pass


    # 6. tmux (if running in tmux tty, last fallback) 
    if 'TMUX' in os.environ:
        tmux_bin = shutil.which("tmux")
        if tmux_bin:
            try:
                # show-buffer outputs the latest (top) buffer
                proc = subprocess.run(
                    [tmux_bin, "show-buffer"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
                if proc.returncode == 0:
                    if verbose:
                        print("using TMUX")
                    if warn_tty:
                        print("Pasted from tmux load-buffer")
                    return proc.stdout.decode(errors="replace")
            except Exception:
                pass

    # 7. Explicit SSH controller clipboard hook
    if os.environ.get("SSH_CONNECTION") or os.environ.get("SSH_CLIENT") or os.environ.get("SSH_TTY"):
        _template = (
            os.environ.get("SEP_SSH_CLIP_GET")
            or os.environ.get("CL9_SSH_CLIP_GET")
            or ""
        ).strip()
        if _template:
            _connection = (os.environ.get("SSH_CONNECTION") or "").strip().split()
            _client = (os.environ.get("SSH_CLIENT") or "").strip().split()
            _ctx = {
                "client_ip": _connection[0] if len(_connection) >= 1 else (_client[0] if len(_client) >= 1 else ""),
                "client_port": _connection[1] if len(_connection) >= 2 else (_client[1] if len(_client) >= 2 else ""),
                "server_ip": _connection[2] if len(_connection) >= 3 else "",
                "server_port": _connection[3] if len(_connection) >= 4 else "",
                "ssh_tty": os.environ.get("SSH_TTY", ""),
            }
            try:
                _command = _template.format(**_ctx)
                _proc = subprocess.run(
                    _command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
                if _proc.returncode == 0:
                    if verbose:
                        print("using SSH controller clipboard command")
                    if warn_tty:
                        print("Pasted from SSH controller clipboard command")
                    return _proc.stdout.decode(errors="replace")
            except Exception:
                pass


    # 8. Total failure
    if verbose:
        print("Total Failure")
    return None



# ---------------------------------
def _prompt_line(msg: str) -> str:
    try:
        from prompt_toolkit import prompt
        value = prompt(msg)
    except (EOFError, KeyboardInterrupt):
        return "ooo"
    except Exception:
        try:
            value = input(msg)
        except (EOFError, KeyboardInterrupt):
            return "ooo"

    if value.strip().lower() == "q":
        return "exit"
    return value
    

# --------------------------------------
def _prompt_password(msg: str) -> str:
    # prompt_toolkit optional, but getpass is good enough and safe
    try:
        return getpass.getpass(msg)
    except (EOFError, KeyboardInterrupt):
        return "ooo"




# ===========================
# MARK: AWS API
# ===========================


class Creds:
    """Lazy credential wrapper around the encrypted creds store."""

    def __init__(
        self,
        initial: Mapping[str, str] | None = None,
        *,
        loader: Callable[[], dict[str, str]] | None = None,
    ) -> None:
        self._data: dict[str, str] | None
        if initial is None and loader is not None:
            self._data = None
        else:
            self._data = _normalize_creds_dict(dict(initial or {}))
        self._loader = loader

    def _ensure_loaded(self) -> dict[str, str]:
        if self._data is None:
            loaded = self._loader() if self._loader is not None else {}
            self._data = _normalize_creds_dict(loaded)
        return self._data

    def get(self, key: str, default: str | None = None) -> str | None:
        value = self._ensure_loaded().get(key)
        if value is None or not value.strip():
            return default
        return value.strip()

    def set(self, key: str, value: str | None) -> None:
        data = self._ensure_loaded()
        if value is None:
            data.pop(key, None)
            return
        cleaned = str(value).strip()
        if cleaned:
            data[key] = cleaned
        else:
            data.pop(key, None)

    def update(self, other: Mapping[str, str]) -> None:
        for key, value in other.items():
            self.set(str(key), str(value))

    def to_dict(self) -> dict[str, str]:
        return dict(self._ensure_loaded())

    def items(self):
        return self._ensure_loaded().items()

    def keys(self):
        return self._ensure_loaded().keys()

    def values(self):
        return self._ensure_loaded().values()

    def __iter__(self):
        return iter(self._ensure_loaded())

    def __len__(self) -> int:
        return len(self._ensure_loaded())

    def __contains__(self, key: object) -> bool:
        return key in self._ensure_loaded()

    @property
    def aws_access_key_id(self) -> str | None:
        return self.get("PRIVATE_AWS_ACCESS_KEY_ID")

    @aws_access_key_id.setter
    def aws_access_key_id(self, value: str | None) -> None:
        self.set("PRIVATE_AWS_ACCESS_KEY_ID", value)

    @property
    def access_key_id(self) -> str | None:
        return self.aws_access_key_id

    @access_key_id.setter
    def access_key_id(self, value: str | None) -> None:
        self.aws_access_key_id = value

    @property
    def aws_secret_access_key(self) -> str | None:
        return self.get("PRIVATE_AWS_SECRET_ACCESS_KEY")

    @aws_secret_access_key.setter
    def aws_secret_access_key(self, value: str | None) -> None:
        self.set("PRIVATE_AWS_SECRET_ACCESS_KEY", value)

    @property
    def secret_access_key(self) -> str | None:
        return self.aws_secret_access_key

    @secret_access_key.setter
    def secret_access_key(self, value: str | None) -> None:
        self.aws_secret_access_key = value

    @property
    def bucket_name(self) -> str | None:
        return self.get("PRIVATE_BUCKET_NAME")

    @bucket_name.setter
    def bucket_name(self, value: str | None) -> None:
        self.set("PRIVATE_BUCKET_NAME", value)

    @property
    def region_name(self) -> str | None:
        return self.get("PRIVATE_BUCKET_REGION")

    @region_name.setter
    def region_name(self, value: str | None) -> None:
        self.set("PRIVATE_BUCKET_REGION", value)

    @property
    def groq_key(self) -> str | None:
        return self.get("GROQ_KEY")

    @groq_key.setter
    def groq_key(self, value: str | None) -> None:
        self.set("GROQ_KEY", value)

    @property
    def github_pat(self) -> str | None:
        return self.get("GITHUB_PAT")

    @github_pat.setter
    def github_pat(self, value: str | None) -> None:
        self.set("GITHUB_PAT", value)

    @property
    def sudo_password(self) -> str | None:
        return self.get("SUDO_PASSWORD")

    @sudo_password.setter
    def sudo_password(self, value: str | None) -> None:
        self.set("SUDO_PASSWORD", value)


_CREDS_SINGLETON: Creds | None = None


def _load_current_creds_dict() -> dict[str, str]:
    if not LOCAL_CREDS_PATH.is_file():
        # if not coder_main():
        #     sys.exit(2)
        crint("Use python3", end='')
        crint(" python3 ~/cl9/m/cl9.py creds set", 'yellow')
        sys.exit(2)

    data = decoder_main()
    if data is None:
        sys.exit(2)
    return data


# ------------------------------------------
def get_creds() -> Creds:
    global _CREDS_SINGLETON
    if _CREDS_SINGLETON is None:
        _CREDS_SINGLETON = Creds(loader=_load_current_creds_dict)
    return _CREDS_SINGLETON
    

# --------------------------------------
def get_s3_bucket(creds: Creds):
    try:
        import boto3
    except ModuleNotFoundError:
        crint(f"boto3 is not installed. Run {LOCAL_MAIN_DIR}/dispatch.py --deps to install the managed Python environment.")
        crint('Please restart', 'yellow')
        sys.exit(0)
    aws_access_key_id = creds.aws_access_key_id
    aws_secret_access_key = creds.aws_secret_access_key
    region_name = creds.region_name
    bucket_name = creds.bucket_name
    S3 = boto3.client(
        "s3",
        aws_access_key_id     = aws_access_key_id,
        aws_secret_access_key = aws_secret_access_key,
        region_name           = region_name
    )
    return S3, bucket_name

# ----------------------------
def get_lambda(creds: Creds):
    import boto3
    aws_access_key_id = creds.aws_access_key_id
    aws_secret_access_key = creds.aws_secret_access_key
    region_name = creds.region_name
    
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    return lambda_client




# ===========================
# MARK: S3 FILE UTILS
# ===========================


# ----------------------------------------------------------------
def _purge_dir(path: Path) -> None:
    """
    Remove all contents of `path` (files and directories). Path itself is preserved.
    """
    path.mkdir(parents=True, exist_ok=True)

    for entry in path.iterdir():
        try:
            if entry.is_dir():
                shutil.rmtree(entry)
            else:
                entry.unlink()
        except Exception as e:
            print(f"[WARN] Failed to delete {entry}: {e!r}")


def _purge_selected_entries(path: Path, names: Iterable[str]) -> None:
    path.mkdir(parents=True, exist_ok=True)

    for name in names:
        target = path / name
        if not target.exists() and not target.is_symlink():
            continue
        try:
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        except Exception as e:
            print(f"[WARN] Failed to delete {target}: {e!r}")


# ----------------------------------------------------------------
def _download_bytes_from_s3(bucket: str, key: S3Key, S3) -> bytes:
    obj = S3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read()

# ----------------------------------------------------------------
def _extract_tgz_bytes_to_dir(tgz_bytes: bytes, dest_dir: Path) -> None:
    with io.BytesIO(tgz_bytes) as bio:
        with tarfile.open(fileobj=bio, mode="r:gz") as tf:
            for member in tf.getmembers():
                member_path = os.path.normpath(member.name)
                if os.path.isabs(member_path) or member_path.startswith(".."):
                    raise RuntimeError(f"Unsafe path in tar: {member.name}")
                if member.issym() or member.islnk():
                    continue
                member.name = member_path.lstrip(os.sep)
                tf.extract(member, dest_dir, set_attrs=True)


def _sync_manifest_roots(unpack_dir: Path) -> list[str]:
    manifest_path = unpack_dir / ".cl9_sync_manifest.json"
    if manifest_path.is_file():
        try:
            payload = json.loads(manifest_path.read_text())
            roots = payload.get("roots", [])
            if isinstance(roots, list):
                cleaned = [str(name).strip() for name in roots if str(name).strip()]
                if cleaned:
                    return sorted(set(cleaned))
        except Exception as e:
            print(f"[WARN] Failed to read sync manifest: {e!r}")

    return sorted(
        {
            path.name
            for path in unpack_dir.iterdir()
            if path.name != ".cl9_sync_manifest.json"
        }
    )

# ----------------------------------------------------------------
def get_file_s3(aws_key: S3Key, dest_name: Path, bucket_name: str, S3) -> bool:
    """
    Simple version: directly downloads a file from AWS S3 and writes to disk.
    No atomic writes, no rollback, no temporary paths.
    """
    try:
        _dir_name = dest_name.parent
        _dir_name.mkdir(parents=True, exist_ok=True)
        
        S3.download_file(bucket_name, aws_key, str(dest_name))
        return True
    except Exception as e:
        print(f"Error downloading {aws_key} from {bucket_name}: {e}")
        return False


#---------------------
def list_s3_objects(
    prefix: str,
    bucket_name: str,
    S3,
) -> list[str]:
    """
    List the objects keys (absolute) in an S3 bucket under the given prefix.

    Args:
        bucket_name (str): Name of the S3 bucket.
        prefix (str): Key prefix to filter objects.

    Returns:
        list[str]: objects keys (absolute) under the prefix.
    """
    keys = []
    continuation_token = None

    while True:
        if continuation_token:
            response = S3.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                ContinuationToken=continuation_token
            )
        else:
            response = S3.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )

        if "Contents" not in response:
            break

        for obj in response["Contents"]:
            keys.append(obj["Key"])

        if response.get("IsTruncated"):
            continuation_token = response["NextContinuationToken"]
        else:
            break

    return keys






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
# MARK: KEYCACHE
# ===========================



# -----------------------------------------------------------
def _load_keyutils():
    """Try to load libkeyutils (preferred on real Linux)."""
    global _libkeyutils, _libc
    if _libkeyutils is not None or _libc is not None:
        return
    path = ctypes.util.find_library("keyutils")
    if path:
        try:
            _libkeyutils = ctypes.CDLL(path, use_errno=True)
            return
        except Exception:
            _libkeyutils = None
    # Fallback to libc.syscall if keyutils isn't available
    libc_path = ctypes.util.find_library("c")
    if libc_path:
        try:
            _libc = ctypes.CDLL(libc_path, use_errno=True)
        except Exception:
            _libc = None


# -------------------------
def _syscall_numbers():
    """
    Per-arch syscall numbers for add_key/keyctl, used only if libkeyutils is absent.
    These are stable for main arches.
    """
    m = platform.machine().lower()
    if m in ("x86_64", "amd64"):
        return 248, 250
    if m in ("aarch64", "arm64"):
        return 217, 219
    if m.startswith("armv7") or m.startswith("arm"):
        return 309, 311
    return None, None


# -----------------------------------
def _running_on_termux() -> bool:
    """Detect Termux/Android userland reliably."""
    # 1. Typical Termux environment variables
    if "TERMUX_VERSION" in os.environ:
        return True
    # 2. Android OS name / properties
    if platform.system().lower() == "linux":
        try:
            with open("/system/build.prop", "rb"):
                return True
        except Exception:
            pass
    # 3. $PREFIX usually exists on Termux
    prefix = os.environ.get("PREFIX", "")
    if prefix.startswith("/data/data/com.termux"):
        return True
    return False


# ---------------------------------
def _keyring_available() -> bool:
    global _keyring_available_cached
    if _keyring_available_cached is not None:
        return _keyring_available_cached

    # Termux / Android => hard disable
    if _running_on_termux():
        _keyring_available_cached = False
        return False

    # Non-posix => disable
    if os.name != "posix":
        _keyring_available_cached = False
        return False

    # Normal Linux detection
    _load_keyutils()

    try:
        if _libkeyutils:
            # We do NOT make a syscall here.
            # We only check if functions exist in the library.
            if hasattr(_libkeyutils, "keyctl_search"):
                _keyring_available_cached = True
                return True

        # Fallback: no keyutils, but libc present
        if _libc:
            add_key_nr, keyctl_nr = _syscall_numbers()
            if add_key_nr is not None and keyctl_nr is not None:
                # We *assume* keyrings exist because we are on Linux.
                # If they don't, syscalls will fail cleanly, not SIGSYS.
                _keyring_available_cached = True
                return True

    except Exception:
        _keyring_available_cached = False
        return False

    _keyring_available_cached = False
    return False


# ---------------------------------------
def _keyring_search() -> Optional[int]:
    """Return key id if present in user keyring, else None."""
    if not _keyring_available():
        return None

    _load_keyutils()
    try:
        if _libkeyutils:
            _libkeyutils.keyctl_search.restype = ctypes.c_long
            _libkeyutils.keyctl_search.argtypes = [
                ctypes.c_long, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_long
            ]
            kid = _libkeyutils.keyctl_search(
                KEY_SPEC_USER_KEYRING,
                ctypes.c_char_p(_KEYRING_TYPE),
                ctypes.c_char_p(_KEYRING_DESC),
                0
            )
            if kid < 0:
                return None
            return int(kid)

        if _libc:
            add_key_nr, keyctl_nr = _syscall_numbers()
            if keyctl_nr is None:
                return None
            _libc.syscall.restype = ctypes.c_long
            kid = _libc.syscall(
                keyctl_nr,
                KEYCTL_SEARCH,
                KEY_SPEC_USER_KEYRING,
                ctypes.c_char_p(_KEYRING_TYPE),
                ctypes.c_char_p(_KEYRING_DESC),
                0
            )
            if kid < 0:
                return None
            return int(kid)

    except Exception:
        return None
    return None


# -------------------------------------------------------
def _keyring_set_timeout(kid: int, ttl_sec: int) -> bool:
    """Kernel-enforced TTL refresh."""
    _load_keyutils()
    try:
        if _libkeyutils:
            _libkeyutils.keyctl_set_timeout.restype = ctypes.c_long
            _libkeyutils.keyctl_set_timeout.argtypes = [ctypes.c_long, ctypes.c_uint]
            res = _libkeyutils.keyctl_set_timeout(kid, ttl_sec)
            return res == 0

        if _libc:
            add_key_nr, keyctl_nr = _syscall_numbers()
            if keyctl_nr is None:
                return False
            _libc.syscall.restype = ctypes.c_long
            res = _libc.syscall(
                keyctl_nr,
                KEYCTL_SET_TIMEOUT,
                kid,
                ttl_sec
            )
            return res == 0
    except Exception:
        return False

    return False


# -------------------------------------------------------------
def _keyring_add_and_timeout(key: bytes, ttl_sec: int) -> bool:
    """Store key bytes into user keyring and set TTL."""
    if not _keyring_available():
        return False

    _load_keyutils()
    try:
        if _libkeyutils:
            _libkeyutils.add_key.restype = ctypes.c_long
            _libkeyutils.add_key.argtypes = [
                ctypes.c_char_p, ctypes.c_char_p,
                ctypes.c_void_p, ctypes.c_size_t,
                ctypes.c_long
            ]
            kid = _libkeyutils.add_key(
                ctypes.c_char_p(_KEYRING_TYPE),
                ctypes.c_char_p(_KEYRING_DESC),
                ctypes.c_char_p(key),
                len(key),
                KEY_SPEC_USER_KEYRING
            )
            if kid < 0:
                return False
            return _keyring_set_timeout(int(kid), ttl_sec)

        if _libc:
            add_key_nr, keyctl_nr = _syscall_numbers()
            if add_key_nr is None or keyctl_nr is None:
                return False

            _libc.syscall.restype = ctypes.c_long
            kid = _libc.syscall(
                add_key_nr,
                ctypes.c_char_p(_KEYRING_TYPE),
                ctypes.c_char_p(_KEYRING_DESC),
                ctypes.c_char_p(key),
                ctypes.c_size_t(len(key)),
                KEY_SPEC_USER_KEYRING
            )
            if kid < 0:
                return False
            return _keyring_set_timeout(int(kid), ttl_sec)

    except Exception:
        return False

    return False


# ----------------------------------------------
def _keyring_read(kid: int) -> Optional[bytes]:
    """Read key payload from keyring."""
    _load_keyutils()
    try:
        if _libkeyutils:
            _libkeyutils.keyctl_read.restype = ctypes.c_long
            _libkeyutils.keyctl_read.argtypes = [
                ctypes.c_long, ctypes.c_void_p, ctypes.c_size_t
            ]
            # First call with NULL to get size
            sz = _libkeyutils.keyctl_read(kid, None, 0)
            if sz <= 0:
                return None
            buf = ctypes.create_string_buffer(sz)
            got = _libkeyutils.keyctl_read(kid, buf, sz)
            if got != sz:
                return None
            return bytes(buf.raw)

        if _libc:
            add_key_nr, keyctl_nr = _syscall_numbers()
            if keyctl_nr is None:
                return None
            _libc.syscall.restype = ctypes.c_long
            sz = _libc.syscall(keyctl_nr, KEYCTL_READ, kid, 0, 0)
            if sz <= 0:
                return None
            buf = ctypes.create_string_buffer(sz)
            got = _libc.syscall(keyctl_nr, KEYCTL_READ, kid, ctypes.byref(buf), sz)
            if got != sz:
                return None
            return bytes(buf.raw)

    except Exception:
        return None

    return None


# ---------------------------------------------
def _store_key_cache_file(key: bytes) -> None:
    blob = json.dumps({
        "wall": time.time(),
        "mono": time.monotonic(),
        "k": base64.b64encode(key).decode()
    }).encode()

    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW
    fd = os.open(KEY_CACHE, flags, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(blob)


# ---------------------------------------------
def _load_key_cache_file() -> Optional[bytes]:
    try:
        flags = os.O_RDONLY | os.O_NOFOLLOW
        fd = os.open(KEY_CACHE, flags)
        with os.fdopen(fd, "rb") as f:
            d = json.loads(f.read().decode())
    except Exception:
        return None

    if "wall" not in d or "mono" not in d or "k" not in d:
        try:
            os.remove(KEY_CACHE)
        except Exception:
            pass
        return None

    wall_now = time.time()
    mono_now = time.monotonic()

    if (wall_now - d["wall"] > KEY_TTL_SEC) or \
       (mono_now - d["mono"] > KEY_TTL_SEC + 1):
        return None

    try:
        return base64.b64decode(d["k"])
    except Exception:
        return None


# ---------------------------------------
def _store_key_cache(key: bytes) -> None:
    """
    Store cache:
      - Fedora/real Linux: kernel keyring + kernel TTL.
      - Termux/others: file cache fallback (logical TTL).
    """
    if _keyring_add_and_timeout(key, KEY_TTL_SEC):
        return
    _store_key_cache_file(key)


# ---------------------------------------
def _load_key_cache() -> Optional[bytes]:
    """
    Load cache:
      - Try keyring first on real Linux.
      - If not found or keyring unavailable, fallback to file.
    Also refreshes TTL opportunistically when keyring hit.
    """
    if _keyring_available():
        kid = _keyring_search()
        if kid is not None:
            k = _keyring_read(kid)
            if k:
                _keyring_set_timeout(kid, KEY_TTL_SEC)  # refresh kernel TTL
                return k

    return _load_key_cache_file()


# --------------------------------
def refresh_cached_key() -> bool:
    """
    Refresh cached key without prompting password.
    Returns:
      True  -> cache existed and was refreshed
      False -> no valid cache to refresh
    """
    if _keyring_available():
        kid = _keyring_search()
        if kid is None:
            return False
        return _keyring_set_timeout(kid, KEY_TTL_SEC)

    # File fallback: only refresh if still valid
    k = _load_key_cache_file()
    if k is None:
        return False
    _store_key_cache_file(k)  # bumps wall/mono timestamps
    return True


# -------------------------
def _keyring_invalidate():
    kidd = _keyring_search()
    if kidd is None:
        return False

    _load_keyutils()
    # keyctl_unlink is command 9
    KEYCTL_UNLINK = 9

    try:
        if _libkeyutils:
            _libkeyutils.keyctl_unlink.restype = ctypes.c_long
            _libkeyutils.keyctl_unlink.argtypes = [ctypes.c_long, ctypes.c_long]
            res = _libkeyutils.keyctl_unlink(kidd, KEY_SPEC_USER_KEYRING)
            return res == 0

        if _libc:
            add_key_nr, keyctl_nr = _syscall_numbers()
            if keyctl_nr is None:
                return False
            res = _libc.syscall(
                keyctl_nr,
                KEYCTL_UNLINK,
                kidd,
                KEY_SPEC_USER_KEYRING
            )
            return res == 0

    except Exception:
        return False

    return False


# -------------------------------------------------------------
def _decrypt_with_cached_key(blob: bytes, key: bytes) -> dict:
    salt_off = 4
    nonce_off = salt_off + SALT_LEN
    ct_off = nonce_off + NONCE_LEN
    nonce = blob[nonce_off:ct_off]
    ciphertext_and_tag = blob[ct_off:]
    pt = _aes_gcm_decrypt(key, nonce, ciphertext_and_tag, MAGIC)
    return json.loads(pt.decode())





# ===========================
# MARK: AES-256
# ===========================

# -----------------------------------------
def _rot_word(w: int) -> int:
    return ((w << 8) & 0xffffffff) | (w >> 24)


# ----------------------------------
def _sub_word(w: int) -> int:
    return ((SBOX[(w >> 24) & 0xff] << 24) |
            (SBOX[(w >> 16) & 0xff] << 16) |
            (SBOX[(w >> 8) & 0xff] << 8) |
            (SBOX[w & 0xff]))


# ----------------------------------
def _key_expansion_256(key: bytes):
    Nk, Nb, Nr = 8, 4, 14
    w = [0] * (Nb * (Nr + 1))  # 60 words

    for i in range(Nk):
        w[i] = int.from_bytes(key[4*i:4*i+4], "big")

    rcon = [0] * (Nr + 1)
    rc = 1
    for i in range(1, Nr + 1):
        rcon[i] = rc << 24
        rc = (rc << 1) ^ (0x11b if rc & 0x80 else 0)
        rc &= 0xff

    for i in range(Nk, Nb*(Nr+1)):
        temp = w[i-1]
        if i % Nk == 0:
            temp = _sub_word(_rot_word(temp)) ^ rcon[i//Nk]
        elif i % Nk == 4:
            temp = _sub_word(temp)
        w[i] = w[i-Nk] ^ temp

    round_keys = []
    for r in range(Nr + 1):
        rk = b"".join(w[4*r + j].to_bytes(4, "big") for j in range(4))
        round_keys.append(rk)
    return round_keys


# ----------------------------------
def _xtime(a: int) -> int:
    return ((a << 1) & 0xff) ^ (0x1b if a & 0x80 else 0)


# ----------------------------------
def _mix_single_column(col):
    a0,a1,a2,a3 = col
    t = a0 ^ a1 ^ a2 ^ a3
    u = a0
    col[0] ^= t ^ _xtime(a0 ^ a1)
    col[1] ^= t ^ _xtime(a1 ^ a2)
    col[2] ^= t ^ _xtime(a2 ^ a3)
    col[3] ^= t ^ _xtime(a3 ^ u)


# -----------------------------------
def _add_round_key(state, rk: bytes):
    for i in range(16):
        state[i] ^= rk[i]


# ---------------------
def _sub_bytes(state):
    for i in range(16):
        state[i] = SBOX[state[i]]


# ----------------------
def _shift_rows(state):
    # state is column-major (AES standard)
    state[1],state[5],state[9],state[13]   = state[5],state[9],state[13],state[1]
    state[2],state[6],state[10],state[14]  = state[10],state[14],state[2],state[6]
    state[3],state[7],state[11],state[15]  = state[15],state[3],state[7],state[11]


# -----------------------
def _mix_columns(state):
    for c in range(4):
        col = [state[4*c + r] for r in range(4)]
        _mix_single_column(col)
        for r in range(4):
            state[4*c + r] = col[r]


# -----------------------------------------------------------
def _aes256_encrypt_block(key: bytes, block: bytes) -> bytes:
    rks = _key_expansion_256(key)
    state = list(block)
    _add_round_key(state, rks[0])

    for rnd in range(1, 14):
        _sub_bytes(state)
        _shift_rows(state)
        _mix_columns(state)
        _add_round_key(state, rks[rnd])

    _sub_bytes(state)
    _shift_rows(state)
    _add_round_key(state, rks[14])
    return bytes(state)





# ===========================
# MARK: GCM LAYER
# ===========================

# ----------------------------------
def _gf_mul(x: int, y: int) -> int:
    z = 0
    v = y
    for i in range(128):
        if (x >> (127 - i)) & 1:
            z ^= v
        if v & 1:
            v = (v >> 1) ^ _R_GHASH
        else:
            v >>= 1
    return z


# ------------------------------------------------
def _ghash(H: bytes, A: bytes, C: bytes) -> bytes:
    h_int = int.from_bytes(H, "big")
    y = 0

    def blocks(data: bytes):
        for i in range(0, len(data), 16):
            b = data[i:i+16]
            if len(b) < 16:
                b += b"\x00" * (16 - len(b))
            yield int.from_bytes(b, "big")

    for b in blocks(A):
        y = _gf_mul(y ^ b, h_int)
    for b in blocks(C):
        y = _gf_mul(y ^ b, h_int)

    a_bits = len(A) * 8
    c_bits = len(C) * 8
    len_block = a_bits.to_bytes(8, "big") + c_bits.to_bytes(8, "big")
    y = _gf_mul(y ^ int.from_bytes(len_block, "big"), h_int)
    return y.to_bytes(16, "big")


# ----------------------------------------
def _inc32(counter_block: bytes) -> bytes:
    prefix = counter_block[:12]
    ctr = int.from_bytes(counter_block[12:], "big")
    ctr = (ctr + 1) & 0xffffffff
    return prefix + ctr.to_bytes(4, "big")


# ------------------------------------------------------------------------------------
def _aes_gcm_encrypt(key: bytes, nonce: bytes, plaintext: bytes, aad: bytes) -> bytes:
    if len(nonce) != 12:
        raise ValueError("GCM nonce must be 12 bytes")

    H  = _aes256_encrypt_block(key, b"\x00" * 16)
    J0 = nonce + b"\x00\x00\x00\x01"

    ctr = _inc32(J0)
    ct = bytearray()
    for i in range(0, len(plaintext), 16):
        ks = _aes256_encrypt_block(key, ctr)
        block = plaintext[i:i+16]
        ct_block = bytes(b ^ k for b, k in zip(block, ks[:len(block)]))
        ct += ct_block
        ctr = _inc32(ctr)

    S = _ghash(H, aad, bytes(ct))
    tag = bytes(a ^ b for a, b in zip(_aes256_encrypt_block(key, J0), S))
    return bytes(ct) + tag


# -------------------------------------------------------------------------------
def _aes_gcm_decrypt(key: bytes, nonce: bytes, data: bytes, aad: bytes) -> bytes:
    if len(nonce) != 12:
        raise ValueError("GCM nonce must be 12 bytes")
    if len(data) < 16:
        raise ValueError("Ciphertext too short")

    ct, tag = data[:-16], data[-16:]

    H  = _aes256_encrypt_block(key, b"\x00" * 16)
    J0 = nonce + b"\x00\x00\x00\x01"

    S = _ghash(H, aad, ct)
    expected = bytes(a ^ b for a, b in zip(_aes256_encrypt_block(key, J0), S))
    if not hmac.compare_digest(expected, tag):
        raise ValueError("Authentication failed (bad tag)")

    ctr = _inc32(J0)
    pt = bytearray()
    for i in range(0, len(ct), 16):
        ks = _aes256_encrypt_block(key, ctr)
        block = ct[i:i+16]
        pt_block = bytes(b ^ k for b, k in zip(block, ks[:len(block)]))
        pt += pt_block
        ctr = _inc32(ctr)

    return bytes(pt)





# ===========================
# MARK: CRYPTO API
# ===========================

# ---------------------------------------------------
def derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERS,
        dklen=32,  # AES-256
    )

# -------------------------------------------------
def encrypt_dict(d: Dict, password: str) -> bytes:
    salt = os.urandom(SALT_LEN)
    key = derive_key(password, salt)
    return _encrypt_dict_with_key(d, key, salt)


def _encrypt_dict_with_key(d: Dict, key: bytes, salt: bytes) -> bytes:
    nonce = os.urandom(NONCE_LEN)

    plaintext = json.dumps(d, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ciphertext_and_tag = _aes_gcm_encrypt(key, nonce, plaintext, MAGIC)

    # MAGIC | salt | nonce | (ciphertext||tag)
    return MAGIC + salt + nonce + ciphertext_and_tag

# ---------------------------------------------------
def decrypt_blob(blob: bytes, password: str) -> dict:
    if len(blob) < len(MAGIC) + SALT_LEN + NONCE_LEN + 16 + 1:
        raise ValueError("File too short / corrupted")

    if blob[:4] != MAGIC:
        raise ValueError("Bad magic/version. Not a coder.py file or corrupted.")

    salt_off = 4
    nonce_off = salt_off + SALT_LEN
    ct_off = nonce_off + NONCE_LEN

    salt = blob[salt_off:nonce_off]
    nonce = blob[nonce_off:ct_off]
    ciphertext_and_tag = blob[ct_off:]

    key = derive_key(password, salt)
    plaintext = _aes_gcm_decrypt(key, nonce, ciphertext_and_tag, MAGIC)

    d = json.loads(plaintext.decode("utf-8"))
    if not isinstance(d, dict):
        raise ValueError("Decrypted payload is not a dict.")
    return d


def _normalize_creds_dict(data: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in data.items():
        if value is None:
            continue
        out[str(key)] = str(value).strip()
    return out


def _extract_creds_salt(blob: bytes) -> bytes:
    if len(blob) < len(MAGIC) + SALT_LEN + NONCE_LEN + 16 + 1:
        raise ValueError("File too short / corrupted")
    if blob[:4] != MAGIC:
        raise ValueError("Bad magic/version. Not a cl9 creds file or corrupted.")
    return blob[4:4+SALT_LEN]


def _missing_required_cred_keys(creds: dict[str, str]) -> list[str]:
    return [key for key in AWS_REQ_KEYS if not creds.get(key, "").strip()]


def _preview_cred_value(key: str, value: str) -> str:
    if not value:
        return "[missing]"
    if key in CREDS_SHOW_FULL_KEYS:
        return value
    if len(value) <= 4:
        return "*" * len(value)
    if len(value) <= 15:
        return f"{value[:2]}...{value[-2:]}"
    return f"{value[:4]}...{value[-4:]} (len={len(value)})"


def _colorize_cred_status(value: str) -> str:
    return clz("saved", "green") if value else clz("missing", "red")


def _colorize_cred_preview(key: str, value: str) -> str:
    preview = _preview_cred_value(key, value)
    if not value:
        return clz(preview, "red")
    if key in CREDS_SHOW_FULL_KEYS:
        return clz(preview, "cyan")
    return clz(preview, "yellow")


def _print_cred_entry(idx: int, key: str, value: str, description: str) -> None:
    index_label = clz(f"[{idx:>2}]", "yellow")
    key_label = clz(f"{key:<30}", "magenta" if not value else "cyan")
    status_label = _colorize_cred_status(value)
    preview_label = _colorize_cred_preview(key, value)
    print(f"  {index_label} {key_label} {status_label} {preview_label}")
    print(f"      {clz(description, 'orange')}")


def _resolve_cred_key(field: str, existing_keys: list[str] | None = None) -> str:
    normalized = _normalize_cred_lookup_key(field)
    if normalized in CREDS_KEY_ALIASES:
        return CREDS_KEY_ALIASES[normalized]
    if existing_keys:
        for key in existing_keys:
            if _normalize_cred_lookup_key(key) == normalized:
                return key
    raise KeyError(field)


def _resolve_cred_fields(fields: list[str], existing: dict[str, str] | None = None) -> list[str]:
    resolved: list[str] = []
    existing_keys = list(existing or {})
    for field in fields:
        key = _resolve_cred_key(field, existing_keys)
        if key not in resolved:
            resolved.append(key)
    return resolved


def _print_creds_preview(creds: dict[str, str], keys: list[str] | None = None) -> None:
    req_keys = keys or list(AWS_REQ_KEYS)
    saved_count = sum(1 for key in req_keys if creds.get(key, "").strip())
    missing_count = len(req_keys) - saved_count
    print()
    crint("Saved creds preview", "cyan")
    print(f"  {clz(str(saved_count), 'green')} saved   {clz(str(missing_count), 'red')} missing")
    for idx, key in enumerate(req_keys, 1):
        print()
        value = creds.get(key, "").strip()
        _print_cred_entry(idx, key, value, AWS_REQ_KEYS.get(key, "Saved value"))

    extra_keys = sorted(key for key in creds if key not in AWS_REQ_KEYS and (keys is None or key in keys))
    if extra_keys:
        print()
        crint("Extra saved fields", "cyan")
        for idx, key in enumerate(extra_keys, start=len(req_keys) + 1):
            value = creds.get(key, "").strip()
            _print_cred_entry(idx, key, value, "Saved value")

    missing = _missing_required_cred_keys(creds)
    print()
    if missing:
        crint(f"Missing required fields: {', '.join(missing)}", "red")
    else:
        crint("All required fields are saved.", "green")


def _write_creds_blob(blob: bytes, out_path: Path = LOCAL_CREDS_PATH) -> None:
    tmp_path = out_path.parent / f"{out_path.name}.tmp"
    with open(tmp_path, "wb") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    tmp_path.replace(out_path)


def _prompt_new_creds_password() -> str | None:
    min_len = 10
    while True:
        password = _prompt_password("Encryption password: ")
        if password.lower() in CREDS_EXIT_WORDS:
            return None
        if len(password) < min_len:
            output(f"Password is too short. It should be at least {min_len} digits. Try Again ...")
            continue

        confirm = _prompt_password("Confirm password: ")
        if confirm.lower() in CREDS_EXIT_WORDS:
            return None
        if password != confirm:
            print("Passwords do not match. Try Again...")
            continue
        return password


def _save_creds_data(
    creds: dict[str, str],
    key: bytes | None = None,
    salt: bytes | None = None,
) -> tuple[bytes, bytes] | None:
    clean_creds = _normalize_creds_dict(creds)
    if key is None or salt is None:
        password = _prompt_new_creds_password()
        if password is None:
            return None
        blob = encrypt_dict(clean_creds, password)
        salt = _extract_creds_salt(blob)
        key = derive_key(password, salt)
        _store_key_cache(key)
    else:
        blob = _encrypt_dict_with_key(clean_creds, key, salt)
        _store_key_cache(key)

    _write_creds_blob(blob)
    output(f"\nSaved {len(clean_creds)} entries to encrypted file: {LOCAL_CREDS_PATH}")
    return key, salt


def _format_creds_timeout(remaining_sec: int, timeout_at: datetime.datetime) -> str:
    minutes, seconds = divmod(max(0, remaining_sec), 60)
    return f"{minutes:02d}:{seconds:02d} remaining, timeout at {timeout_at:%H:%M}"


def _remaining_creds_session_seconds(deadline_mono: float) -> int:
    return max(0, int(deadline_mono - time.monotonic()))


def _creds_session_expired(deadline_mono: float) -> bool:
    return time.monotonic() >= deadline_mono

# MARK: Creds Editor
def _print_creds_editor_menu(
    creds: dict[str, str],
    keys: list[str],
    deadline_mono: float,
    timeout_at: datetime.datetime,
) -> None:
    saved_count = sum(1 for key in keys if creds.get(key, "").strip())
    missing_count = len(keys) - saved_count
    print()
    crint(f"Creds session: {_format_creds_timeout(_remaining_creds_session_seconds(deadline_mono), timeout_at)}", "yellow")
    print(f"  {clz(str(saved_count), 'green')} saved   {clz(str(missing_count), 'red')} missing")
    crint("Select an index to edit that field. Use q/quit/exit to stop.", "cyan")
    print()
    for idx, key in enumerate(keys, start=1):
        value = creds.get(key, "").strip()
        _print_cred_entry(idx, key, value, AWS_REQ_KEYS.get(key, "Saved value"))
    print()


def _prompt_for_cred_value_timed(
    key: str,
    current_value: str | None,
    deadline_mono: float,
    timeout_at: datetime.datetime,
) -> tuple[str, str | None]:
    description = AWS_REQ_KEYS.get(key, f"Saved value for {key}")
    while True:
        if _creds_session_expired(deadline_mono):
            crint("Creds session expired after 10 minutes. Start `python3 cl9.py creds config` again.", "red")
            return "expired", None

        print()
        crint(f"Editing {key}", "magenta")
        crint(f"Creds session: {_format_creds_timeout(_remaining_creds_session_seconds(deadline_mono), timeout_at)}", "yellow")
        if current_value:
            print(f"Current: {_preview_cred_value(key, current_value)}")
            line = _prompt_line(f"{description} [Enter keeps current]: ").strip()
            if _creds_session_expired(deadline_mono):
                crint("Creds session expired before this update could be applied.", "red")
                return "expired", None
            if not line:
                return "ok", current_value
        else:
            line = _prompt_line(f"{description}: ").strip()
            if _creds_session_expired(deadline_mono):
                crint("Creds session expired before this update could be applied.", "red")
                return "expired", None
            if not line:
                crint("This value is required. Type it, or exit with q/quit/exit.", "yellow")
                continue

        lowered = line.lower()
        if lowered in CREDS_EXIT_WORDS:
            return "quit", None
        if line == "p":
            _tmp = getclip()
            if _tmp is None:
                crint("Pasting is not possible. Type the value manually.", "red")
                continue
            line = _tmp.strip()
            preview = _preview_cred_value(key, line)
            if _prompt_line(f"Use clipboard value {preview}? (y/n): ").strip().lower() != "y":
                continue
        if not line:
            crint("Empty values are not allowed.", "yellow")
            continue
        return "ok", line


def _prompt_for_cred_value(key: str, current_value: str | None = None) -> str | None:
    description = AWS_REQ_KEYS.get(key, f"Saved value for {key}")
    while True:
        print()
        crint(key, "magenta")
        if current_value:
            print(f"Current: {_preview_cred_value(key, current_value)}")
            line = _prompt_line(f"{description} [Enter keeps current]: ").strip()
            if not line:
                return current_value
        else:
            line = _prompt_line(f"{description}: ").strip()
            if not line:
                crint("This value is required. Type it, or exit with aban/exit/end/ooo.", "yellow")
                continue

        if line.lower() in CREDS_EXIT_WORDS:
            return None
        if line == "p":
            _tmp = getclip()
            if _tmp is None:
                crint("Pasting is not possible. Type the value manually.", "red")
                continue
            line = _tmp.strip()
            preview = _preview_cred_value(key, line)
            if _prompt_line(f"Use clipboard value {preview}? (y/n): ").strip().lower() != "y":
                continue
        if not line:
            crint("Empty values are not allowed.", "yellow")
            continue
        return line


def _load_creds_store() -> Optional[tuple[dict[str, str], bytes, bytes]]:
    in_path = LOCAL_CREDS_PATH
    if not in_path.is_file():
        return None

    with open(in_path, "rb") as f:
        blob = f.read()

    try:
        salt = _extract_creds_salt(blob)
    except ValueError as e:
        crint(str(e), "red")
        sys.exit(2)

    cached_key = _load_key_cache()
    if cached_key:
        try:
            data = _normalize_creds_dict(_decrypt_with_cached_key(blob, cached_key))
            refresh_cached_key()
            return data, cached_key, salt
        except Exception:
            pass

    password = _prompt_password(f"{PROGRAM_NAME} Password: ")
    if not password:
        print("Empty password not allowed. Exiting.")
        sys.exit(2)
    if password == "reset":
        if _prompt_line("Are you sure you want to reset your password by deleting the existing credentials? (y/n) ") == "y":
            in_path.unlink()
            crint("Password Reset Successful. Please launch the Program again.", "green")
            sys.exit(0)
        crint("Not Reseting", "red")
        sys.exit(0)

    key = derive_key(password, salt)
    try:
        data = _normalize_creds_dict(_decrypt_with_cached_key(blob, key))
    except Exception:
        print("Incorrect Password")
        sys.exit(2)

    _store_key_cache(key)
    return data, key, salt


def _configure_creds_interactive(
    selected_keys: list[str] | None = None,
    existing: dict[str, str] | None = None,
    key: bytes | None = None,
    salt: bytes | None = None,
) -> bool:
    working = dict(existing or {})
    keys_to_edit = selected_keys or list(AWS_REQ_KEYS)

    output("Type 'p' to get the value directly from the clipboard (works on termux if termux-api is installed)")
    if existing:
        output("Press Enter to keep the current saved value.")
        _print_creds_preview(working)

    changed_keys: list[str] = []
    for cred_key in keys_to_edit:
        current_value = working.get(cred_key, "").strip() or None

        try:
            new_value = _prompt_for_cred_value(cred_key, current_value=current_value)
        except (KeyboardInterrupt, EOFError):
            break
        
        if new_value is None:
            return False
        if new_value != working.get(cred_key, "").strip():
            working[cred_key] = new_value
            changed_keys.append(cred_key)

    if not changed_keys and existing:
        output("No changes made.")
        return True

    if _save_creds_data(working, key=key, salt=salt) is None:
        return False

    print()
    crint("Updated fields: " + ", ".join(changed_keys or keys_to_edit), "green")
    _print_creds_preview(working)
    return True


def _configure_creds_menu(
    selected_keys: list[str],
    existing: dict[str, str] | None = None,
    key: bytes | None = None,
    salt: bytes | None = None,
) -> bool:
    working = dict(existing or {})
    deadline_mono = time.monotonic() + CREDS_SESSION_TIMEOUT_SEC
    timeout_at = datetime.datetime.now() + datetime.timedelta(seconds=CREDS_SESSION_TIMEOUT_SEC)

    output("Type 'p' to paste from the clipboard while editing a selected field.")
    while True:
        if _creds_session_expired(deadline_mono):
            crint("Creds session expired after 10 minutes. Start `python3 cl9.py creds config` again.", "red")
            return False

        _print_creds_editor_menu(working, selected_keys, deadline_mono, timeout_at)
        choice = _prompt_line("Select field index to edit, or q/quit/exit: ").strip()
        if _creds_session_expired(deadline_mono):
            crint("Creds session expired after 10 minutes. Start `python3 cl9.py creds config` again.", "red")
            return False

        lowered = choice.lower()
        if lowered in CREDS_EXIT_WORDS:
            output("Leaving creds editor.")
            return True
        if not choice.isdigit():
            crint("Enter a valid index number, or q/quit/exit.", "yellow")
            continue

        index = int(choice)
        if index < 1 or index > len(selected_keys):
            crint("That index is out of range.", "yellow")
            continue

        selected_key = selected_keys[index - 1]
        current_value = working.get(selected_key, "").strip() or None
        status, new_value = _prompt_for_cred_value_timed(
            selected_key,
            current_value=current_value,
            deadline_mono=deadline_mono,
            timeout_at=timeout_at,
        )
        if status == "quit":
            output("Leaving creds editor.")
            return True
        if status == "expired":
            return False
        if new_value == working.get(selected_key, "").strip():
            crint(f"No change for {selected_key}.", "yellow")
            continue

        working[selected_key] = new_value or ""
        saved = _save_creds_data(working, key=key, salt=salt)
        if saved is None:
            return False
        key, salt = saved
        crint(f"Updated {selected_key}.", "green")





# ===========================
# MARK: CREDS (EN)CODER
# ===========================

# ------------------------------------------------------------
def coder_main() -> bool:
    return _configure_creds_interactive(list(AWS_REQ_KEYS))


# ---------------------------------------------
def decoder_main() -> Optional[dict[str, str]]:
    store = _load_creds_store()
    if store is None:
        print("File not found.")
        if not coder_main():
            print("Exitting")
            sys.exit(2)
        store = _load_creds_store()
        if store is None:
            sys.exit(2)
    return store[0]


# -----------------------
def validate_cache(verbose: bool=True):
    """
    Equivalent to: sudo -v
    Refresh TTL if cache exists and is valid.
    """
    refresh = refresh_cached_key()
    if refresh is False:
        decoder_main()
    
    if verbose:
        print("Cache validated (TTL refreshed).")


# -----------------------
def invalidate_cache():
    """
    Force-delete cached key from both keyring and file.
    """
    removed = False

    # 1. Try keyring first
    if _keyring_available():
        if _keyring_invalidate():
            print("Kernel keyring cache invalidated.")
            removed = True

    # 2. Fallback: remove file
    try:
        KEY_CACHE.unlink()
        print("File cache invalidated.")
        removed = True
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error invalidating file cache: {e}")

    if not removed:
        print("No cache present.")


def _run_creds_command(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(
        prog="cl9 creds",
        description="Inspect and update encrypted creds without re-entering everything.",
    )
    subparsers = parser.add_subparsers(dest="creds_action")

    list_parser = subparsers.add_parser("list", help="Show all saved fields with previews")
    list_parser.add_argument("fields", nargs="*", help="Optional field names to preview")

    show_parser = subparsers.add_parser("show", help="Alias for list")
    show_parser.add_argument("fields", nargs="*", help="Optional field names to preview")

    config_parser = subparsers.add_parser("config", help="Open the creds editor for all fields or selected ones")
    config_parser.add_argument("fields", nargs="*", metavar="field", help="Optional field names to include in the editor")

    set_parser = subparsers.add_parser("set", help="Alias for config")
    set_parser.add_argument("fields", nargs="*", metavar="field", help="Optional field names to include in the editor")

    args = parser.parse_args(argv)
    action = args.creds_action or "list"
    fields = getattr(args, "fields", [])

    if action in {"list", "show"}:
        store = _load_creds_store()
        if store is None:
            crint("No creds file found yet. Run `python3 cl9.py creds config` to create it.", "yellow")
            return
        creds, _, _ = store
        try:
            keys = _resolve_cred_fields(fields, creds) if fields else None
        except KeyError as e:
            crint(f"Unknown creds field: {e.args[0]}", "red")
            sys.exit(2)
        _print_creds_preview(creds, keys)
        return

    if action in {"config", "set"}:
        store = _load_creds_store()
        if store is None:
            creds: dict[str, str] = {}
            key = None
            salt = None
        else:
            creds, key, salt = store

        try:
            selected_keys = _resolve_cred_fields(fields, creds) if fields else list(AWS_REQ_KEYS)
        except KeyError as e:
            crint(f"Unknown creds field: {e.args[0]}", "red")
            print("Available fields:")
            for field in AWS_REQ_KEYS:
                print(f"  {field}")
            sys.exit(2)

        if not _configure_creds_menu(selected_keys, existing=creds, key=key, salt=salt):
            sys.exit(2)
        return

    parser.print_help()





# ============================
# OFFLINE
# ============================




def _write_offline_timestamp(end_ts: float) -> None:
    """Atomically write the offline end timestamp to disk."""
    try:
        tmp_path = LOCAL_MAKE_OFFLINE_PATH.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(f"{end_ts:.6f}\n")
            f.flush()
            os.fsync(f.fileno())
            tmp_path.replace(LOCAL_MAKE_OFFLINE_PATH)
    except Exception as e:
        crint(f"Failed to write offline timestamp: {e}", "red")



def make_offline(minutes: str | float | int = OFFLINE_DEFAULT_DURATION_MINUTES) -> None:
    """Set the device to offline mode for the given number of minutes."""
    try:
        minutes_val = float(minutes)
    except (ValueError, TypeError):
        minutes_val = OFFLINE_DEFAULT_DURATION_MINUTES

    minutes_val = min(minutes_val, OFFLINE_MAX_DURATION_MINUTES)
    end_ts = time.time() + minutes_val * 60

    _write_offline_timestamp(end_ts)
    crint(f"cl9 made offline for {minutes_val:.0f} minutes", "yellow")



def make_online() -> None:
    """Immediately bring the device back online."""
    try:
        if LOCAL_MAKE_OFFLINE_PATH.exists():
            LOCAL_MAKE_OFFLINE_PATH.unlink()
        # crint("cl9 is online now. Type rev --sync to sync", "green")
    except Exception as e:
        crint(f"Error removing offline file: {e}", "red")
        if LOCAL_MAKE_OFFLINE_PATH.is_dir():
            shutil.rmtree(LOCAL_MAKE_OFFLINE_PATH)


def is_offline() -> tuple[bool, str]:
    """
    Check current offline status. Always fresh — no caching.

    Returns:
        (is_currently_offline: bool, status_message: str)
    """
    if not LOCAL_MAKE_OFFLINE_PATH.is_file():
        return False, "cl9 is Online"

    try:
        content = LOCAL_MAKE_OFFLINE_PATH.read_text().strip()
        end_ts = float(content)
    except Exception as e:
        crint(f"Error reading offline timestamp (file removed): {e}", "red")
        try:
            LOCAL_MAKE_OFFLINE_PATH.unlink(missing_ok=True)
        except Exception:
            pass
        return False, "cl9 is Online (corrupted offline file cleared)"

    now = time.time()

    if end_ts <= now:
        # Expired — clean up
        try:
            LOCAL_MAKE_OFFLINE_PATH.unlink(missing_ok=True)
        except Exception as e:
            crint(f"Error removing expired offline file: {e}", "red")
        return False, "cl9 is Online (offline period expired)"

    # Still offline
    remaining_minutes = max(0, (end_ts - now) / 60)
    # Clamp to max just in case file was tampered with
    if remaining_minutes > OFFLINE_MAX_DURATION_MINUTES:
        end_ts = now + OFFLINE_MAX_DURATION_MINUTES * 60
        _write_offline_timestamp(end_ts)
        remaining_minutes = OFFLINE_MAX_DURATION_MINUTES

    status_msg = f"cl9 is Offline for {remaining_minutes:.0f} more minutes"
    return True, status_msg


# ========================
# CLI Integration
# ========================


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "creds":
        _run_creds_command(sys.argv[2:])
        return

    parser = argparse.ArgumentParser(
        prog = "cl9",
        description = "The cl9 Learning System",
        epilog = "Creds commands: python3 cl9.py creds [list|show|config|set]"
    )

    actions = parser.add_mutually_exclusive_group(required=True)

    actions.add_argument(
        "-v",
        action = "store_true",
        help = "Validate/refresh the cache TTL"
    )

    actions.add_argument(
        "-i",
        action = "store_true",
        help = "Invalidate/delete cache TTL"
    )

    actions.add_argument(
        "--fetch",
        action = "store_true",
        help = "Fetch the latest version of cl9 from the private bucket"
    )

    args = parser.parse_args()

    if args.v:
        validate_cache()
    
    elif args.i:
        invalidate_cache()

    elif args.fetch:
        get_cl9()


if __name__ == "__main__":
    main()
