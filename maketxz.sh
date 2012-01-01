#!/bin/sh

cd $(dirname $0)
./compile.sh
mkdir -p pkg
export DESTDIR=$PWD/pkg
./install.sh
VER=$(grep 'version =' src/liveclone.py | head -n 1 | sed "s/.*'\(.*\)'/\1/")
RLZ=1plb
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
makepkg -l y -c n ../liveclone-$VER-noarch-$RLZ.txz
cd ..
echo -e "python,pygtk,syslinux" > liveclone-$VER-noarch-$RLZ.dep
md5sum liveclone-$VER-noarch-$RLZ.txz > liveclone-$VER-noarch-$RLZ.md5
echo 'cdrtools,coreutils,dosfstools,grep,grub2,parted,python,pygtk,sed,squashfs-tools,syslinux,sysvinit,tar,xfsprogs,xz' > liveclone-$VER-noarch-$RLZ.dep
rm -rf pkg
