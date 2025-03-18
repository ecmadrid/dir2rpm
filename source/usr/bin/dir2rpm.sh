
#!/bin/bash

# Set up gettext for translations
export TEXTDOMAIN=dir2rpm
export TEXTDOMAINDIR=/usr/share/locale

# Check if a directory is provided
if [ -z "$1" ]; then
    echo "$(gettext "Usage"): $0 $(gettext "<directory>")" >&2
    exit 1
fi

INPUT_DIR="$1"
RPMBUILD_DIR="$HOME/rpmbuild"
DEFAULT_PACKAGE_NAME=$(basename "$INPUT_DIR" | tr -cd '[:alnum:].-' | tr '[:upper:]' '[:lower:]')
PACKAGE_NAME="$DEFAULT_PACKAGE_NAME"
VERSION=""
RELEASE="1"
SUMMARY="$(gettext "Binary package generated from directory")"
LICENSE="MIT"
ARCH="noarch"
VENDOR="xAI"
DESCRIPTION="$SUMMARY"
DEPENDS=""

# Check if the directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "$(gettext "Error: Directory") '$INPUT_DIR' $(gettext "does not exist")" >&2
    exit 1
fi

# Read metadata from metadata.txt (if exists)
METADATA_FILE="$INPUT_DIR/metadata.txt"
if [ -f "$METADATA_FILE" ]; then
    PACKAGE_NAME=$(grep -i "Name:" "$METADATA_FILE" | cut -d: -f2 | tr -d ' ')
    VERSION=$(grep -i "Version:" "$METADATA_FILE" | cut -d: -f2 | tr -d ' ')
    RELEASE=$(grep -i "Release:" "$METADATA_FILE" | cut -d: -f2 | tr -d ' ' || echo "1")
    SUMMARY=$(grep -i "Summary:" "$METADATA_FILE" | cut -d: -f2- | sed 's/^ *//')
    LICENSE=$(grep -i "License:" "$METADATA_FILE" | cut -d: -f2- | sed 's/^ *//' || echo "MIT")
    ARCH=$(grep -i "Arch:" "$METADATA_FILE" | cut -d: -f2 | tr -d ' ' || echo "noarch")
    VENDOR=$(grep -i "Vendor:" "$METADATA_FILE" | cut -d: -f2- | sed 's/^ *//' || echo "xAI")
    DESCRIPTION=$(awk '/Description:/{flag=1; next} flag{print} /^$/{flag=0}' "$METADATA_FILE" | sed 's/^  //')
    DEPENDS=$(grep -i "Depends:" "$METADATA_FILE" | cut -d: -f2- | sed 's/^ *//')
fi

# Use default values if empty
[ -z "$PACKAGE_NAME" ] && PACKAGE_NAME="$DEFAULT_PACKAGE_NAME"
[ -z "$VERSION" ] && VERSION="1.0.$(date '+%Y%m%d')"  # Generación automática de versión
[ -z "$RELEASE" ] && RELEASE="1"
[ -z "$SUMMARY" ] && SUMMARY="$(gettext "Binary package generated from directory")"
[ -z "$LICENSE" ] && LICENSE="MIT"
[ -z "$ARCH" ] && ARCH="noarch"
[ -z "$VENDOR" ] && VENDOR="xAI"
[ -z "$DESCRIPTION" ] && DESCRIPTION="$SUMMARY"

# Validate package name, version, and release
if [[ ! "$PACKAGE_NAME" =~ ^[a-zA-Z0-9_.-]+$ ]]; then
    echo "Error: Nombre de paquete inválido: $PACKAGE_NAME" >&2
    exit 1
fi
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
    echo "Error: Versión inválida: $VERSION" >&2
    exit 1
fi
if [[ ! "$RELEASE" =~ ^[0-9]+$ ]]; then
    echo "Error: Release inválido: $RELEASE" >&2
    exit 1
fi

# Create rpmbuild structure
echo "Creating rpmbuild directories..." >&2
mkdir -p "$RPMBUILD_DIR"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

# Create a temporary BUILDROOT directory
BUILDROOT="$RPMBUILD_DIR/BUILDROOT/$PACKAGE_NAME-$VERSION-$RELEASE.$ARCH"
echo "Setting up BUILDROOT: $BUILDROOT" >&2
mkdir -p "$BUILDROOT"

# Copy files to BUILDROOT, excluding metadata and scripts
echo "Copying files from $INPUT_DIR to $BUILDROOT..." >&2
rsync -av --exclude='metadata.txt' --exclude='preinst' --exclude='postinst' --exclude='preun' --exclude='postun' "$INPUT_DIR/" "$BUILDROOT/"

# Set executable permissions for files in bin directories
find "$BUILDROOT" -type f -path "*/bin/*" -exec chmod 755 {} \;

# Read scripts (if exist)
PREINST=""
POSTINST=""
PREUN=""
POSTUN=""
[ -f "$INPUT_DIR/preinst" ] && PREINST=$(cat "$INPUT_DIR/preinst")
[ -f "$INPUT_DIR/postinst" ] && POSTINST=$(cat "$INPUT_DIR/postinst")
[ -f "$INPUT_DIR/preun" ] && PREUN=$(cat "$INPUT_DIR/preun")
[ -f "$INPUT_DIR/postun" ] && POSTUN=$(cat "$INPUT_DIR/postun")

# Generate %files section
FILES_SECTION=""
if [ -n "$(ls -A "$BUILDROOT")" ]; then
    echo "Generating %files section..." >&2
    FILES_SECTION=$(find "$BUILDROOT" -type f | while read -r file; do
        rel_path="${file#$BUILDROOT}"
        if [[ "$rel_path" =~ ^/.*bin/ ]]; then
            echo "%attr(755,root,root) $rel_path"
        else
            echo "%attr(644,root,root) $rel_path"
        fi
    done)
else
    echo "Warning: BUILDROOT is empty!" >&2
fi

# Create spec file
SPEC_FILE="$RPMBUILD_DIR/SPECS/$PACKAGE_NAME.spec"
echo "Creating spec file: $SPEC_FILE" >&2
cat << EOF > "$SPEC_FILE"
Name: $PACKAGE_NAME
Version: $VERSION
Release: $RELEASE
Summary: $SUMMARY
License: $LICENSE
Vendor: $VENDOR
BuildArch: $ARCH
$( [ -n "$DEPENDS" ] && echo "Requires: $DEPENDS" )

%description
$DESCRIPTION

%prep
# No preparation needed, using binaries directly

%build
# No build step

%install
rm -rf %{buildroot}/*
mkdir -p %{buildroot}
cp -r $BUILDROOT/* %{buildroot}/

%files
$FILES_SECTION

$( [ -n "$PREINST" ] && echo "%pre" && echo "$PREINST" )
$( [ -n "$POSTINST" ] && echo "%post" && echo "$POSTINST" )
$( [ -n "$PREUN" ] && echo "%preun" && echo "$PREUN" )
$( [ -n "$POSTUN" ] && echo "%postun" && echo "$POSTUN" )

%changelog
* $(LC_TIME=C date "+%a %b %d %Y") Juan Madrid <ecmadrid@github> - $VERSION-$RELEASE
- Binary package generated automatically with GUI support
EOF

# Build RPM
echo "Running rpmbuild..." >&2
rpmbuild -bb "$SPEC_FILE" 2> rpmbuild_errors.log
RPMBUILD_EXIT=$?

if [ $RPMBUILD_EXIT -ne 0 ]; then
    echo "$(gettext "Error: Failed to create RPM")" >&2
    echo "rpmbuild errors:" >&2
    cat rpmbuild_errors.log >&2
    rm -f rpmbuild_errors.log
    exit 1
fi

# Verify RPM file
RPM_FILE="$RPMBUILD_DIR/RPMS/$ARCH/$PACKAGE_NAME-$VERSION-$RELEASE.$ARCH.rpm"
if [ -f "$RPM_FILE" ]; then
    echo "Moving RPM to current directory..." >&2
    mv "$RPM_FILE" .
    echo "$(gettext "RPM created"): $(basename "$RPM_FILE")"
else
    echo "$(gettext "Error: Failed to create RPM")" >&2
    echo "RPM file not found at: $RPM_FILE" >&2
    exit 1
fi

# Clean up
echo "Cleaning up temporary files..." >&2
if ! rm -rf "$RPMBUILD_DIR/BUILDROOT" "$RPMBUILD_DIR/BUILD" "$RPMBUILD_DIR/SPECS/$PACKAGE_NAME.spec" rpmbuild_errors.log; then
    echo "Advertencia: No se pudieron eliminar todos los archivos temporales" >&2
fi

exit 0