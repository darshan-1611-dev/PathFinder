@echo off

setlocal

:start


:: Prompt the user for the commit message
set /p commit_message="Enter commit message: "

:: Check if the user entered a commit message
if "%commit_message%"=="" (
  echo Commit message cannot be empty.
  goto :eof
)

:: Add all changes
git add .

:: Commit the changes with the specified message
git commit -m "%commit_message%"

:: Push the changes to the remote repository
git push origin master

:: Display success message
echo Changes committed and pushed successfully.

pause


endlocal