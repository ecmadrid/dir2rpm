# dir2rpm

Create binary RPMs from directories with a PyQt5 GUI and CLI support.

## Overview

`dir2rpm` is a powerful and user-friendly tool that transforms directories into installable binary RPM packages, mirroring the functionality of `dpkg-deb --build` for Debian-based systems, but tailored for RPM-based distributions. It provides two interfaces:

- **CLI**: Use `dir2rpm.sh` for a lightweight, terminal-based workflow.
- **GUI**: Enjoy a modern, PyQt5-powered interface with `dir2rpm_gui.py` for a graphical experience.

### Key Features
- Convert any directory structure into a binary RPM.
- Customize metadata via an optional `metadata.txt` file.
- Include maintenance scripts (`preinst`, `postinst`, `preun`, `postun`).
- Multi-language support (English and Spanish) with a `.desktop` file for menu integration.

Developed with ❤️ on Fedora, `dir2rpm` is compatible with any RPM-based Linux distribution.

## Requirements

- **Operating System**: Tested on Fedora 41; works on any RPM-based distro.
- **Dependencies**:
  - `bash`
  - `rpm-build`
  - `python3`
  - `python3-qt5`

Install dependencies on Fedora with:
```bash
sudo dnf install bash rpm-build python3 python3-qt5
```

## Installation

1. Clone or download the repository:
   ```bash
   git clone https://github.com/ecmadrid/dir2rpm.git
   cd dir2rpm
   ```
2. Build and install the RPM:
   ```bash
   ./dir2rpm.sh dir2rpm
   sudo rpm -Uvh dir2rpm-1.0-1.noarch.rpm
   ```

## Usage

- **CLI**:
  ```bash
  /usr/bin/dir2rpm.sh <directory>
  ```
- **GUI**:
  ```bash
  /usr/bin/dir2rpm_gui.py
  ```

## Authors
- Juan Sánchez `<contact@xanmian.com>`
- xAI
