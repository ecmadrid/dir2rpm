#!/bin/bash

# dir2rpm: Creates a binary RPM from a directory
# Usage: dir2rpm <directory>

# Check if a directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>" >&2
    exit 1
fi

INPUT_DIR="$1"
RPMBUILD_DIR="$HOME/rpmbuild"
PACKAGE_NAME="mypackage"
VERSION="1.0"
RELEASE="1"
SUMMARY="Binary package generated from directory"
LICENSE="MIT"
ARCH="noarch"
DESCRIPTION="$SUMMARY"
DEPENDS=""

# Check if the directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Directory '$INPUT_DIR' does not exist" >&2
    exit 1
fi

# Create rpmbuild structure if it doesn't exist
mkdir -p "$RPMBUILD_DIR"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

# Read metadata from metadata.txt (if exists)
METADATA_FILE="$INPUT_DIR/metadata.txt"
if [ -f "$METADATA_FILE" ]; then
    PACKAGE_NAME=$(grep -i "Name:" "$METADATA_FILE" | cut -d: -f2 | tr -d ' ')
    VERSION=$(grep -i "Version:" "$METADATA_FILE" | cut -d: -f2 | tr -d ' ')
    RELEASE=$(grep -i "Release:" "$METADATA_FILE" | cut -d: -f2 | tr -d ' ' || echo "1")
    SUMMARY=$(grep -i "Summary:" "$METADATA_FILE" | cut -d: -f2- | sed 's/^ *//')
    LICENSE=$(grep -i "License:" "$METADATA_FILE" | cut -d: -f2- | sed 's/^ *//' || echo "MIT")
    ARCH=$(grep -i "Arch:" "$METADATA_FILE" | cut -d: -f2 | tr -d ' ' || echo "noarch")
    DESCRIPTION=$(awk '/Description:/{flag=1; next} flag{print} /^$/{flag=0}' "$METADATA_FILE" | sed 's/^  //')
    DEPENDS=$(grep -i "Depends:" "$METADATA_FILE" | cut -d: -f2- | sed 's/^ *//')
fi

# Use default values if empty
[ -z "$PACKAGE_NAME" ] && PACKAGE_NAME="mypackage"
[ -z "$VERSION" ] && VERSION="1.0"
[ -z "$RELEASE" ] && RELEASE="1"
[ -z "$SUMMARY" ] && SUMMARY="Binary package generated from directory"
[ -z "$LICENSE" ] && LICENSE="MIT"
[ -z "$ARCH" ] && ARCH="noarch"
[ -z "$DESCRIPTION" ] && DESCRIPTION="$SUMMARY"

# Create a temporary BUILDROOT directory
BUILDROOT="$RPMBUILD_DIR/BUILDROOT/$PACKAGE_NAME-$VERSION-$RELEASE.$ARCH"
mkdir -p "$BUILDROOT"

# Copy all files from input directory to BUILDROOT
cp -r "$INPUT_DIR"/* "$BUILDROOT"/
# Exclude metadata.txt and maintenance scripts if they exist
for file in metadata.txt preinst postinst preun postun; do
    [ -f "$BUILDROOT/$file" ] && rm "$BUILDROOT/$file"
done

# Ensure executable permissions for binaries
find "$BUILDROOT" -type f -path "*/bin/*" -exec chmod 755 {} \;

# Detect maintenance scripts
PREINST=""
POSTINST=""
PREUN=""
POSTUN=""
[ -f "$INPUT_DIR/preinst" ] && PREINST=$(cat "$INPUT_DIR/preinst")
[ -f "$INPUT_DIR/postinst" ] && POSTINST=$(cat "$INPUT_DIR/postinst")
[ -f "$INPUT_DIR/preun" ] && PREUN=$(cat "$INPUT_DIR/preun")
[ -f "$INPUT_DIR/postun" ] && POSTUN=$(cat "$INPUT_DIR/postun")

# Generate %files section dynamically with specific permissions
FILES_SECTION=""
if [ -n "$(ls -A "$BUILDROOT")" ]; then
    FILES_SECTION=$(find "$BUILDROOT" -type f | while read -r file; do
        rel_path="${file#$BUILDROOT}"
        if [[ "$rel_path" =~ ^/.*bin/ ]]; then
            echo "%attr(755,root,root) $rel_path"
        else
            echo "%attr(644,root,root) $rel_path"
        fi
    done)
fi

# Create the .spec file
SPEC_FILE="$RPMBUILD_DIR/SPECS/$PACKAGE_NAME.spec"
cat << EOF > "$SPEC_FILE"
Name: $PACKAGE_NAME
Version: $VERSION
Release: $RELEASE
Summary: $SUMMARY
License: $LICENSE
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

# Build the RPM
rpmbuild -bb "$SPEC_FILE"

# Move the generated RPM to the current directory
RPM_FILE="$RPMBUILD_DIR/RPMS/$ARCH/$PACKAGE_NAME-$VERSION-$RELEASE.$ARCH.rpm"
if [ -f "$RPM_FILE" ]; then
    mv "$RPM_FILE" .
    echo "RPM created: $(basename "$RPM_FILE")"
else
    echo "Error: Failed to create RPM" >&2
    exit 1
fi

# Cleanup
rm -rf "$RPMBUILD_DIR/BUILDROOT" "$RPMBUILD_DIR/BUILD" "$RPMBUILD_DIR/SPECS/$PACKAGE_NAME.spec"

exit 0
