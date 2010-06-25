#!/bin/sh

intltool-extract --type="gettext/ini" src/liveclone.desktop.in

xgettext --from-code=utf-8 \
	-L Glade \
	-o po/liveclone.pot \
	src/liveclone.glade

xgettext --from-code=utf-8 \
	-j \
	-L Python \
	-o po/liveclone.pot \
	src/liveclone.py
xgettext --from-code=utf-8 -j -L C -kN_ -o po/liveclone.pot src/liveclone.desktop.in.h

rm src/liveclone.desktop.in.h

cd po
for i in `ls *.po`; do
	msgmerge -U $i liveclone.pot
done
rm -f ./*~

