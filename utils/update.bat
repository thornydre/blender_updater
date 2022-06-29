@echo off

set branch=%1
if [%1] == [] set branch=master
set base_path=%2
set branches_path=./branches/
set full_path=%branches_path%/%branch%_branch/

cd /d %base_path%
echo CHECKOUT
call git checkout %branch%
if [%3] == [] (
	echo APPLY DIFF
	set diff_path = %3
	call git apply %diff_path%
)
echo UPDATE
call ./make.bat update
echo BUILD
echo %full_path%
call ./make.bat release builddir %full_path%

echo DONE
