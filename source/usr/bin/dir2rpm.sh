#!/bin/bash

# dir2rpm: Crea un RPM binario desde un directorio
# Uso: dir2rpm <directorio>

# Verifica que se pase un directorio
if [ -z "$1" ]; then
    echo "Uso: $0 <directorio>"
    exit 1
fi

INPUT_DIR="$1"
RPMBUILD_DIR="$HOME/rpmbuild"
PACKAGE_NAME="mypackage"
VERSION="1.0"
RELEASE="1"
SUMMARY="Paquete binario generado desde directorio"
LICENSE="MIT"
ARCH="noarch"
DESCRIPTION="$SUMMARY"
DEPENDS=""

# Verifica que el directorio exista
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: El directorio '$INPUT_DIR' no existe"
    exit 1
fi

# Crea la estructura de rpmbuild si no existe
mkdir -p "$RPMBUILD_DIR"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

# Lee metadatos desde metadata.txt (si existe)
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

# Usa valores por defecto si están vacíos
[ -z "$PACKAGE_NAME" ] && PACKAGE_NAME="mypackage"
[ -z "$VERSION" ] && VERSION="1.0"
[ -z "$RELEASE" ] && RELEASE="1"
[ -z "$SUMMARY" ] && SUMMARY="Paquete binario generado desde directorio"
[ -z "$LICENSE" ] && LICENSE="MIT"
[ -z "$ARCH" ] && ARCH="noarch"
[ -z "$DESCRIPTION" ] && DESCRIPTION="$SUMMARY"

# Crea un directorio temporal para BUILDROOT
BUILDROOT="$RPMBUILD_DIR/BUILDROOT/$PACKAGE_NAME-$VERSION-$RELEASE.$ARCH"
mkdir -p "$BUILDROOT"

# Copia todos los archivos del directorio de entrada a BUILDROOT
cp -r "$INPUT_DIR"/* "$BUILDROOT"/
# Excluye metadata.txt y scripts de mantenimiento si existen
for file in metadata.txt preinst postinst preun postun; do
    [ -f "$BUILDROOT/$file" ] && rm "$BUILDROOT/$file"
done

# Asegura permisos ejecutables en archivos binarios
find "$BUILDROOT" -type f -path "*/bin/*" -exec chmod 755 {} \;

# Detecta scripts de mantenimiento
PREINST=""
POSTINST=""
PREUN=""
POSTUN=""
[ -f "$INPUT_DIR/preinst" ] && PREINST=$(cat "$INPUT_DIR/preinst")
[ -f "$INPUT_DIR/postinst" ] && POSTINST=$(cat "$INPUT_DIR/postinst")
[ -f "$INPUT_DIR/preun" ] && PREUN=$(cat "$INPUT_DIR/preun")
[ -f "$INPUT_DIR/postun" ] && POSTUN=$(cat "$INPUT_DIR/postun")

# Genera la sección %files dinámicamente con permisos específicos
FILES_SECTION=""
if [ -n "$(ls -A "$BUILDROOT")" ]; then
    # Usar find con una sola pasada y aplicar permisos condicionalmente
    FILES_SECTION=$(find "$BUILDROOT" -type f | while read -r file; do
        rel_path="${file#$BUILDROOT}"
        if [[ "$rel_path" =~ ^/.*bin/ ]]; then
            echo "%attr(755,root,root) $rel_path"
        else
            echo "%attr(644,root,root) $rel_path"
        fi
    done)
fi

# Crea el archivo .spec
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
# No hay preparación, usamos binarios directamente

%build
# No hay compilación

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
* $(LC_TIME=C date "+%a %b %d %Y") Grok 3 <grok@xai.com> - $VERSION-$RELEASE
- Paquete binario generado automáticamente con GUI
EOF

# Construye el RPM
rpmbuild -bb "$SPEC_FILE"

# Mueve el RPM generado al directorio actual
RPM_FILE="$RPMBUILD_DIR/RPMS/$ARCH/$PACKAGE_NAME-$VERSION-$RELEASE.$ARCH.rpm"
if [ -f "$RPM_FILE" ]; then
    mv "$RPM_FILE" .
    echo "RPM creado: $(basename "$RPM_FILE")"
else
    echo "Error al crear el RPM"
    exit 1
fi

# Limpia
rm -rf "$RPMBUILD_DIR/BUILDROOT" "$RPMBUILD_DIR/BUILD" "$RPMBUILD_DIR/SPECS/$PACKAGE_NAME.spec"

exit 0
