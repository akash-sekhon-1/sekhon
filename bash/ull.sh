#!/bin/bash

# ULL SETUP (includes BASICS + ULL)

# FEDORA
if command -v dnf >/dev/null 2>&1; then
    echo -e "\nYou are using dnf based platform.\n"
    sudo dnf upgrade -y || true

    # BASICS
    for pkg in xclip vim neovim gedit tilix terminator htop gparted tree curl wget zip unzip p7zip fd-find ripgrep; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # TOOLCHAIN
    for pkg in gcc gcc-c++ clang clang-tools-extra llvm lld lldb libstdc++-static clang-libs; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # BUILD SYSTEMS
    for pkg in make cmake ninja-build meson pkgconf; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # KERNEL / BPF / TRACING
    for pkg in kernel-devel kernel-headers bpftool bcc bpftrace perf trace-cmd systemtap dwarves elfutils elfutils-libelf-devel elfutils-devel debuginfod debuginfod-client; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # NETWORKING / RDMA / DPDK / NUMA
    for pkg in ethtool rdma-core librdmacm-utils libibverbs-utils libibverbs-devel rdma-core-devel numactl numactl-devel hwloc hwloc-gui dpdk dpdk-tools libpcap-devel linuxptp; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # DEBUGGING / PROFILING
    for pkg in gdb gdb-gdbserver strace ltrace valgrind helgrind massif radare2 sysstat iotop perf-tools blktrace tuna; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # CPU / MICROARCH / PMU TOOLS
    for pkg in kernel-tools msr-tools cpuid x86info pmu-tools; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # BPF / CO-RE / DEV TOOLCHAIN
    for pkg in libbpf libbpf-devel bpftool-devel llvm-devel llvm-static clang-resource-filesystem clang-devel libdw-devel binutils-devel; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # SANITIZERS / COMPILER-RT
    for pkg in libasan libasan-static libubsan libubsan-static libtsan libtsan-static liblsan compiler-rt compiler-rt-static; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # HELPERS
    for pkg in ccache sccache jq ripgrep fd-find fzf silversearcher-ag; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # LUA / LUAJIT
    for pkg in lua lua-devel luajit luajit-devel luv-devel; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # FPGA / HDL
    for pkg in verilog verilator gtkwave yosys iverilog; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # SECURITY
    for pkg in audit audit-libs-devel libseccomp libseccomp-devel selinux-policy-devel setools-console policycoreutils-python-utils; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # COMPRESSION / RPM DEV
    for pkg in xz zstd lz4 rpm-build rpmdevtools cpio p7zip-plugins; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done

    # DNF PLUGINS
    sudo dnf install -y dnf-plugins-core || true

    # DEBUGINFO (kernel + glibc)
    sudo dnf debuginfo-install -y kernel glibc libcxx || true

    # IDE
    sudo dnf install -y spyder || true


# TERMUX
elif command -v pkg >/dev/null 2>&1; then
    echo "You are using Termux"
    pkg update -y || true
    pkg upgrade -y || true

    # BASICS
    for pkg in xclip vim neovim htop tree curl wget zip unzip p7zip ripgrep fd; do
        pkg install -y "$pkg" || echo "failed: $pkg"
    done

    # TOOLCHAIN (limited)
    for pkg in clang llvm lld; do
        pkg install -y "$pkg" || echo "failed: $pkg"
    done

    # DEBUGGING
    for pkg in gdb strace ltrace; do
        pkg install -y "$pkg" || echo "failed: $pkg"
    done

    # LUA / LUAJIT
    for pkg in lua lua54 luajit; do
        pkg install -y "$pkg" || echo "failed: $pkg"
    done




# ARCH
elif command -v pacman >/dev/null 2>&1; then
    echo "You are using Arch-based platform"
    sudo pacman -Syu --noconfirm || true

    # BASICS
    for pkg in xclip vim neovim gedit tilix terminator htop gparted tree curl wget zip unzip p7zip ripgrep fd; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done

    # TOOLCHAIN
    for pkg in gcc clang llvm lld lldb; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done

    # BUILD SYSTEMS
    for pkg in make cmake ninja; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done

    # KERNEL / BPF / TRACING
    for pkg in linux-headers bpftrace bpftool perf strace systemtap; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done

    # NETWORKING / RDMA / DPDK / NUMA
    for pkg in ethtool rdma-core libibverbs numactl hwloc dpdk; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done

    # DEBUGGING
    for pkg in gdb valgrind radare2 sysstat iotop; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done

    # CPU / MICROARCH / PMU TOOLS
    for pkg in msr-tools cpuid x86info; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done

    # BPF / CO-RE / DEV TOOLCHAIN
    for pkg in libbpf llvm-libs; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done

    # HELPERS
    for pkg in ccache sccache jq ripgrep fd; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done

    # LUA / LUAJIT
    for pkg in lua luajit; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done

    # FPGA / HDL
    for pkg in verilator gtkwave yosys; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done




# UBUNTU / DEBIAN
elif command -v apt-get >/dev/null 2>&1; then
    echo "You are using Ubuntu/Debian"

    sudo apt-get update -y || true
    sudo apt-get upgrade -y || true

    # BASICS
    for pkg in xclip vim neovim gedit tilix terminator htop gparted tree curl wget zip unzip p7zip-full ripgrep fd-find; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # TOOLCHAIN
    for pkg in gcc g++ clang clang-tools llvm lld lldb; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # BUILD SYSTEMS
    for pkg in make cmake ninja-build gparted; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # KERNEL / BPF / TRACING
    for pkg in linux-headers-$(uname -r) bpftool bpfcc-tools bpftrace linux-tools-common linux-tools-$(uname -r) systemtap-sdt-dev dwarves; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # NETWORKING / RDMA / DPDK / NUMA
    for pkg in ethtool rdma-core ibverbs-providers rdmacm-utils numactl hwloc dpdk dpdk-dev; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # DEBUGGING
    for pkg in gdb gdbserver strace ltrace valgrind sysstat iotop radare2; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # CPU / MICROARCH / PMU TOOLS
    for pkg in msr-tools cpuid; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # BPF / CO-RE / DEV TOOLCHAIN
    for pkg in libbpf-dev libbpf1 llvm-dev libdw-dev binutils-dev; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # HELPERS
    for pkg in ccache jq ripgrep fd-find; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # LUA / LUAJIT / Neovim ecosystem
    for pkg in lua5.4 liblua5.4-dev luajit libluajit-5.1-dev; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # FPGA / HDL
    for pkg in verilator gtkwave yosys; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # SECURITY
    for pkg in auditd libseccomp-dev selinux-utils selinux-basics; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

    # COMPRESSION / RPM tools
    for pkg in xz-utils zstd lz4 rpm rpm2cpio; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

fi
