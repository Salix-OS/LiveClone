#!/bin/sh

cd $(dirname $0)
VER=$(grep 'version =' src/liveclone.py | head -n 1 | sed "s/.*'\(.*\)'/\1/")

install -d -m 755 $DESTDIR/usr/doc/liveclone-$VER
install -d -m 755 $DESTDIR/install
install -d -m 755 $DESTDIR/usr/sbin
install -d -m 755 $DESTDIR/usr/share/applications
install -d -m 755 $DESTDIR/usr/share/icons/hicolor/24x24/apps
install -d -m 755 $DESTDIR/usr/share/icons/hicolor/64x64/apps
install -d -m 755 $DESTDIR/usr/share/icons/hicolor/128x128/apps
install -d -m 755 $DESTDIR/usr/share/icons/hicolor/scalable/apps
install -d -m 755 $DESTDIR/usr/share/liveclone

install -m 755 src/liveclone.py \
$DESTDIR/usr/sbin/
install -m 644 src/liveclone.glade \
$DESTDIR/usr/share/liveclone
install -m 644 src/liveclone.desktop \
$DESTDIR/usr/share/applications/
install -m 644 src/liveclone-kde.desktop \
$DESTDIR/usr/share/applications/
install -m 644 src/liveclone.png \
$DESTDIR/usr/share/liveclone/
install -m 644 icons/liveclone-24.png \
$DESTDIR/usr/share/icons/hicolor/24x24/apps/liveclone.png
install -m 644 icons/liveclone-64.png \
$DESTDIR/usr/share/icons/hicolor/64x64/apps/liveclone.png
install -m 644 icons/liveclone-128.png \
$DESTDIR/usr/share/icons/hicolor/128x128/apps/liveclone.png
install -m 644 icons/liveclone.svg \
$DESTDIR/usr/share/icons/hicolor/scalable/apps/

for i in `ls po/*.mo|sed "s|po/\(.*\).mo|\1|"`; do
	install -d -m 755 $DESTDIR/usr/share/locale/${i}/LC_MESSAGES
	install -m 644 po/${i}.mo \
	$DESTDIR/usr/share/locale/${i}/LC_MESSAGES/liveclone.mo
done

for i in `ls docs`; do
	install -m 644 docs/${i} \
	$DESTDIR/usr/doc/liveclone-$VER/
done
