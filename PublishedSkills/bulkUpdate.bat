@echo off
echo Be aware that this script will checkout the master of every skills, stash your changes and pull
echo latest changes before trying to reapply your changes which might fail but no rollback is available!
echo.
pause
set back=%cd%
for /d %%i in (%cd%\*) do (
	cd "%%i"
	echo current directory: %%i
	git -C %%i checkout master
	git -C %%i stash
	git -C %%i remote prune origin
	git -C %%i pull
	git -C %%i stash apply
	cd
)
echo.
echo All done!
echo.
pause
