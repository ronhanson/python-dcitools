#!/bin/bash

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

cd ../..
confirm "Are you sure you want to remove dist, deb_dist and eggs folders?" && rm -Rf dist deb_dist *.egg-info 
