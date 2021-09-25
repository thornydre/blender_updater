#!/bin/sh
BRANCH=$1
BASE_PATH=$2
FULL_PATH=$3/$1

cd ${BASE_PATH}
echo CHECKOUT
git checkout ${BRANCH}
echo UPDATE
make update
echo BUILD
make release BUILD_DIR=${FULL_PATH}

echo DONE
