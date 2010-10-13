#!/bin/sh

cd $(dirname $0)
for i in `ls po/*.po`;do
	echo "Compiling `echo $i|sed "s|po/||"`"
	msgfmt $i -o `echo $i |sed "s/.po//"`.mo
done
intltool-merge po/ -d -u src/liveclone.desktop.in src/liveclone.desktop
intltool-merge po/ -d -u src/liveclone-kde.desktop.in src/liveclone-kde.desktop
