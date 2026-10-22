#!/usr/bin/env rpm

# RHEL adaptation of upstream contrib/fedora/aws-ofi-nccl.spec.
# Resolve the upstream release placeholders and use standard RHEL RPM paths.
%{!?cuda_version:%global cuda_version 13.4}
%global cuda_pkgver %(echo %{cuda_version} | tr '.' '-')
%{!?cuda_prefix:%global cuda_prefix /usr/local/cuda-%{cuda_version}}

# The plugin loads CUDA Runtime APIs dynamically by default. Keep the RPM from
# requiring libcudart unless the packager explicitly opts into dependency tracking.
%{!?enable_cudart_dep_tracking: %global enable_cudart_dep_tracking 0}
%if %{enable_cudart_dep_tracking} == 0
%if %{?__requires_exclude:1}%{!?__requires_exclude:0}
%global __requires_exclude %{__requires_exclude}|^libcudart.so
%else
%global __requires_exclude ^libcudart.so
%endif
%endif

Name:           libnccl-ofi
Version:        1.21.1
Release:        2%{?dist}
Summary:        NCCL and libfabric compatibility layer
License:        Apache-2.0
URL:            https://github.com/aws/aws-ofi-nccl
Source0:        https://github.com/aws/aws-ofi-nccl/releases/download/v%{version}/aws-ofi-nccl-%{version}.tar.gz

BuildRequires:  autoconf
BuildRequires:  autoconf-archive
BuildRequires:  automake
BuildRequires:  gcc-c++
BuildRequires:  hwloc-devel
# Needed by hwloc-libs
BuildRequires:  cuda-opencl-%{cuda_pkgver}
BuildRequires:  cuda-crt-%{cuda_pkgver}
BuildRequires:  libfabric-devel >= 1.22.0
BuildRequires:  gdrcopy-devel
BuildRequires:  cuda-cudart-devel-%{cuda_pkgver}
BuildRequires:  libtool
BuildRequires:  make
BuildRequires:  pkgconf-pkg-config

AutoProv:       yes

%description
AWS OFI NCCL is a plugin that lets NCCL applications use libfabric as their
network provider. This build enables AWS platform support for EFA deployments.

%prep
%setup -q -n aws-ofi-nccl-%{version}

%build
cuda_path="%{cuda_prefix}"
if [ ! -f "$cuda_path/include/cuda.h" ]; then
    cuda_path=$(find /usr/local -maxdepth 1 -type d -name 'cuda-*' -print | sort -V | tail -n 1)
fi
if [ -z "$cuda_path" ] || [ ! -f "$cuda_path/include/cuda.h" ]; then
    echo "CUDA headers not found; install the CUDA Toolkit or set --define 'cuda_prefix PATH'." >&2
    exit 1
fi
test -f "%{_includedir}/rdma/fabric.h" || {
    echo "Libfabric headers not found; install libfabric-devel." >&2
    exit 1
}
%configure --disable-picky-compiler \
           --with-cuda="$cuda_path" \
           --enable-cudart-dynamic \
           --with-gdrcopy \
           --disable-werror \
           --disable-tests \
           --enable-platform-aws
%make_build

%install
%make_install
find %{buildroot} -name '*.la' -delete

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%{_libdir}/*.so
%{_datadir}/aws-ofi-nccl/xml/*.xml
%license LICENSE NOTICE

%changelog
* Thu Oct 22 2026 Loris Fauster <lfauster@redhat.com> - 1.21.1-2
- Enable GDRCopy support

* Thu Oct 15 2026 Loris Fauster <lfauster@redhat.com> - 1.21.1-1
- Initial package
