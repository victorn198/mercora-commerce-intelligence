@echo off
setlocal
set "ROOT=%~dp0"
set "HOME=%ROOT%.runtime\home"
set "USERPROFILE=%HOME%"
set "APPDATA=%ROOT%.runtime\appdata"
set "LOCALAPPDATA=%ROOT%.runtime\localappdata"
set "TEMP=%ROOT%.runtime\temp"
set "TMP=%TEMP%"
set "PIP_CACHE_DIR=%ROOT%.runtime\cache\pip"
set "SE_CACHE_PATH=%ROOT%.runtime\cache\selenium"
set "PATH=%ROOT%.runtime\tools\chromedriver-win64;%ROOT%.venv\Scripts;%PATH%"
if not exist "%TEMP%" mkdir "%TEMP%"
if not exist "%SE_CACHE_PATH%" mkdir "%SE_CACHE_PATH%"
%*
