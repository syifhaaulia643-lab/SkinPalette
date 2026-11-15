@echo off
title Autorisasi dan Upload SkinPalette ke GitHub
cd /d "%~dp0"
set "PATH=%~dp0..\Git\cmd;%~dp0..\Git\mingw64\bin;%PATH%"
set "GIT_EXEC_PATH=%~dp0..\Git\mingw64\libexec\git-core"

echo ======================================================================
echo       MEMBUKA JENDELA PERAMBAN UNTUK OTORISASI GITHUB
echo ======================================================================
echo.
echo Sedang menghubungkan ke https://github.com/syifhaaulia643-lab/SkinPalette...
echo Jendela browser akan terbuka secara otomatis untuk login / otorisasi GitHub.
echo Silakan klik tombol "Sign in with your browser" / "Authorize" di browser Anda.
echo.
git.exe push -u origin main
echo.
echo ======================================================================
echo Selesai! Seluruh berkas telah terunggah ke GitHub.
echo ======================================================================
pause
