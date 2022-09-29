@echo off

set lib_path=%1
set base_path=%2

cd /d %lib_path%
echo CLEANUP
call svn cleanup
echo UPDATE
call svn update
cd /d %base_path%
echo PULL
call git stash
call git pull

echo CLEAN UP DONE
