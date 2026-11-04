@echo off
chcp 65001 >nul
python hepsi.py > cikti\ozet.txt 2>&1
type cikti\ozet.txt
echo.
echo Bitti. cikti\ozet.txt dosyasinin icerigini Claude'a yapistirin.
pause
