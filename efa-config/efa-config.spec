# Repackage of efa-config 1.18 from aws-efa-installer 1.50.0.
# Payload sources below are the files from that RPM, unchanged.
# Downstream deltas are applied in %%install:
#   - hugepage script moves from /opt/amazon/bin to %%{_libexecdir}/efa-config
#   - ExecStart in the unit is rewritten to match
#   - vendor preset enables the unit; %%post does not start it

Name:           efa-config
Version:        1.18
Release:        1%{?dist}
Summary:        EFA configuration scripts and files

License:        Apache-2.0
Source0:        efa-hugepages-reserve.sh
Source1:        efa-config.service
Source2:        01_efa.conf
Source3:        01-efa.conf
Source4:        nvidia-aws-platform.conf
Source5:        LICENSE
Source6:        90-efa-config.preset

BuildArch:      noarch
BuildRequires:  systemd-rpm-macros

%{?systemd_requires}
Requires:       pciutils
Requires:       util-linux

%description
efa-config configures huge pages when an EFA device is present and changes
some of the ulimits required for EFA.


%prep
# File sources, no archive to unpack. -c -T creates the build dir
# so %%license can see LICENSE.
%setup -c -T
cp -p %{SOURCE0} efa-hugepages-reserve.sh
cp -p %{SOURCE1} efa-config.service
cp -p %{SOURCE2} 01_efa.conf
cp -p %{SOURCE3} 01-efa.conf
cp -p %{SOURCE4} nvidia-aws-platform.conf
cp -p %{SOURCE5} LICENSE
cp -p %{SOURCE6} 90-efa-config.preset


%build
# Shell and configuration only.


%install
install -Dpm 0755 efa-hugepages-reserve.sh %{buildroot}%{_libexecdir}/efa-config/efa-hugepages-reserve.sh

install -Dpm 0644 efa-config.service %{buildroot}%{_unitdir}/efa-config.service
sed -i 's|^ExecStart=.*|ExecStart=%{_libexecdir}/efa-config/efa-hugepages-reserve.sh|' \
    %{buildroot}%{_unitdir}/efa-config.service

install -Dpm 0644 01_efa.conf %{buildroot}%{_sysconfdir}/security/limits.d/01_efa.conf
install -Dpm 0644 01-efa.conf %{buildroot}%{_sysconfdir}/systemd/system.conf.d/01-efa.conf
install -Dpm 0644 nvidia-aws-platform.conf %{buildroot}%{_sysconfdir}/modprobe.d/nvidia-aws-platform.conf
install -Dpm 0644 90-efa-config.preset %{buildroot}%{_presetdir}/90-efa-config.preset


# Amazon's binary RPM uses %%systemd_post, then also runs
# "systemctl enable" and "systemctl start" with no $1 check, so the
# service is enabled and started on every install and upgrade.
# %%systemd_post applies the vendor preset on first install only.
%post
%systemd_post efa-config.service

%preun
%systemd_preun efa-config.service

%postun
%systemd_postun_with_restart efa-config.service


%files
%license LICENSE
%dir %{_libexecdir}/efa-config
%{_libexecdir}/efa-config/efa-hugepages-reserve.sh
%{_unitdir}/efa-config.service
%{_presetdir}/90-efa-config.preset
%config(noreplace) %{_sysconfdir}/security/limits.d/01_efa.conf
%config(noreplace) %{_sysconfdir}/systemd/system.conf.d/01-efa.conf
%config(noreplace) %{_sysconfdir}/modprobe.d/nvidia-aws-platform.conf


%changelog
* Tue Oct 20 2026 Loris Fauster <lfauster@redhat.com> - 1.18-2
- Repackage efa-config 1.18 from aws-efa-installer 1.50.0
- Install the hugepage script under /usr/libexec instead of /opt/amazon
- Enable the oneshot through a systemd preset instead of systemctl in %%post
