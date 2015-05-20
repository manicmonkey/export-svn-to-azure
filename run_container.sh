#!/usr/bin/env bash
set -e
docker build -t manicmonkey/svn-blob-upload .
docker run -it --rm --add-host=svn:192.168.1.10 manicmonkey/svn-blob-upload \
    --svn_url=http://svn/stuff_to_export/ \
    --svn_username=user \
    --svn_password=pass \
    --azure_acc_name=accname \
    --azure_acc_key=t7r84urhru43hfeporifh3332/regfrthge/rfew== \
    --azure_container_name=svn-exports