

"""
cl9.py

1. This module is available publically at curl -O https://raw.githubusercontent.com/akash-sekhon-1/sekhon/main/scripts/cl9.py

2. I can download it from anywhere globally and set up my system in seconds. This script is meant to be strictly stand-alone. 

3. This is for PERSONAL USE ONLY
"""

# ===========================
# IMPORTS
# ===========================

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
from socket import gethostname
from textwrap import fill
from typing import Dict, Optional
from uuid import uuid4


# ===========================
# GLOBAL
# ===========================
poin = os.path.join
PC_login_name: str = "akash@n0"
login_name: str = f"{getuser()}@{gethostname()}" # fast wifi PC where compaction happens automatically
MAIN_PC: bool = PC_login_name == login_name
HOME: str = os.path.expanduser("~")


if MAIN_PC and os.path.exists(poin(HOME, "cl9_dev")) and os.path.abspath(os.path.relpath(__file__)) == poin(HOME, "cl9_dev/m/cl9.py"):
    print("DEVELOPMENT MODE ON")
    PROGRAM_NAME = 'cl9_dev'
    DEV_PC = True
else:
    PROGRAM_NAME = 'cl9'
    DEV_PC = False

prefer_conda = True # if anaconda3/bin/python3 is present prefer it over python3, if False uses python3 always

# ===========================
# MARK: PATH CONST
# ===========================

LOCAL_AG_DIR            = os.path.expanduser(f"~/{PROGRAM_NAME}")
ALIAS_REL_PATH          = ".cl9_aliases"
LOCAL_DUSTBIN           = os.path.expanduser(f"~/AD_4M")

LOCAL_MAIN_DIR          = poin(LOCAL_AG_DIR, "m")
LOCAL_JSON_DIR          = poin(LOCAL_AG_DIR, "j")
LOCAL_TMP_DIR           = poin(LOCAL_AG_DIR, "tmp")
LOCAL_BAK_DIR           = poin(LOCAL_AG_DIR, 'bak')

# SUB DIRS
LOCAL_SUB_MAIN_DIR      = poin(LOCAL_JSON_DIR, 'm')
LOCAL_SUB_DELTAS_DIR    = poin(LOCAL_JSON_DIR, 'u')
LOCAL_VERSION_DIR       = poin(LOCAL_JSON_DIR, 'v')

# BACK UPS
LOCAL_FILES_BU_DIR      = poin(LOCAL_AG_DIR, "automated_backups/flashcards_all") # for daily backups
LOCAL_SCRIPTS_BU_DIR    = poin(LOCAL_AG_DIR, "automated_backups/scripts") # for backup before init

# OTHERS
LOCAL_DUP_CHECK_JSON    = poin(LOCAL_JSON_DIR, "duplication_check_file.json")
LOCAL_T_DUP_CHECK_JSON  = poin(LOCAL_JSON_DIR, "task_dup_check.json")
LOCAL_LOG_PATH          = poin(LOCAL_JSON_DIR, "log_err.txt")
LOCAL_CAREER_NEWS       = poin(LOCAL_JSON_DIR, "career_news.json")
LOCAL_CREDS_PATH         = poin(LOCAL_JSON_DIR, ".creds")

LOCAL_TEXT_HISTORY =    poin(LOCAL_JSON_DIR, ".text_history.json.gz") # THIS path is also mentioned in ins_adder.py (not imported to keep that fast)
# has two keys, 'last_sync': ts and 'history': {hash: date}

# PUBLIC
LOCAL_CL9_NAME = 'cl9.py'
LOCAL_INF_NAME = 'inf.py'

LOCAL_CL9_PATH = poin(LOCAL_MAIN_DIR, LOCAL_CL9_NAME)
LOCAL_INF_PATH = poin(LOCAL_MAIN_DIR, LOCAL_INF_NAME)
LOCAL_BASH_DIR = poin(LOCAL_MAIN_DIR, 'bash')


MAIN_SUFFIX: str    = "m.gz"
DELTA_SUFFIX: str   = "d.gz"
VERSION_SUFFIX: str = "v.gz"


# two stat(2) + mkdir(2) calls if doesn't exist, else only 1 stat(2) call, thus optimal when direc mostly exists
for direc in (LOCAL_AG_DIR, LOCAL_JSON_DIR, LOCAL_FILES_BU_DIR, LOCAL_SCRIPTS_BU_DIR, LOCAL_MAIN_DIR, LOCAL_SUB_MAIN_DIR, LOCAL_VERSION_DIR, LOCAL_SUB_DELTAS_DIR, LOCAL_TMP_DIR, LOCAL_BAK_DIR):
    if not os.path.exists(direc):
        os.makedirs(direc)

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

AWS_SCRIPTS_PRE  = "scripts"
AWS_JSON_PRE     = "j"
AWS_AWS_PRE = "aws"

AWS_SUB_MAIN_PRE   = f"{AWS_JSON_PRE}/m"
AWS_SUB_DELTAS_PRE = f"{AWS_JSON_PRE}/u"
AWS_VERSION_PRE    = f"{AWS_JSON_PRE}/v" # will contain an empty file inside like 1735252.txt

AWS_TEXT_HISTORY = f"{AWS_JSON_PRE}/.text_history.json.gz"
# has two keys, 'last_sync': ts and 'history': {hash: date}


AWS_TGZ_KEY  = f"{AWS_SCRIPTS_PRE}/complete_flashcard_program.tgz"
AWS_CL9_KEY = f"{AWS_SCRIPTS_PRE}/{LOCAL_CL9_NAME}"
AWS_INF_KEY = f"{AWS_SCRIPTS_PRE}/{LOCAL_INF_NAME}"



# ===========================
# MARK: TIME CONST
# ===========================

TIME_FMT: str = "%Y-%m-%d_%H:%M:%S"
DATE_FMT: str = "%Y-%m-%d"
MONTH_FMT: str = '%Y-%m'



# ===========================
# MARK: CRYPTO CONST
# ===========================

# ----------------------------------------------
def _cache_path():
    run_dir = f"/run/user/{os.getuid()}"
    if os.path.isdir(run_dir):
        return os.path.join(run_dir, f"{PROGRAM_NAME}_passcache")
    return os.path.join(tempfile.gettempdir(), f"{PROGRAM_NAME}_passcache") # for termux



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
# MARK: SELECTION
# ===========================

# -----------------------------------
def _get_fp(path:str) -> str:
    return os.path.expanduser(f"~/{path}")

# -----------------------------------------
def _get_py() -> str:
    conpy = _get_fp("anaconda3/bin/python3") 
    if prefer_conda:
        return conpy if os.path.exists(conpy) else 'python3'
    return 'python3'




# ===========================
# MARK: NATIVE DISPATCH
# ===========================


# -------------------------------------
def _setup_aliases() -> int:
    """
    Setups the aliases if they don't exist already.
    Returns 0 if aliases already existed. Returns 1 if just created (print refresh .bashrc)
    """
    alias_path = _get_fp(ALIAS_REL_PATH)

    py = _get_py()
    _p = LOCAL_MAIN_DIR 
    f_aliases: str = f"""

# cl9 Aliases

alias ad='{py} {_p}/add_auto.py'
alias adt='{py} {_p}/add_tasks.py'
alias aws='{py} {_p}/aws.py'
alias bak='{py} {_p}/bak.py'
alias chat='{py} {_p}/chat.py'
alias cl9='{py} {_p}/cl9.py'
alias cotes='{py} {_p}/cotes.py'
alias mtl='{py} {_p}/mtl.py'
alias rev='{py} {_p}/__main__.py'
alias todo='{py} {_p}/todo.py'
alias tools='{py} {_p}/tools.py'

"""


    alias_exist = False
    if os.path.exists(alias_path):
        with open(alias_path, 'r') as f:
            if f_aliases == f.read():
                alias_exist = True
    
    if not alias_exist:
        with open(alias_path, 'w') as f1:
            f1.write(f_aliases)
    
    bashrc_path = _get_fp(".bashrc")
    src_cmd = f"\n\n# Sourcing cl9 aliases\nsource {alias_path}\n"
    if os.path.exists(_get_fp(".bashrc")):
        with open(bashrc_path, 'r') as f:
            if src_cmd not in f.read():
                with open(bashrc_path, 'a') as f:
                    f.write(src_cmd)

    if not alias_exist:
        return 1
    return 0


# ----------------------
def get_cl9(): # --cl9
    try:
        import boto3
        import rich
        import prompt_toolkit
    except ModuleNotFoundError: # this simple check will make sure termux-api is installed for pasting credentials easily
        native_reqs()
        crint("Dependencies installed. Please run the same command again")
        sys.exit(0)

    if DEV_PC:
        crint("This operation is not allowed on the DEV MODE", 'red')
        return 0

    __creds = get_creds()
    S3, BUCKET_NAME = get_s3_bucket(__creds)

    # backup the previous stuff first
    before_backup_path = os.path.join(
        LOCAL_SCRIPTS_BU_DIR,
        datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    )
    os.makedirs(before_backup_path, exist_ok=True)

    shutil.copytree(LOCAL_MAIN_DIR, before_backup_path, dirs_exist_ok=True)  # Copies everything
    print("Current backup taken")

    print("\n[init] Fetching program archive from S3 ...")
    tgz = _download_bytes_from_s3(BUCKET_NAME, AWS_TGZ_KEY, S3)

    print("[init] Cleaning target directory:", LOCAL_MAIN_DIR)
    _purge_dir(LOCAL_MAIN_DIR)

    with tempfile.TemporaryDirectory(prefix="flashcards_unpack_") as tmpd:
        print("[init] Extracting archive")
        _extract_tgz_bytes_to_dir(tgz, tmpd)

        # Copy all extracted contents into main_path
        for name in os.listdir(tmpd):
            src = os.path.join(tmpd, name)
            dst = os.path.join(LOCAL_MAIN_DIR, name)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

    # Remove previous versions
    for v in [os.path.join(LOCAL_VERSION_DIR, ver) for ver in os.listdir(LOCAL_VERSION_DIR)]:
        os.remove(v)

    versions = list_s3_objects(AWS_VERSION_PRE, BUCKET_NAME, S3)
    if len(versions) == 1: # usual case
        version = versions[0]
    elif len(versions) > 1:
        version = max(versions, key=lambda x: float(x.remove_suffix(VERSION_SUFFIX)))
    else:
        print(f"[Error] No version file found. Please run update_flashcards.py from the host device to create one")
        return 1

    if save_file_from_aws(version, poin(LOCAL_VERSION_DIR, os.path.basename(version)), BUCKET_NAME, S3):
        print('version updated successfully.')
    else:
        print("[Error] Failed to download the latest version")
        return 1

    print("\n[init] Update complete.")
    return 0






# ===========================
# MARK: BASH DISPATCH
# ===========================

# -----------------------------
def launch_bash(script: str):
    tmp_path: str = os.path.join(LOCAL_TMP_DIR, uuid4().hex) # compatible even on termux
    try:
        with open(tmp_path, 'w') as f:
            f.write(script)

        os.chmod(tmp_path, 0o755)
        try:
            subprocess.run(["bash", tmp_path], check=False)
        except (KeyboardInterrupt, EOFError):
            crint("Exitting safely", 'orange')
    finally:
        os.remove(tmp_path)


# ----------------------------
def native_reqs(): # --cl9
    """
    Requirements needed for running the flashcards script
    """
    py = _get_py()
    PY_ONLY_SCRIPT = f"""
    
#!/bin/bash


# FEDORA
if command -v dnf >/dev/null 2>&1; then
    echo "You are using dnf based platform"
    sudo dnf install xclip || echo "failed: xclip"

    echo "Ensuring and Downloading pip"
    {py} -m ensurepip || true
    {py} -m pip install --upgrade pip || true

    echo "Installing required python third party packages"
    {py} -m pip install prompt_toolkit rich boto3 pyperclip || true


# TERMUX
elif command -v pkg >/dev/null 2>&1; then
    echo "You are using Termux"
    pkg update -y || true
    pkg upgrade -y || true
    pkg install -y python || true
    pkg install -y termux-api || true
    

    echo "Ensuring and Downloading pip"
    {py} -m ensurepip || true   # pip upgrade forbidden on termux

    echo "Installing required python third party packages"
    {py} -m pip install prompt_toolkit rich boto3 || true
    # pyperclip may fail on termux



# Arch Linux
elif command -v pacman >/dev/null 2>&1; then
    echo "You are using Arch-based platform"
    sudo pacman -S xclip || true

    # ensure python + pip exist
    sudo pacman -S --noconfirm python python-pip || true

    echo "Ensuring and Downloading pip"
    {py} -m ensurepip || true
    {py} -m pip install --upgrade pip || true

    echo "Installing required python third party packages"
    {py} -m pip install prompt_toolkit rich boto3 pyperclip || true



# UBUNTU / Debian
elif command -v apt-get >/dev/null 2>&1; then
    echo "You are using Ubuntu/Debian"
    sudo apt install xclip || echo "failed: xclip"

    echo "Ensuring and downloading pip"
    {py} -m ensurepip || true
    {py} -m pip install --upgrade pip || true

    echo "Installing required python third party packages"
    {py} -m pip install prompt_toolkit rich boto3 pyperclip || true



else
    echo "Unknown System detection: Please run update and upgrade" || true

    echo "Ensuring and Downloading pip"
    {py} -m ensurepip || true
    {py} -m pip install --upgrade pip || true

    echo "Installing required python third party packages"
    {py} -m pip install prompt_toolkit rich boto3 || true
    {py} -m pip install pyperclip || true  # separated because it may fail on some systems
fi
"""

    launch_bash(PY_ONLY_SCRIPT)
    r = _setup_aliases()
    if r == 1:
        print("\nPlease run source ~/.bashrc to refresh aliases")
    return





# ===========================
# MARK: INPUT
# ===========================

# -----------------------------
def getclip() -> Optional[str]:
    """
    Robust clipboard getter.
    Priority:
        1. pyperclip.paste
        2. xclip (subprocess)
        3. termux-clipboard-get (Termux)
    Returns:
        str on success,
        None on failure.
    Never raises.
    """

    # 1. pyperclip
    try:
        import pyperclip
        data = pyperclip.paste()
        # pyperclip returns '' on empty clipboard, treat as success
        return data if isinstance(data, str) else None
    except Exception:
        pass

    # 2. xclip
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
                return proc.stdout.decode(errors="replace")
        except Exception:
            pass

    # 3. Termux
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
                return proc.stdout.decode(errors="replace")
        except Exception:
            pass

    # 4. Total failure
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
    if not os.path.exists(LOCAL_CREDS_PATH):
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
        crint(f"boto3 is not installed. Please install it or simply run ~/{LOCAL_MAIN_DIR}/init_flashcards.py --py. Trying automatically")
        native_reqs()
        crint('Please restart', 'yellow')
        sys.exit(0)
    S3 = boto3.client(
        "s3",
        aws_access_key_id     = creds["PRIVATE_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key = creds["PRIVATE_AWS_SECRET_ACCESS_KEY"],
        region_name           = creds["PRIVATE_BUCKET_REGION"],
    )
    return S3, creds["PRIVATE_BUCKET_NAME"]


# -----------------------------------
def get_groq(creds: dict[str, str]) -> str:
    return creds["GROQ_KEY"]


def get_gh_pat(creds: dict[str, str]) -> str:
    return creds["GITHUB_PAT"]





# ===========================
# MARK: S3 FILE UTILS
# ===========================

# ----------------------------------------------------------------
def _purge_dir(path: str) -> None:
    """
    Remove all contents of `path` (files and directories). Path itself is preserved.
    """
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        return
    for entry in os.listdir(path):
        p = os.path.join(path, entry)
        try:
            if os.path.islink(p) or os.path.isfile(p):
                os.remove(p)
            else:
                shutil.rmtree(p)
        except Exception as e:
            print(f"[WARN] Failed to delete {p}: {e!r}")


# ----------------------------------------------------------------
def _download_bytes_from_s3(bucket: str, key: str, S3) -> bytes:
    obj = S3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read()

# ----------------------------------------------------------------
def _extract_tgz_bytes_to_dir(tgz_bytes: bytes, dest_dir: str) -> None:
    with io.BytesIO(tgz_bytes) as bio:
        with tarfile.open(fileobj=bio, mode="r:gz") as tf:
            # Extract safely: force no absolute paths, no path traversal
            for member in tf.getmembers():
                member_path = os.path.normpath(member.name).lstrip(os.sep)
                if member_path.startswith(".."):
                    raise RuntimeError(f"Unsafe path in tar: {member.name}")
            tf.extractall(dest_dir, filter="data")

# ----------------------------------------------------------------
def save_file_from_aws(aws_key: str, dest_name: str, bucket_name: str, S3) -> bool:
    """
    Simple version: directly downloads a file from AWS S3 and writes to disk.
    No atomic writes, no rollback, no temporary paths.
    """
    try:
        _dir_name = os.path.dirname(dest_name)
        if not os.path.exists(_dir_name):
            os.makedirs(_dir_name)
        S3.download_file(bucket_name, aws_key, dest_name)
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
                line = _tmp
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
    if not out_path:
        print("Empty path. Exiting.")
        return False

    min_len = 5
    while True:
        password = _prompt_password("Encryption password: ")
        if len(password) < min_len:
            output(f"Password is too short. It should be at least {min_len} digits. Try Again ...")
            continue
        if password == 'reset':
            print("reset as password is forbidden. Try again ...")
            continue
        break

    if password in exits:
        return False
    
    while True:
        confirm = _prompt_password("Confirm password: ")
        if confirm in exits:
            return False
        if password != confirm:
            print("Passwords do not match. Try Again...")
            continue
        break

    blob = encrypt_dict(d, password)
    tmp_path = out_path + ".tmp"

    # atomic-ish write
    with open(tmp_path, "wb") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, out_path)

    output(f"\nSaved {len(d)} entries to encrypted file: {out_path}")
    return True


# ---------------------------------------------
def decoder_main() -> Optional[dict[str, str]]:
    in_path = LOCAL_CREDS_PATH
    if not in_path:
        print("Empty path. Exiting.")
        return
    if not os.path.exists(in_path):
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
                os.remove(in_path)
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
            os.remove(in_path)
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
    d = json.loads(d.decode())
    if not all(k in d for k in AWS_REQ_KEYS):
        crint("The creds file have invalid keys. Removing it.", 'red')
        os.remove(in_path)
        sys.exit(2)
    return d


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
        os.remove(KEY_CACHE)
        print("File cache invalidated.")
        removed = True
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error invalidating file cache: {e}")

    if not removed:
        print("No cache present.")



# ------------------------
HELP_TEXT = """
cl9 cache control tool

Usage:
    cl9 -v        Validate/refresh cache TTL (like sudo -v)
    cl9 -i        Invalidate/delete cache
    cl9 --help    Show this help message
    cl9 --fetch   Fetches the latest verison of cl9 from the private bucket
    cl9 --py      Installs the required third-party packages

Description:

  -v (validate):
      If a valid key-cache exists, its TTL is refreshed.
      If no cache exists, nothing happens.

  -i (invalidate):
      Deletes the cache file if present.

"""





def main():
    if len(sys.argv) != 2:
        print(HELP_TEXT.strip())
        sys.exit(1)

    arg = sys.argv[1].strip()

    if arg == "--help":
        print(HELP_TEXT.strip())
        sys.exit(0)

    elif arg == "-v":
        validate_cache()
        sys.exit(0)

    elif arg == "-i":
        invalidate_cache()
        sys.exit(0)

    elif arg == "--fetch":
        get_cl9()

    elif arg == "--py":
        native_reqs()    

    else:
        print("Unknown flag.")
        print(HELP_TEXT.strip())
        sys.exit(1)


if __name__ == "__main__":
    main()
