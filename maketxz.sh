#!/bin/sh

cd $(dirname $0)
./compile.sh
mkdir -p pkg
export DESTDIR=$PWD/pkg
./install.sh
VER=$(grep 'version =' src/liveclone.py | head -n 1 | sed "s/.*'\(.*\)'/\1/")
cd pkg
cat <<EOF > install/slack-desc
liveclone: LiveClone - A simple GUI to clone Live systems.
liveclone: 
liveclone: LiveClone simplifies the creation of a Live CD or a Live USB
liveclone: key based on SalixLive or Salix standard running environment.
liveclone: All this from the comfort of a graphical interface. 
liveclone:
liveclone:
liveclone:
liveclone:
liveclone:
liveclone:
EOF
makepkg -l y -c n ../liveclone-$VER-noarch-1plb.txz
cd ..
echo -e "python,pygtk,syslinux" > liveclone-$VER-noarch-1plb.dep
md5sum liveclone-$VER-noarch-1plb.txz > liveclone-$VER-noarch-1plb.md5
rm -rf pkg
