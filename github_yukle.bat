@echo off
chcp 65001 >nul
title MerVid Studio - GitHub Yükleyici

echo ========================================================
echo         MERVID STUDIO - GITHUB YÜKLEYİCİ
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/4] Git kontrolleri yapılıyor...
git status >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [BILGI] Git deposu baslatiliyor...
    git init
    git config user.name "oguxmercan"
    git config user.email "oguxmercan@users.noreply.github.com"
)

echo.
echo [2/4] GitHub Remote adresi kontrol ediliyor...
git remote get-url origin >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo GitHub'da olusturdugunuz repo adresini girin
    echo Varsayilan: https://github.com/oguxmercan/MerVid-Studio.git
    echo.
    set /p REPO_URL="Repo URL (Bos birakirsaniz varsayilan kullanilir): "
    if "%REPO_URL%"=="" (
        git remote add origin https://github.com/oguxmercan/MerVid-Studio.git
        echo Varsayilan adres eklendi: https://github.com/oguxmercan/MerVid-Studio.git
    ) else (
        git remote add origin %REPO_URL%
        echo Girilen adres eklendi: %REPO_URL%
    )
) else (
    for /f "delims=" %%i in ('git remote get-url origin') do set CURRENT_REMOTE=%%i
    echo Mevcut Remote: %CURRENT_REMOTE%
)

echo.
echo [3/4] Dosyalar hazirlaniyor...
git branch -M main
git add .
git commit -m "feat: MerVid Studio v1.0.0 with Real-Debrid & 4K media downloader" >nul 2>&1

echo.
echo [4/4] GitHub'a gonderiliyor (git push -u origin main)...
echo.
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo      TEBRIKLER! MerVid Studio GitHub'a basariyla yuklendi!
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo [BILGI] Eger GitHub sizden giris (Sign in with Browser)
    echo veya Token istediyse lutfen yetkiyi onaylayin.
    echo Ardindan bu dosyayi tekrar cift tiklayarak calistirabilirsiniz.
    echo ========================================================
)

echo.
pause
