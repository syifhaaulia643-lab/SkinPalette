@echo off
title Menjalankan SkinPalette Web App
cd /d "%~dp0"
echo ======================================================================
echo         MENJALANKAN SKINPALETTE WEB APP (DERMATONE AI)
echo ======================================================================
echo.
echo Sedang membuka http://localhost:8000 di peramban web Anda...
start http://localhost:8000
echo.
echo Server lokal aktif. Tekan Ctrl+C untuk menghentikan.
"C:\Users\UNIQ\AppData\Local\Programs\Python311\python.exe" -m http.server 8000
pause
