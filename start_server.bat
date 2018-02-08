@echo off
set curpath=%~dp0

cd ..
set KBE_ROOT=%cd%
set KBE_RES_PATH=%KBE_ROOT%/kbe/res/;%curpath%/;%curpath%/scripts/;%curpath%/res/
set KBE_BIN_PATH=%KBE_ROOT%/kbe/bin/server/

if defined uid (echo UID = %uid%) else set uid=%random%%%32760+1

cd %curpath%
taskkill /f /t /im baseappmgr.exe > nul 2> nul 
taskkill /f /t /im cellappmgr.exe > nul 2> nul 
taskkill /f /t /im baseapp.exe > nul 2> nul 
taskkill /f /t /im cellapp.exe > nul 2> nul 
taskkill /f /t /im loginapp.exe > nul 2> nul 

echo KBE_ROOT = %KBE_ROOT%
echo KBE_RES_PATH = %KBE_RES_PATH%
echo KBE_BIN_PATH = %KBE_BIN_PATH%

start %KBE_BIN_PATH%/baseappmgr.exe --cid=5000 --gus=5 --hide=1
start %KBE_BIN_PATH%/cellappmgr.exe --cid=6000 --gus=6 --hide=1

start %KBE_BIN_PATH%/baseapp.exe --cid=7001 --gus=7 --hide=1
@rem start %KBE_BIN_PATH%/baseapp.exe --cid=7002 --gus=8 --hide=1
start %KBE_BIN_PATH%/cellapp.exe --cid=8001 --gus=9 --hide=1
@rem start %KBE_BIN_PATH%/cellapp.exe --cid=8002  --gus=10 --hide=1

start %KBE_BIN_PATH%/loginapp.exe --cid=9000 --gus=11 --hide=1
