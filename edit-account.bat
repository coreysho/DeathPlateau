@echo off
setlocal enabledelayedexpansion
REM ============================================================
REM  Edit a player's account on the live server, from any PC.
REM
REM  It does not need the repo, Node, or a checkout on this
REM  machine - it opens an ssh session to the server and runs
REM  engine/tools/server/account.ts there. All you need is the
REM  OpenSSH client, which Windows 10 and 11 already have.
REM
REM  First run asks for the server address and saves it next to
REM  this file in edit-account.cfg (which is gitignored - it is
REM  yours, not the repo's).
REM
REM  A player who is LOGGED IN cannot be edited: the server holds
REM  their character in memory and writes it over your change at
REM  logout. Log them out first. The tool refuses rather than
REM  letting you lose the edit.
REM ============================================================

set "CFG=%~dp0edit-account.cfg"

if not exist "%CFG%" goto firstrun
for /f "usebackq tokens=1,* delims==" %%A in ("%CFG%") do set "%%A=%%B"
goto connected

:firstrun
echo.
echo ==================================================
echo  First run - where is the server?
echo ==================================================
echo.
echo  Host: the LXC's address, e.g. 192.168.1.50 or lostcity.local
set /p SSH_HOST=  Host: 
echo.
echo  User: the account you ssh in as, usually root
set /p SSH_USER=  User [root]: 
if "!SSH_USER!"=="" set "SSH_USER=root"
echo.
echo  Port: leave blank for the normal 22
set /p SSH_PORT=  Port [22]: 
if "!SSH_PORT!"=="" set "SSH_PORT=22"
echo.
echo  Engine folder on the server
set /p ENGINE_DIR=  Path [/opt/lostcity/engine]: 
if "!ENGINE_DIR!"=="" set "ENGINE_DIR=/opt/lostcity/engine"
(
  echo SSH_HOST=!SSH_HOST!
  echo SSH_USER=!SSH_USER!
  echo SSH_PORT=!SSH_PORT!
  echo ENGINE_DIR=!ENGINE_DIR!
) > "%CFG%"
echo.
echo  Saved to edit-account.cfg - delete that file to be asked again.
echo.
echo  TIP: every command below opens its own ssh session, so without a key
echo  you will be asked for the password each time - and Debian refuses root
echo  password logins outright, so it may not let you in at all. Set up a key:
echo.
echo    1. In PowerShell on this PC:
echo         ssh-keygen -t ed25519            (Enter through every question)
echo         Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub ^| Set-Clipboard
echo.
echo    2. In the server's own console (Proxmox: the container, then Console):
echo         mkdir -p ~/.ssh
echo         echo "PASTE" ^> ~/.ssh/authorized_keys
echo         chmod 700 ~/.ssh
echo         chmod 600 ~/.ssh/authorized_keys
echo.
echo  It goes in through the console because ssh cannot be used to install
echo  the key that ssh needs before it will let you in.
echo.
pause

:connected
set "SSH=ssh -p %SSH_PORT% %SSH_USER%@%SSH_HOST%"
set "TOOL=cd %ENGINE_DIR% && npx tsx tools/server/account.ts"

:menu
cls
echo ==================================================
echo   Account editor - %SSH_USER%@%SSH_HOST%
echo ==================================================
echo.
echo   1  List every player
echo   2  Show a player (stats, items, bank, account)
echo.
echo   3  Set one stat
echo   4  Max every stat
echo   5  Give an item
echo   6  Move them somewhere
echo.
echo   7  Members on / off
echo   8  Staff mod level
echo   9  Ban / unban
echo  10  Mute / unmute
echo  11  Change password
echo.
echo  12  Download a player to a file on this PC
echo  13  Upload a file back to the server
echo.
echo  14  Type a command yourself
echo   0  Quit
echo.
set "CHOICE="
set /p CHOICE=  Choose: 

if "%CHOICE%"=="0" exit /b 0
if "%CHOICE%"=="1" goto do_list
if "%CHOICE%"=="2" goto do_show
if "%CHOICE%"=="3" goto do_stat
if "%CHOICE%"=="4" goto do_maxstats
if "%CHOICE%"=="5" goto do_give
if "%CHOICE%"=="6" goto do_move
if "%CHOICE%"=="7" goto do_members
if "%CHOICE%"=="8" goto do_modlevel
if "%CHOICE%"=="9" goto do_ban
if "%CHOICE%"=="10" goto do_mute
if "%CHOICE%"=="11" goto do_password
if "%CHOICE%"=="12" goto do_download
if "%CHOICE%"=="13" goto do_upload
if "%CHOICE%"=="14" goto do_raw
goto menu

:askname
set "PLAYER="
set /p PLAYER=  Player name: 
if "%PLAYER%"=="" goto menu
exit /b 0

:do_list
echo.
%SSH% "%TOOL% list"
goto done

:do_show
call :askname
if "%PLAYER%"=="" goto menu
echo.
%SSH% "%TOOL% show %PLAYER%"
goto done

:do_stat
call :askname
if "%PLAYER%"=="" goto menu
echo.
echo   attack defence strength hitpoints ranged prayer magic cooking
echo   woodcutting fletching fishing firemaking crafting smithing mining
echo   herblore agility thieving slayer farming runecraft construction
echo.
set /p SKILL=  Which skill: 
set /p LEVEL=  Level (1-99): 
if "%SKILL%"=="" goto menu
if "%LEVEL%"=="" goto menu
echo.
%SSH% "%TOOL% set %PLAYER% save.stats.%SKILL% %LEVEL%"
goto done

:do_maxstats
call :askname
if "%PLAYER%"=="" goto menu
echo.
echo  This sets EVERY skill on %PLAYER% to 99.
pause
echo.
%SSH% "%TOOL% set %PLAYER% 'save.stats.*' 99"
goto done

:do_give
call :askname
if "%PLAYER%"=="" goto menu
echo.
echo  Item name as the content uses it, e.g. abyssal_whip, coins,
echo  dragon_scimitar, platinum_token. Not the name shown in game.
set /p ITEM=  Item: 
set /p QTY=  How many [1]: 
if "%QTY%"=="" set "QTY=1"
set /p WHERE=  Into inv or bank [inv]: 
if "%WHERE%"=="" set "WHERE=inv"
if "%ITEM%"=="" goto menu
echo.
%SSH% "%TOOL% give %PLAYER% %ITEM% %QTY% --inv %WHERE%"
goto done

:do_move
call :askname
if "%PLAYER%"=="" goto menu
echo.
echo  Lumbridge is 3222, 3218, plane 0.
set /p PX=  X: 
set /p PZ=  Z: 
set /p PL=  Plane [0]: 
if "%PL%"=="" set "PL=0"
if "%PX%"=="" goto menu
if "%PZ%"=="" goto menu
echo.
%SSH% "%TOOL% set %PLAYER% save.position.x %PX%"
%SSH% "%TOOL% set %PLAYER% save.position.z %PZ%"
%SSH% "%TOOL% set %PLAYER% save.position.level %PL%"
goto done

:do_members
call :askname
if "%PLAYER%"=="" goto menu
set /p ONOFF=  Members - true or false: 
if "%ONOFF%"=="" goto menu
echo.
%SSH% "%TOOL% set %PLAYER% account.members %ONOFF%"
goto done

:do_modlevel
call :askname
if "%PLAYER%"=="" goto menu
echo.
echo  0 = ordinary player. Higher numbers are staff.
set /p LVL=  Level: 
if "%LVL%"=="" goto menu
echo.
%SSH% "%TOOL% set %PLAYER% account.staffmodlevel %LVL%"
goto done

:do_ban
call :askname
if "%PLAYER%"=="" goto menu
echo.
echo  A date to ban until, e.g. 2027-01-01T00:00:00.000Z
echo  Type  null  to lift a ban.
set /p WHEN=  Banned until: 
if "%WHEN%"=="" goto menu
echo.
%SSH% "%TOOL% set %PLAYER% account.banned_until %WHEN%"
goto done

:do_mute
call :askname
if "%PLAYER%"=="" goto menu
echo.
echo  A date to mute until, e.g. 2027-01-01T00:00:00.000Z
echo  Type  null  to lift a mute.
set /p WHEN=  Muted until: 
if "%WHEN%"=="" goto menu
echo.
%SSH% "%TOOL% set %PLAYER% account.muted_until %WHEN%"
goto done

:do_password
call :askname
if "%PLAYER%"=="" goto menu
echo.
set /p PW=  New password: 
if "%PW%"=="" goto menu
echo.
%SSH% "%TOOL% password %PLAYER% %PW%"
goto done

:do_download
call :askname
if "%PLAYER%"=="" goto menu
set "OUTFILE=%~dp0%PLAYER%.json"
echo.
echo  Saving to %OUTFILE%
REM The tool prints the JSON when it is not given --out, so this is the whole
REM transfer - no copy of the account is left behind on the server.
%SSH% "%TOOL% export %PLAYER%" > "%OUTFILE%"
if errorlevel 1 (
  REM A half-written file is worse than none: 13 would upload it without complaint.
  del "%OUTFILE%" 2>nul
  echo  FAILED - nothing was saved.
) else (
  echo  Done. Open it in Notepad, change what you like, then use 13 to send it back.
)
goto done

:do_upload
call :askname
if "%PLAYER%"=="" goto menu
set "INFILE=%~dp0%PLAYER%.json"
if not exist "%INFILE%" (
  echo.
  echo  There is no %INFILE% - use 12 to download them first.
  goto done
)
echo.
echo  Sending %INFILE%
REM Piped into the tool's stdin rather than scp'd, so the file never lands on
REM the server's disk. The server backs the old save up before it writes.
type "%INFILE%" | %SSH% "%TOOL% import %PLAYER% --in -"
goto done

:do_raw
echo.
echo  Everything after the tool name, e.g.
echo    show corey
echo    set corey save.runenergy 10000
echo.
set "RAW="
set /p RAW=  account.ts 
if "%RAW%"=="" goto menu
echo.
%SSH% "%TOOL% %RAW%"
goto done

:done
echo.
pause
goto menu
