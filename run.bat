@echo off
REM HP Printer Counter 執行檔
REM 請確保 printers.xlsx 與此檔案在同一資料夾

echo ===============================================
echo HP Printer Counter 執行中...
echo ===============================================
echo.

REM 檢查 Excel 檔案是否存在
if not exist "printers.xlsx" (
    echo [錯誤] 找不到 printers.xlsx 檔案！
    echo 請確保 printers.xlsx 與此批次檔在同一資料夾。
    echo.
    pause
    exit /b 1
)

REM 執行程式
GetPrinterCount.exe --excel printers.xlsx --out hp_usage_output.csv --debug

REM 檢查執行結果
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===============================================
    echo 執行成功！
    echo 結果已儲存至：hp_usage_output.csv
    echo ===============================================
) else (
    echo.
    echo ===============================================
    echo 執行失敗！錯誤碼：%ERRORLEVEL%
    echo ===============================================
)

echo.
pause
