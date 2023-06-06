@echo off

rem Grab the list of directories to scan, before we "pushd to dir containing this script",
rem so that we can have the default be "dir from which we ran this script".
setlocal
if x%CD%==x (echo Command Extensions must be enabled. && goto :eof)
set ORIGINAL_DIR=%CD%

pushd %~dp0

set DIRS_TO_CHECK=%*
if x%DIRS_TO_CHECK%==x (
    set DIRS_TO_CHECK=.
)

rem Find all the files which are both links (/al) and directories (/ad).
rem (We use "delims=" in case any paths have a space; space is a delim by default.)
rem If not, delete it (and assume something else will fix it later :-).
echo Deleting broken symlinks ...
echo.
for %%D in (%ORIGINAL_DIR%\%DIRS_TO_CHECK%) do (
    echo Checking %%D
    echo.
    pushd %%D
    if errorlevel 1 (
        echo Cannot find "%%D"
        echo.
        goto :Next_Dir
    )
    rem Clean up broken directory links.
    for /f "usebackq delims=" %%L in (`dir /adl /b`) do (
        rem Check the directory link works.
        rem Redirecting to nul just to hide "The system cannot find the file specified." message.
        pushd "%%L" >nul 2>&1
        if errorlevel 1 (
            echo Deleting broken directory symlink "%%L".
            rem First dump out some info on the link, before we delete it.
            rem I'd rather a more human-readable form, but don't know how to get that.
            fsutil reparsepoint query "%%L"
            rmdir "%%L"
            echo.
        ) else (
            popd
        )
    )
    rem Clean up broken file (non-directory) links.
    for /f "usebackq delims=" %%L in (`dir /a-dl /b`) do (
        rem Check the file link works.
        rem Redirecting to nul just to hide "The system cannot find the file specified." message.
        copy "%%L" nul >nul 2>&1
        if errorlevel 1 (
            echo Deleting broken file symlink "%%L".
            rem First dump out some info on the link, before we delete it.
            rem I'd rather a more human-readable form, but don't know how to get that.
            fsutil reparsepoint query "%%L"
            rm "%%L"
            echo.
        ) else (
            popd
        )
    )
    popd
    :Next_Dir
    rem Putting a label on the line immediately before a ')' causes a batch file parse error, hence this comment.
)
echo Deleting broken symlinks ... done.

:Finally
popd