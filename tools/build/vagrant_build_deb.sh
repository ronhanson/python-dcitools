confirm () {
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure? [y/N]} " response
    case $response in
        [yY][eE][sS]|[yY])
            true
            ;;
        *)
            false
            ;;
    esac
}


echo "This operation may take long..."

if [ $(vagrant box list | grep "trusty64" | wc -l) -ne 1 ]
then
    vagrant box add ubuntu/trusty64 --provider virtualbox
else
    echo "Trusty vagrant box already downloaded."
fi

vagrant up
vagrant provision
vagrant ssh -c "cd /vagrant/tools/build && ./build_deb.sh"
confirm "Process finished. Do you want to close the build VM?" && vagrant halt -f

cd ../..
confirm "Do you want to clean folder of temp files (dist, deb_dist, egg-info)?" && rm -Rf dist deb_dist *.egg-info

echo ""
echo "=>"
ls build/*.deb
echo ""
echo "Done."
