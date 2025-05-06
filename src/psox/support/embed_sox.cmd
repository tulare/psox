@SETLOCAL

@SET "SCRIPT_DIR=%~dp0"
@ECHO %SCRIPT_DIR%
@SET "RUNTIME_DIR=%CD%\opt"

@IF EXIST %RUNTIME_DIR%\7z\7z.exe GOTO :skip7z

@ECHO -- Installation tools 7z
@RMDIR /Q /S %RUNTIME_DIR%\7z
@MD %RUNTIME_DIR%\7z
@curl --ssl-no-revoke -L https://www.7-zip.org/a/7zr.exe --output 7zr.exe
@curl --ssl-no-revoke -L https://www.7-zip.org/a/7z2301-x64.exe --output 7z2301-x64.exe
@7zr.exe x 7z2301-x64.exe -o%RUNTIME_DIR%\7z
@DEL 7zr.exe 7z2301-x64.exe

:skip7z
@ECHO -- Installation sox
@SET "SOX_VERSION=sox-14.4.2"
@SET "SOX_PACKAGE=%SOX_VERSION%-win32.zip"
@SET "SOX_ROOT=%RUNTIME_DIR%\%SOX_VERSION%"
@RMDIR /Q /S %SOX_ROOT%
@curl --ssl-no-revoke -O -J -L "https://sourceforge.net/projects/sox/files/sox/14.4.2/%SOX_PACKAGE%/download"
@%RUNTIME_DIR%\7z\7z x %SOX_PACKAGE% -o%RUNTIME_DIR%
@DEL %SOX_PACKAGE%
@COPY %SOX_ROOT%\sox.exe %SOX_ROOT%\play.exe
@COPY %SOX_ROOT%\sox.exe %SOX_ROOT%\rec.exe
@COPY %SOX_ROOT%\sox.exe %SOX_ROOT%\soxi.exe
@COPY %SCRIPT_DIR%\*.dll %SOX_ROOT%
