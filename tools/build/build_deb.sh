#!/bin/bash
cd ../..
echo "Packaging Python .tar.gz package."
echo ""
python3 setup.py sdist #--dist-dir /tmp/python-dist
cp debian.cfg stdeb.cfg
mv stdeb.cfg *.egg-info/
echo ""
echo "Python package complete. Packaging .DEB now..."
echo ""
#py2dsc-deb `ls -1 dist/*.tar.gz | tail -n1`
python3 setup.py --command-packages=stdeb.command sdist_dsc --with-python2=True --with-python3=True --dist-dir=deb_dist --extra-cfg-file=debian.cfg --use-premade-distfile=`ls -1 dist/*.tar.gz | tail -n1` bdist_deb 
echo ""
echo ".DEB creation completed"
echo ""
[ -d build ] || mkdir build
mv `ls deb_dist/*.deb` ./build/
echo "   .deb moved into 'build' folder : "
ls build/*.deb
echo ""
cd tools/build/
source ./clean_deb.sh
