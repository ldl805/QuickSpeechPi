#!/bin/bash
# Script to build a Debian package for QuickSpeechPi

APP_NAME="quickspeechpi"
VERSION="1.1"
PKG_DIR="${APP_NAME}_${VERSION}_all"

echo "Building Debian package $PKG_DIR..."

# Create structure
mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/usr/bin"
mkdir -p "$PKG_DIR/usr/share/$APP_NAME"
mkdir -p "$PKG_DIR/usr/share/applications"

# Create control file
cat <<EOF > "$PKG_DIR/DEBIAN/control"
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-tk, espeak
Maintainer: ldl805 <ldl805@github.com>
Description: Quick Speech Pi
 Quick Speech Pi is a simple text-to-speech GUI designed for the Raspberry Pi.
 It uses espeak to convert text into speech with adjustable pitch and speed.
EOF

# Create wrapper
cat <<EOF > "$PKG_DIR/usr/bin/$APP_NAME"
#!/bin/bash
python3 /usr/share/$APP_NAME/tts_gui.py "\$@"
EOF
chmod 755 "$PKG_DIR/usr/bin/$APP_NAME"

# Copy application files
cp tts_gui.py "$PKG_DIR/usr/share/$APP_NAME/"
cp tts_gui.desktop "$PKG_DIR/usr/share/applications/$APP_NAME.desktop"

# Build package
dpkg-deb --build --root-owner-group "$PKG_DIR"

echo "Package built: ${PKG_DIR}.deb"
