@echo off

set branch=%1
IF [%1] == [] set branch=main
set base_path=%2
set diff_path=%3
set branches_path=./branches/
set full_path=%branches_path%/%branch%_branch/

cd /d %base_path%
echo CHECKOUT
call git checkout %branch%
call git stash
echo UPDATE
call ./make.bat update
IF NOT [%3] == [] (
	echo APPLY DIFF
	call git apply %diff_path%
)
echo BUILD
echo %full_path%
call ./make.bat ninja release builddir %full_path% nobuild
cd %full_path%
ninja

echo DONE
