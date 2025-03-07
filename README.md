# dir2rpm

Create binary RPMs from directories with a PyQt5 GUI and CLI support.

## Overview

`dir2rpm` is a versatile tool designed to package directories into binary RPMs, similar to `dpkg-deb --build` for Debian-based systems. It offers two interfaces:
- **CLI**: A shell script (`dir2rpm.sh`) for terminal users.
- **GUI**: A modern PyQt5-based interface (`dir2rpm_gui.py`) for a graphical experience.

Key features:
- Generate RPMs from any directory structure.
- Optional metadata configuration via `metadata.txt`.
- Support for maintenance scripts (`preinst`, `postinst`, `preun`, `postun`).
- Multi-language menu integration with a `.desktop` file.

Developed with ❤️ on Fedora, but compatible with any RPM-based distribution.

## Requirements

- **Operating System**: Fedora (tested on Fedora 41) or any RPM-based Linux distro.
- **Dependencies**:
  - `bash`
  - `rpm-build`
  - `python3`
  - `python3-qt5`

Install them on Fedora with:
```bash
sudo dnf install bash rpm-build python3 python3-qt5
