#!/usr/bin/env bash
list=$(find . -name 'update.sample')
for item in $list; do
	ln -sr post-receive $(dirname $item)/post-receive;
done;
