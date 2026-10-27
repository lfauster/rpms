Name:           nvidia-gpu-tweaks
Version:        1.0
Release:        1%{?dist}
Summary:        Set NVIDIA GPU clocks to AWS-recommended maximums

License:        Apache-2.0
URL:            https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/optimize_gpu.html
Source0:        nvidia-gpu-tweaks
Source1:        nvidia-gpu-tweaks.service
Source2:        90-nvidia-gpu-tweaks.preset
Source3:        LICENSE

BuildArch:      noarch
BuildRequires:  systemd-rpm-macros

%{?systemd_requires}
Requires:       nvidia-persistenced

%description
nvidia-gpu-tweaks sets NVIDIA GPU and memory clocks to the maximum
frequencies AWS documents for EC2 GPU instance types. It runs once at
boot after nvidia-persistenced, and exits without changes when nvidia-smi
is missing or the GPU is not in the supported set.


%prep
# File sources, no archive to unpack. -c -T creates the build dir
# so %%license can see LICENSE.
%setup -c -T
cp -p %{SOURCE0} nvidia-gpu-tweaks
cp -p %{SOURCE1} nvidia-gpu-tweaks.service
cp -p %{SOURCE2} 90-nvidia-gpu-tweaks.preset
cp -p %{SOURCE3} LICENSE


%build
# Shell and configuration only.


%install
install -Dpm 0755 nvidia-gpu-tweaks %{buildroot}%{_libexecdir}/nvidia-gpu-tweaks
install -Dpm 0644 nvidia-gpu-tweaks.service %{buildroot}%{_unitdir}/nvidia-gpu-tweaks.service
install -Dpm 0644 90-nvidia-gpu-tweaks.preset %{buildroot}%{_presetdir}/90-nvidia-gpu-tweaks.preset


# %%systemd_post applies the vendor preset on first install only.
%post
%systemd_post nvidia-gpu-tweaks.service

%preun
%systemd_preun nvidia-gpu-tweaks.service

%postun
%systemd_postun_with_restart nvidia-gpu-tweaks.service


%files
%license LICENSE
%{_libexecdir}/nvidia-gpu-tweaks
%{_unitdir}/nvidia-gpu-tweaks.service
%{_presetdir}/90-nvidia-gpu-tweaks.preset


%changelog
* Tue Oct 27 2026 Loris Fauster <lfauster@redhat.com> - 1.0-1
- Package the ami-nvidia GPU clock script and oneshot unit
- Enable the unit through a systemd preset
