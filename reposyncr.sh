#!/usr/bin/env bash

repo_list="
/home/share/android
"

if [[ $EUID -ne 0 ]]; then
    echo "This script should be run as root"
    exit 1
fi

for repo in ${repo_list}; do
    var=$(ps aux | grep "[p]ython ${repo}/reposyncc.py")
    if [[ -n $var ]]; then
        continue
    fi
    user=$(stat ${repo} -c "%U")
    su ${user} -c "(${repo}/reposyncc.py >> ${repo}/reposync.log 2>&1 &)"
done

