@echo off
cd /d "%~dp0"
echo ===================================================
echo   Subiendo FruityFocus a GitHub (LuisNafate/FruityFocus)
echo ===================================================
echo.
git push -u origin main
echo.
if %ERRORLEVEL% equ 0 (
    echo ===================================================
    echo   Subida completada con exito en GitHub!
    echo ===================================================
) else (
    echo Hubo un problema al subir. Revisa tus credenciales de GitHub.
)
pause
