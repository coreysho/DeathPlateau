@echo off
REM Deletes the stale engine cache so it rebuilds from the latest content
REM (including the Regicide files pulled down from GitHub). Make sure the
REM server is NOT running before you run this.
echo This will delete the cached pack data at:
echo   C:\LostCityServer\Engine-TS\data\pack
echo Make sure the server console is closed first.
echo.
pause
REM Engine-TS, not engine. There were two checkouts of the engine repo for a
REM while and this pointed at the wrong one - the one that was never built, so
REM it had no data\pack at all. rd on a missing folder says nothing and returns,
REM which looked exactly like a successful clear.
rd /s /q "C:\LostCityServer\Engine-TS\data\pack"
echo.
echo Done. Pack folder deleted - it will rebuild automatically next time
echo you start the server (this may take a bit longer than usual on that
echo first startup).
pause
