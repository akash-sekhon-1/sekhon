#!/bin/bash

# -----------------------------
# Fedora Package Category Setup
# -----------------------------

# Category names (menu order matters)
CATEGORIES=(
  "BASICS"
  "TOOLCHAIN"
  "BUILD_SYSTEMS"
  "KERNEL_TRACING"
  "NETWORKING"
  "DEBUGGING"
  "CPU_PMU"
  "BPF_CORE"
  "SANITIZERS"
  "HELPERS"
  "LUA"
  "FPGA"
  "SECURITY"
  "COMPRESSION"
)

# -----------------------------
# Package lists per category
# -----------------------------

BASICS="xclip vim neovim gedit tilix terminator htop gparted tree curl wget zip unzip p7zip fd-find ripgrep libreoffice"

TOOLCHAIN="gcc gcc-c++ clang clang-tools-extra llvm lld lldb libstdc++-static clang-libs"

BUILD_SYSTEMS="make cmake ninja-build meson pkgconf"

KERNEL_TRACING="kernel-devel kernel-headers bpftool bcc bpftrace perf trace-cmd systemtap dwarves elfutils elfutils-libelf-devel elfutils-devel debuginfod debuginfod-client"

NETWORKING="ethtool rdma-core librdmacm-utils libibverbs-utils libibverbs-devel rdma-core-devel numactl numactl-devel hwloc hwloc-gui dpdk dpdk-tools libpcap-devel linuxptp"

DEBUGGING="gdb gdb-gdbserver strace ltrace valgrind helgrind massif radare2 sysstat iotop perf-tools blktrace tuna"

CPU_PMU="kernel-tools msr-tools cpuid x86info pmu-tools"

BPF_CORE="libbpf libbpf-devel bpftool-devel llvm-devel llvm-static clang-resource-filesystem clang-devel libdw-devel binutils-devel"

SANITIZERS="libasan libasan-static libubsan libubsan-static libtsan libtsan-static liblsan compiler-rt compiler-rt-static"

HELPERS="ccache sccache jq ripgrep fd-find fzf silversearcher-ag"

LUA="lua lua-devel luajit luajit-devel luv-devel"

FPGA="verilog verilator gtkwave yosys iverilog"

SECURITY="audit audit-libs-devel libseccomp libseccomp-devel selinux-policy-devel setools-console policycoreutils-python-utils"

COMPRESSION="xz zstd lz4 rpm-build rpmdevtools cpio p7zip-plugins"

# -----------------------------
# Menu
# -----------------------------

echo ""
echo "===== Fedora Setup Categories ====="
i=1
for cat in "${CATEGORIES[@]}"; do
    echo "  $i) $cat"
    ((i++))
done
echo "  all) Install EVERYTHING"
echo "==================================="
echo ""
read -p "Enter selection (indexes like '1 3 7' or 'all'): " USER_SELECTION
echo ""

# -----------------------------
# Update system
# -----------------------------
sudo dnf upgrade -y || true

# -----------------------------
# Expand "all" to all indexes
# -----------------------------
if [[ "$USER_SELECTION" == "all" ]]; then
    USER_SELECTION=""
    for idx in $(seq 1 ${#CATEGORIES[@]}); do
        USER_SELECTION+="$idx "
    done
fi

# -----------------------------
# Install selected categories
# -----------------------------

for index in $USER_SELECTION; do
    if ! [[ "$index" =~ ^[0-9]+$ ]]; then
        echo "Skipping invalid input: $index"
        continue
    fi

    # Convert index → category name
    category="${CATEGORIES[$((index-1))]}"

    if [[ -z "$category" ]]; then
        echo "Invalid index: $index"
        continue
    fi

    echo ">>> Installing category: $category"
    pkglist="${!category}"

    sudo dnf install -y --skip-unavailable $pkglist
done

echo ""
echo "===== DONE ====="
echo "Selected package categories installed."
