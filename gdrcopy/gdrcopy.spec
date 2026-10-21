# Override toolkit with: rpmbuild --define 'cuda_version 13.5'
# or an explicit path:     rpmbuild --define 'CUDA /path/to/cuda'
%{!?cuda_version:%global cuda_version 13.4}
%global cuda_pkgver %(echo %{cuda_version} | tr '.' '-')
%{!?CUDA: %global CUDA /usr/local/cuda-%{cuda_version}}

# Tools link against libcuda; expect it on the host (driver), not as an RPM dep.
%global __requires_exclude ^libcuda\\.so.*$

Name:           gdrcopy
Version:        2.5.1
Release:        4%{?dist}
Summary:        GDRcopy library
Group:          System Environment/Libraries
License:        MIT
URL:            https://github.com/NVIDIA/gdrcopy
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
# CUDA needed to build the userspace tools (incl. gdrcopy_pplat via nvcc)
BuildRequires:  cuda-nvcc-%{cuda_pkgver}
BuildRequires:  cuda-cudart-devel-%{cuda_pkgver}
BuildRequires:  cuda-driver-devel-%{cuda_pkgver}
BuildRequires:  cuda-crt-%{cuda_pkgver}

# NVIDIA supports ARM64 and and AMD64
ExclusiveArch: aarch64 x86_64

%description
GDRCopy, a low-latency GPU memory copy library and a kernel-mode driver, built on top of the 
NVIDIA GPUDirect RDMA technology.

This package contains the userspace library and diagnostic/benchmark tools.
The kernel module (gdrdrv) is not included.

%package devel
Summary: The development files
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
This package contains header and development files for GDRCopy.

%prep
%autosetup

%build
%make_build config lib exes \
    CUDA=%{CUDA}

%check

%install
# Upstream-style install: lib + tools (no driver/kmod)
%__make install \
    DESTDIR=%{?buildroot} \
    CUDA=%{CUDA} \
    prefix=%{_prefix} \
    exec_prefix=%{_exec_prefix} \
    libdir=%{_libdir} \
    bindir=%{_bindir} \
    includedir=%{_includedir}

%files
%license LICENSE
%doc README.md
%{_bindir}/apiperf
%{_bindir}/copybw
%{_bindir}/copylat
%{_bindir}/sanity
%{_bindir}/gdrcopy_apiperf
%{_bindir}/gdrcopy_copybw
%{_bindir}/gdrcopy_copylat
%{_bindir}/gdrcopy_sanity
%{_bindir}/gdrcopy_pplat
%{_libdir}/libgdrapi.so.*

%files devel
%{_prefix}/include/gdrapi.h
%{_prefix}/include/gdrconfig.h
%{_libdir}/libgdrapi.so

%changelog
* Tue Oct 20 2026 Loris Fauster <lfauster@redhat.com> - 2.5.1-4
- Package userspace tools; no kernel module

* Tue Aug 26 2025 Christian Heimes <cheimes@redhat.com> - 2.5.1-3
- Rewrite spec file for downstream
- Drop DKMS and Kernel module
- Fix CFLAGS and LDFLAGS to use RPM flags and to support debug symbols
- Include LICENSE file
- Resolves: AIPCC-4403

* Mon Aug 04 2025 GPUDirect Team <gpudirect@nvidia.com> 2.5.1-2
- Support RHEL 10.0.
- Support CUDA 13.0.
- Support the CDMM mode.
- Support Blackwell.
- Fix errors when compiling with CUDA 12.6.

* Fri Mar 21 2025 GPUDirect Team <gpudirect@nvidia.com> 2.5-1
- Introduce gdr_pin_buffer_v2 API, GDR_PIN_FLAG_FORCE_PCIE pin flag and the GDR_ATTR_SUPPORT_PIN_FLAG_FORCE_PCIE attribute. Extend gdrcopy_sanity coverage to those new APIs.
- Waive some unit tests in gdrcopy_sanity if the GPU compute mode is not set as default.
- Introduce gdr_get_attribute API and GDR_ATTR_USE_PERSISTENT_MAPPING.
- Add persistent mapping coverage to gdrcopy_sanity.
- Support setting GPU ID in gdrcopy_sanity.
- Fix nvidia_p2p_get_pages_persistent leakage in gdrdrv.
- Introduce leakage_pin_pages_fork_cumemalloc unit test.
- Add support for mix mappings.
- Introduce /proc/driver/gdrdrv/params and /proc/driver/gdrdrv/nv_get_pages_refcount.
- Fix silent failure in gdrcopy_copybw and gdrcopy_apiperf.
- Add -l to shmoo sizes in gdrcopy_copybw.
- Set the default NVCC_FLAGS to generate PTX and SASS for all supported architectures.
- Improve the error reporting in gdrcopy_pplat due to PTX loading errors.
- Add cold cache testing to gdrcopy_copylat.
- Fix errors in gdr_map due to PAT.
- Improve the gdrcopy_pplat algorithm and add more test cases.
- Improve vm_flags_set detection mechanism.
- Change the default to set use_persistent_mapping=1.

* Mon Dec 16 2024 Pak Markthub <pmarkthub@nvidia.com> 2.4.4-1
- Fix the use-after-free bug of mr objects in gdrdv_vma_close.
- Fix the resource leakage bug in gdrdrv_release.

* Mon Dec 02 2024 Pak Markthub <pmarkthub@nvidia.com> 2.4.3-1
- Fix NVIDIA_IS_OPENSOURCE detection when compile with NVIDIA driver version 545 or newer.

* Thu Oct 31 2024 Pak Markthub <pmarkthub@nvidia.com> 2.4.2-1
- Fix the size alignment bug in gdrdrv.
- Fix memory leak in gdr_pin_buffer.
- Add support for another flavor of BF3.

* Mon Dec 18 2023 Pak Markthub <pmarkthub@nvidia.com> 2.4.1-1
- Add support for persistent mapping.
- Fix bug in src/gdrdrv/Makefile.
- Fix compile-time bug when check.h is not found.

* Fri Sep 01 2023 Pak Markthub <pmarkthub@nvidia.com> 2.4-1
- Various bug fixes in the test and benchmark applications.
- Prefix all applications with "gdrcopy_".
- Introduce more unit tests in gdrcopy_sanity.
- Introduce gdrcopy_pplat benchmark application.
- Remove dependency on libcheck and libsubunit
- Introduce gdr_get_info_v2.
- Introduce new copy algorithm for device mappings.
- Add support for NVIDIA BLUEFIELD-3.
- Add support for Linux kernel >= 6.3.
- Add support for SLES and OpenSUSE.
- Add support for systemd service on RHEL9.
- Relicense gdrdrv to Dual MIT/GPL.
- Fix bugs in gdrdrv when pinning two small buffers back-to-back.
- Add support for coherent platforms such as Grace-Hopper.
- Add support for Confidential Computing (CC).

* Fri May 12 2023 Pak Markthub <pmarkthub@nvidia.com> 2.3.1-1
- Add a workaround for the GPL-compatibility issue when compile with CONFIG_ARCH_HAS_CC_PLATFORM on Linux kernel 5.18+.
- Fix error in init.d/gdrcopy due to missing /etc/rc.d/init.d/functions.

* Fri Jul 23 2021 Pak Markthub <pmarkthub@nvidia.com> 2.3-1
- Remove automatically-generated build id links.
- Remove gdrcopy-kmod from the Requires field.
- Add apiperf test.
- Various updates in README.
- Revamp gdrdrv to fix race-condition bugs.

* Mon Feb 01 2021 Pak Markthub <pmarkthub@nvidia.com> 2.2-1
- Add support for ARM64.
- Update various information on README.
- Improve Makefile.
- Add multi-arch support.
- Handle removal of HAVE_UNLOCKED_IOCTL in Linux kernel v5.9 and later.
- Prevent dpkg package creation to unnecessarily compile gdrdrv.
- Improve gdr_open error message.
- Fix bug that prevents sanity from correctly summarizing failure.
- Add dkms support in kmod package.
- Handle the removal of kzfree in Linux kernel v5.10 and later.
- Improve small-size copy-to-mapping.

* Mon Jan 18 2021 Pak Markthub <pmarkthub@nvidia.com> 2.1-2
- Add DKMS support in gdrcopy-kmod.rpm

* Fri Jul 31 2020 Davide Rossetti <drossetti@nvidia.com> 2.1-1
- fix build problem on RHL8 kernels
- relax checks in gdrdrv to support multi-threading use cases
- fix fd leak in gdr_open()

* Mon Mar 02 2020 Davide Rossetti <drossetti@nvidia.com> 2.0-4
- Introduce copylat test application.
- Introduce basic_with_tokens and invalidation_fork_child_gdr_pin_parent_with_tokens sub-tests in sanity.
- Remove the dependency with libcudart.so.
- Clean up the code in the tests folder.
- Change the package maintainer to Davide Rossetti.

* Mon Sep 16 2019 Pak Markthub <pmarkthub@nvidia.com> 2.0-3
- Harden security in gdrdrv.
- Enable cached mappings in POWER9.
- Improve copy performance with unrolling in POWERPC.
- Creates _sanity_ unit test for testing the functionality and security.
- Consolidate basic and _validate_ into sanity unit test.
- Introduce compile time and runtime version checking in libgdrapi.
- Improve rpm packaging.
- Introduce deb packaging for the userspace library and the applications.
- Introduce dkms packaging for the gdrdrv driver.
- Rename gdr_copy_from/to_bar to gdr_copy_from/to_mapping.
- Update README

* Thu Jul 26 2018 Davide Rossetti <davide.rossetti@gmail.com> 1.4-2
- bumped minor version

* Fri Jun 29 2018 Davide Rossetti <davide.rossetti@gmail.com> 1.3-2
- a few bug fixes

* Mon Feb 13 2017 Davide Rossetti <davide.rossetti@gmail.com> 1.2-2
- package libgdrcopy.so as well
- add basic test

* Thu Sep 15 2016 Davide Rossetti <davide.rossetti@gmail.com> 1.2-1
- First version of RPM spec
