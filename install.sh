#!/bin/sh

cd $(dirname $0)

install -d -m 755 $DESTDIR/usr/doc/liveclone-$VER
install -d -m 755 $DESTDIR/install
install -d -m 755 $DESTDIR/usr/sbin
install -d -m 755 $DESTDIR/usr/share/applications
install -d -m 755 $DESTDIR/usr/share/icons/hicolor/24x24/apps
install -d -m 755 $DESTDIR/usr/share/icons/hicolor/64x64/apps
install -d -m 755 $DESTDIR/usr/share/icons/hicolor/128x128/apps
install -d -m 755 $DESTDIR/usr/share/icons/hicolor/scalable/apps
install -d -m 755 $DESTDIR/usr/share/liveclone/liveskel/boot/syslinux
install -d -m 755 $DESTDIR/usr/share/liveclone/liveskel/boot/isolinux
install -d -m 755 $DESTDIR/usr/share/liveclone/liveskel/salixlive
install -d -m 755 $DESTDIR/usr/share/liveclone/stockskel/boot
install -d -m 755 $DESTDIR/usr/share/liveclone/stockskel/etc/rc.d

install -m 755 src/liveclone.py $DESTDIR/usr/sbin/liveclone.py
install -m 644 src/liveclone.glade \
$DESTDIR/usr/share/liveclone
install -m 644 src/liveclone.desktop \
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
install -m 644 liveskel/boot/syslinux/syslinux.cfg \
$DESTDIR/usr/share/liveclone/liveskel/boot/syslinux/
install -m 644 liveskel/boot/isolinux/isolinux.cfg \
$DESTDIR/usr/share/liveclone/liveskel/boot/isolinux/
install -m 644 liveskel/boot/isolinux/isolinux.bin \
$DESTDIR/usr/share/liveclone/liveskel/boot/isolinux/
install -m 644 liveskel/boot/vesamenu.c32 \
$DESTDIR/usr/share/liveclone/liveskel/boot/
install -m 644 liveskel/salixlive/livecd.sgn \
$DESTDIR/usr/share/liveclone/liveskel/salixlive/
install -m 644 liveskel/salixlive/make_iso.sh \
$DESTDIR/usr/share/liveclone/liveskel/salixlive/
install -m 644 stockskel/boot/README.initrd \
$DESTDIR/usr/share/liveclone/stockskel/boot/
install -m 644 stockskel/boot/salix.bmp \
$DESTDIR/usr/share/liveclone/stockskel/boot/
install -m 755 stockskel/etc/rc.d/rc.6 \
$DESTDIR/usr/share/liveclone/stockskel/etc/rc.d/
install -m 755 stockskel/etc/rc.d/rc.M \
$DESTDIR/usr/share/liveclone/stockskel/etc/rc.d/
install -m 755 stockskel/etc/rc.d/rc.S \
$DESTDIR/usr/share/liveclone/stockskel/etc/rc.d/
install -m 755 stockskel/etc/rc.d/rc.alsa \
$DESTDIR/usr/share/liveclone/stockskel/etc/rc.d/
install -m 755 stockskel/etc/rc.d/rc.services \
$DESTDIR/usr/share/liveclone/stockskel/etc/rc.d/

for i in `ls po/*.mo|sed "s|po/\(.*\).mo|\1|"`; do
	install -d -m 755 $DESTDIR/usr/share/locale/${i}/LC_MESSAGES
	install -m 644 po/${i}.mo \
	$DESTDIR/usr/share/locale/${i}/LC_MESSAGES/liveclone.mo
done

for i in `ls docs`; do
	install -m 644 docs/${i} \
	$DESTDIR/usr/doc/liveclone-$VER/
done
