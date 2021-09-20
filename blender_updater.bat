@echo off

set branch=%1
set base_path=%2
if [%1] == [] set branch=master
set branches_path=./branches/
set path_end=_branch/
set full_path=%branches_path%%branch%%path_end%

cd /d %base_path%
echo CHECKOUT
call git checkout %branch%
echo UPDATE
call ./make.bat update
echo BUILD
call ./make.bat release builddir %full_path%

echo DONE
