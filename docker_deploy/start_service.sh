#!/usr/bin/env bash

/usr/sbin/nginx

systemctl daemon-reload
systemctl start ip2w.service

/usr/bin/pytest -v -s /root/app/tests/
if [[ $? -eq 0 ]]
then
    echo "Tests completed successfully"
    exit 0
else
    echo "Tests completed with errors"
    exit 1
fi
