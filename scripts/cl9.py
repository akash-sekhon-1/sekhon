

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
from typing import Dict, NewType, Optional





# annotate
S3Key = NewType("S3Key", str)


sys.path.insert(0, str(Path(__file__).resolve().parent / "pybind11"))

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

# Root
LOCAL_CL9_DIR           = HOME / PROGRAM_NAME
LOCAL_ALIAS_PATH        = HOME / ".cl9"
LOCAL_DUSTBIN           = HOME / "AD" / "AD_4M"


# Core SubDir
LOCAL_MAIN_DIR    = LOCAL_CL9_DIR / "m"
LOCAL_JSON_DIR    = LOCAL_CL9_DIR / "j"
LOCAL_TMP_DIR     = LOCAL_CL9_DIR / "tmp"
LOCAL_BAK_DIR     = LOCAL_CL9_DIR / "bak"
LOCAL_DEV_DIR     = LOCAL_CL9_DIR / "dev"

# non-cl9 roots
LOCAL_MANY_DIR    = HOME / "many"
LOCAL_SPEECH_DIR  = HOME / ".cache" / "cl9" / "speech"


# Bases
LOCAL_BASES_DIR   = LOCAL_JSON_DIR / "b"
LOCAL_MAIN_BASES_DIR = LOCAL_BASES_DIR / "m"
LOCAL_DELTAS_DIR     = LOCAL_BASES_DIR / "d"
LOCAL_VERSION_DIR    = LOCAL_BASES_DIR / "v"
LOCAL_PENDING_DIR     = LOCAL_BASES_DIR / "p"
LOCAL_SYNC_TS_FILE = LOCAL_BASES_DIR / ".last_sync_ts.txt"

# cache
LOCAL_MAIN_CACHE_PATH = LOCAL_JSON_DIR / ".all_json_cache.json.gz"
LOCAL_ABBR_DATA = LOCAL_JSON_DIR / "abbr_data.json.gz"

# automated backups
LOCAL_BACKUPS_DIR = LOCAL_CL9_DIR / "backups"
LOCAL_ABBR_BACKUP_DIR = LOCAL_BACKUPS_DIR / "abbr"
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

LOCAL_TEXT_HISTORY = LOCAL_JSON_DIR / ".text_history.json.gz" # THIS path is also mentioned in ins_adder.py (not imported to keep that fast) # has two keys, 'last_sync': ts and 'history': {hash: date}

VIVAL_LOAD_PATH: Path = HOME / "wing" / "career" / "dbt" / f"vivaldi_load_{HOSTNAME}.txt"


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



DIRS_TO_CREATE: tuple[Path] = (
    LOCAL_BAK_DIR,
    LOCAL_BASES_DIR,
    LOCAL_CL9_DIR,
    LOCAL_DELTAS_DIR,
    LOCAL_DUSTBIN,
    LOCAL_FILES_BU_DIR,
    LOCAL_JSON_DIR,
    LOCAL_MAIN_BASES_DIR,
    LOCAL_MAIN_DIR,
    LOCAL_MANY_DIR,
    LOCAL_PENDING_DIR,
    LOCAL_SCRIPTS_BU_DIR,
    LOCAL_SPEECH_DIR,
    LOCAL_TMP_DIR,
    LOCAL_VERSION_DIR,
    LOCAL_BACKUPS_DIR,
    LOCAL_ABBR_BACKUP_DIR,
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
    "GITHUB_PAT": "GitHub Token for storing a public version of cl9.py and inf.py (and bash sripts)"
}


AWS_SCRIPTS_PRE: S3Key  = "scripts/"
AWS_JSON_PRE: S3Key     = "j/"
AWS_BASES_PRE: S3Key    = "j/b/"
AWS_AWS_PRE: S3Key = "aws/"
AWS_SPEECH_PRE: S3Key = "speech/"
AWS_MANY_PRE: S3Key = "many/" # many/n0, many/n1, ...
AWS_DUSTBIN30_PRE: S3Key = "dustbin30/"

AWS_ABBR_DATA_KEY: S3Key = f"{AWS_JSON_PRE}abbr_data.json.gz"

AWS_MAIN_PRE: S3Key        = f"{AWS_BASES_PRE}m/"
AWS_DELTAS_PRE: S3Key      = f"{AWS_BASES_PRE}d/"
AWS_VERSION_PRE: S3Key     = f"{AWS_BASES_PRE}v/" # will contain an empty file inside like 1735252.txt

AWS_TEXT_HISTORY: S3Key = f"{AWS_JSON_PRE}.text_history.json.gz"
AWS_CLIP_KEY: S3Key = f"{AWS_JSON_PRE}.clips.json.gz"
AWS_SCHEDULE_KEY: S3Key = f"{AWS_JSON_PRE}.schedules.json.gz"

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


def backup_so_files() -> list[str]:
    all_so_paths: list[Path] = []

    main_dir = LOCAL_MAIN_DIR
    tmp_dir = LOCAL_TMP_DIR

    for file in main_dir.iterdir():
        if file.is_file():
            name = file.name
            if name.endswith('.so'):
                all_so_paths.append(file)

    all_tmp_path = []
    for file in all_so_paths:
        tmp_path = tmp_dir / file.name
        try:
            file.copy(tmp_path, preserve_metadata=True)
        except AttributeError: # older python versions
            shutil.copy2(file, tmp_path)
        all_tmp_path.append(tmp_path)

    return all_tmp_path



def restore_so_files(src_paths: list[Path]) -> None:
    main_dir = LOCAL_MAIN_DIR
    
    for file in src_paths:
        dst_path = main_dir / file.name
        try:
            file.copy(dst_path, preserve_metadata=True)
        except AttributeError: # older python versions
            shutil.copy2(file, dst_path)


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

    print("[init] Cleaning target directory:", LOCAL_MAIN_DIR)
    _purge_dir(LOCAL_MAIN_DIR)


    with tempfile.TemporaryDirectory(prefix="flashcards_unpack_") as tmpd:
        tmpd = Path(tmpd)
        print("[init] Extracting archive")
        _extract_tgz_bytes_to_dir(tgz, tmpd) # updated too to handle Path

        # Copy all extracted contents into main_path
        for src in tmpd.iterdir():
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
        print(f"[Error] No version file found in S3. Please run update_flashcards.py from the host device to create one")
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
def getclip(warn_tty: bool=True, debug: bool=False) -> Optional[str]: # copy paste it from utils.py which has the original version
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
        import pyperclip 
        data = pyperclip.paste() 
        if debug:
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
                if debug:
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
                if debug:
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
                if debug:
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
                if debug:
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
                    if debug:
                        print("using TMUX")
                    if warn_tty:
                        print("Pasted from tmux load-buffer")
                    return proc.stdout.decode(errors="replace")
            except Exception:
                pass


    # 7. Total failure
    if debug:
        print("Total Failure")
    return None



# ---------------------------------
def _prompt_line(msg: str) -> str:
    try:
        from prompt_toolkit import prompt
        return prompt(msg)
    except:
        return input(msg)
    

# --------------------------------------
def _prompt_password(msg: str) -> str:
    # prompt_toolkit optional, but getpass is good enough and safe
    return getpass.getpass(msg)




# ===========================
# MARK: AWS API
# ===========================


# ------------------------------------------
def get_creds() -> Optional[dict[str, str]]:
    if not LOCAL_CREDS_PATH.is_file():
        if not coder_main():
            sys.exit(2)
    
    d = decoder_main()
    if d is None:
        sys.exit(2)
    return d
    

# --------------------------------------
def get_s3_bucket(creds: dict[str, str]):
    try:
        import boto3
    except ModuleNotFoundError:
        crint(f"boto3 is not installed. Please install it (python3 -m pip install boto3) or simply run {LOCAL_MAIN_DIR}/dispatch.py --deps.")
        crint('Please restart', 'yellow')
        sys.exit(0)
    S3 = boto3.client(
        "s3",
        aws_access_key_id     = creds["PRIVATE_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key = creds["PRIVATE_AWS_SECRET_ACCESS_KEY"],
        region_name           = creds["PRIVATE_BUCKET_REGION"]
    )
    return S3, creds["PRIVATE_BUCKET_NAME"]


def get_bucket_name(creds: dict[str, str]) -> str:
    return creds["PRIVATE_BUCKET_NAME"]

def get_region_name(creds: dict[str, str]) -> str:
    return creds["PRIVATE_BUCKET_REGION"]

def get_access_secret_keys(creds: dict[str, str]) -> tuple[str, str]:
    return creds["PRIVATE_AWS_ACCESS_KEY_ID"], creds["PRIVATE_AWS_SECRET_ACCESS_KEY"]

# ----------------------------
def get_lambda(creds: dict):
    import boto3
    
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=creds["PRIVATE_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=creds["PRIVATE_AWS_SECRET_ACCESS_KEY"],
        region_name=creds["PRIVATE_BUCKET_REGION"]
    )
    return lambda_client


# -----------------------------------
def get_groq(creds: dict[str, str]) -> str:
    return creds["GROQ_KEY"]


def get_gh_pat(creds: dict[str, str]) -> str:
    return creds["GITHUB_PAT"]





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


# ----------------------------------------------------------------
def _download_bytes_from_s3(bucket: str, key: S3Key, S3) -> bytes:
    obj = S3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read()

# ----------------------------------------------------------------
def _extract_tgz_bytes_to_dir(tgz_bytes: bytes, dest_dir: Path) -> None:
    with io.BytesIO(tgz_bytes) as bio:
        with tarfile.open(fileobj=bio, mode="r:gz") as tf:
            # Extract safely: force no absolute paths, no path traversal
            for member in tf.getmembers():
                member_path = os.path.normpath(member.name).lstrip(os.sep)
                if member_path.startswith(".."):
                    raise RuntimeError(f"Unsafe path in tar: {member.name}")
            tf.extractall(dest_dir, filter="data")

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





# ===========================
# MARK: CREDS (EN)CODER
# ===========================

# ------------------------------------------------------------
def coder_main() -> bool:
    output("Type 'p' to get the value directly from the clipboard (works on termux if termux-api is installed)")

    d = {}
    exits = ['aban', 'exit', 'end', 'ooo']
    for k in AWS_REQ_KEYS:
        while True:
            print()
            crint(k, 'magenta')
            line = _prompt_line(f"{AWS_REQ_KEYS[k]}: ").strip()
            if line.lower() in exits:
                return False
            if line == 'p':
                _tmp = getclip()
                if _tmp is None:
                    crint("Pasting is not possible. Type", 'red')
                    continue
                line = _tmp.strip()
                if _prompt_line(f"Are you sure about {line[:3]}......{line[-3:]}? (y/n): ").strip().lower() != 'y':
                    continue
            if not line:
                continue
            break
        d[k] = line


    if not d:
        print("No valid key/value pairs collected. Exiting.")
        return False

    out_path = LOCAL_CREDS_PATH

    min_len = 10
    while True:
        password = _prompt_password("Encryption password: ")
        if len(password) < min_len:
            output(f"Password is too short. It should be at least {min_len} digits. Try Again ...")
            continue
        
        if password in exits:
            return False
    
        confirm = _prompt_password("Confirm password: ")
        if confirm in exits:
            return False
        if password != confirm:
            print("Passwords do not match. Try Again...")
            continue
        break

    blob = encrypt_dict(d, password)
    tmp_path = out_path.parent / f"{out_path.name}.tmp"

    # atomic-ish write
    with open(tmp_path, "wb") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    tmp_path.replace(out_path)

    output(f"\nSaved {len(d)} entries to encrypted file: {out_path}")
    return True


# ---------------------------------------------
def decoder_main() -> Optional[dict[str, str]]:
    in_path = LOCAL_CREDS_PATH

    if not in_path.is_file():
        print("File not found.")
        if not coder_main():
            print("Exitting")
            sys.exit(2)

    with open(in_path, "rb") as f:
        blob = f.read()


    cached_key = _load_key_cache()
    if cached_key:
        try:
            d = _decrypt_with_cached_key(blob, cached_key)
            if not all(k in d for k in AWS_REQ_KEYS):
                crint("The creds file have invalid keys. Removing it.", 'red')
                in_path.unlink()
                sys.exit(2)
            refresh_cached_key()
            return d
        except:
            pass # fall back to asking password


    password = _prompt_password(f"{PROGRAM_NAME} Password: ")
    if not password:
        print("Empty password not allowed. Exiting.")
        return
    if password == 'reset':
        if _prompt_line("Are you sure you want to reset your password by deleting the existing credentials? (y/n) ") == 'y':
            in_path.unlink()
            crint("Password Reset Successful. Please launch the Program again.", 'green')
            sys.exit(0)
        else:
            crint("Not Reseting", 'red')
            sys.exit(0)

    salt = blob[4:4+SALT_LEN]
    key = derive_key(password, salt)

    try:
        d = _aes_gcm_decrypt(key, blob[4+SALT_LEN:4+SALT_LEN+NONCE_LEN], blob[4+SALT_LEN+NONCE_LEN:], MAGIC)
    except:
        print("Incorrect Password")
        sys.exit(2)

    _store_key_cache(key)
    d: dict[str, str] = json.loads(d.decode())
    if not all(k in d for k in AWS_REQ_KEYS):
        crint("The creds file have invalid keys. Removing it.", 'red')
        os.remove(in_path)
        sys.exit(2)

    return {key: value.strip() for key, value in d.items()}


# -----------------------
def validate_cache():
    """
    Equivalent to: sudo -v
    Refresh TTL if cache exists and is valid.
    """
    refresh = refresh_cached_key()
    if refresh is False:
        decoder_main()
    
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
    parser = argparse.ArgumentParser(
        prog = "cl9",
        description = "The cl9 Learning System"
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




