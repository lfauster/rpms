# Override toolkit with: rpmbuild --define 'cuda_version 13.5'
%{!?cuda_version:%global cuda_version 13.4}
%global cuda_pkgver %(echo %{cuda_version} | tr '.' '-')
%{!?cuda_prefix:%global cuda_prefix /usr/local/cuda-%{cuda_version}}

# GIN benches link libcuda. The real library comes from the host driver.
%global __requires_exclude ^libcuda\\.so.*$

# nvcc fat binaries do not strip cleanly.
%global debug_package %{nil}

Name:           nccl-tests
Version:        2.21.1
Release:        1%{?dist}
Summary:        Performance and correctness tests for NCCL
License:        BSD-3-Clause
URL:            https://github.com/NVIDIA/nccl-tests
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  cuda-nvcc-%{cuda_pkgver}
BuildRequires:  cuda-cudart-devel-%{cuda_pkgver}
BuildRequires:  cuda-opencl-%{cuda_pkgver}
BuildRequires:  cuda-crt-%{cuda_pkgver}
BuildRequires:  cuda-driver-devel-%{cuda_pkgver}
BuildRequires:  libnccl-devel
BuildRequires:  openmpi-cuda-devel

ExclusiveArch:  aarch64 x86_64

%description
NCCL tests check the performance and correctness of NCCL collectives.
This build enables MPI so the tests can run across multiple processes
and nodes with openmpi-cuda.

The Open MPI libraries are not on the default linker path. Launch the
tests with mpirun and put %{_libdir}/openmpi/lib on LD_LIBRARY_PATH.

%prep
%autosetup

%build
# Open MPI headers and libraries live in different prefixes. The Makefile
# looks for both include/ and lib/ under MPI_HOME.
MPI_PREFIX="$PWD/openmpi-prefix"
mkdir -p "$MPI_PREFIX"
ln -sfnT %{_includedir}/openmpi-%{_arch} "$MPI_PREFIX/include"
ln -sfnT %{_libdir}/openmpi/lib "$MPI_PREFIX/lib"

# NCCL_HOME stays unset: libnccl-devel installs headers in /usr/include
# and the library in %%{_libdir}. Setting NCCL_HOME=/usr would add -L/usr/lib.
%make_build MPI=1 \
    MPI_INCLUDE=%{_includedir}/openmpi-%{_arch} \
    MPI_HOME="$MPI_PREFIX" \
    CUDA_HOME=%{cuda_prefix}

%install
install -d %{buildroot}%{_bindir}
install -p -m 755 build/*_perf %{buildroot}%{_bindir}/

install -d %{buildroot}%{_libexecdir}/nccl-tests
if [ -d build/device_api/gin ]; then
    find build/device_api/gin -type f -name '*_perf' | while read -r bin; do
        rel=${bin#build/}
        install -D -p -m 755 "$bin" "%{buildroot}%{_libexecdir}/nccl-tests/${rel}"
    done
fi

%files
%license LICENSE.txt
%doc README.md
%{_bindir}/all_reduce_perf
%{_bindir}/all_gather_perf
%{_bindir}/broadcast_perf
%{_bindir}/reduce_scatter_perf
%{_bindir}/reduce_perf
%{_bindir}/alltoall_perf
%{_bindir}/alltoallv_perf
%{_bindir}/scatter_perf
%{_bindir}/gather_perf
%{_bindir}/sendrecv_perf
%{_bindir}/hypercube_perf
%{_bindir}/comm_ops_perf
%{_libexecdir}/nccl-tests

%changelog
* Thu Oct 22 2026 Loris Fauster <lfauster@redhat.com> - 2.21.1-1
- Initial package
