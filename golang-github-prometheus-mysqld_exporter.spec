# Run tests (requires network connectivity)
%global with_check 0

# Prebuilt binaries break build process for CentOS. Disable debug packages to resolve
%if 0%{?rhel}
%define debug_package %{nil}
%endif

%global provider        github
%global provider_tld    com
%global project         prometheus
%global repo            mysqld_exporter
# https://github.com/prometheus/mysqld_exporter/
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}

Name:           golang-%{provider}-%{project}-%{repo}
Version:        0.12.1
Release:        2%{?dist}
Summary:        MySQL metrics exporter
License:        ASL 2.0
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/v%{version}.tar.gz
Source1:        mysqld_exporter.service
Source2:        sysconfig.mysqld_exporter

Provides:       mysqld_exporter = %{version}-%{release}

%if 0%{?rhel} != 6
BuildRequires:  systemd
%endif

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%description
Prometheus exporter for MySQL server metrics.
Supports MySQL & MariaDB versions: 5.5 and up.

%prep
%setup -q -n %{repo}-%{version}

%build
export GO111MODULE=on
go build -ldflags=-linkmode=external -mod vendor -o mysqld_exporter

%install
%if 0%{?rhel} != 6
install -d -p   %{buildroot}%{_unitdir}
%endif

install -Dpm 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/mysqld_exporter/mysqld_exporter.conf
install -Dpm 0755 mysqld_exporter %{buildroot}%{_sbindir}/mysqld_exporter
%if 0%{?rhel} != 6
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_unitdir}/mysqld_exporter.service
%endif

%if 0%{?with_check}
%check
export GO111MODULE=on
go test -mod vendor
%endif


%files
%if 0%{?rhel} != 6
%{_unitdir}/mysqld_exporter.service
%endif
%attr(0640, mysqld_exporter, mysqld_exporter) %config(noreplace) %{_sysconfdir}/mysqld_exporter/mysqld_exporter.conf
%license LICENSE
%doc README.md
%attr(0755, root, root) %caps(cap_net_raw=ep) %{_sbindir}/mysqld_exporter

%pre
getent group mysqld_exporter > /dev/null || groupadd -r mysqld_exporter
getent passwd mysqld_exporter > /dev/null || \
    useradd -Mrg mysqld_exporter -s /sbin/nologin \
            -c "MySQL Prometheus exporter" mysqld_exporter

%post
%if 0%{?rhel} != 6
%systemd_post mysqld_exporter.service
%endif

%preun
%if 0%{?rhel} != 6
%systemd_preun mysqld_exporter.service
%endif

%postun
%if 0%{?rhel} != 6
%systemd_postun mysqld_exporter.service
%endif

%changelog
* Thu Nov 21 2019 Bugzy Little <bugzylittle@gmail.com> - 0.12.1-2
- Fix systemd unit file

* Thu Nov 21 2019 Bugzy Little <bugzylittle@gmail.com> - 0.12.1-1
- Initial package

