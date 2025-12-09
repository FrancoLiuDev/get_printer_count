# HP Printer Counter - Windows 執行檔打包說明

## 方法 1：使用自動打包腳本（推薦）

### 1. 安裝 PyInstaller
```bash
pip install pyinstaller
```

### 2. 執行打包腳本
```bash
python build_windows_exe.py
```

### 3. 取得執行檔
打包完成後，執行檔位於：
```
dist/GetPrinterCount.exe
```

---

## 方法 2：使用 PyInstaller 規格檔

```bash
pip install pyinstaller
pyinstaller GetPrinterCount.spec
```

---

## 方法 3：直接使用 PyInstaller 指令

### 基本版（單一執行檔）
```bash
pyinstaller --onefile --name=GetPrinterCount --console GetPrinterCount.py
```

### 完整版（包含所有依賴）
```bash
pyinstaller --onefile ^
    --name=GetPrinterCount ^
    --console ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=requests ^
    GetPrinterCount.py
```

---

## Windows 上的使用方式

### 1. 將以下檔案放在同一資料夾：
- `GetPrinterCount.exe`
- `printers.xlsx` (您的印表機清單)

### 2. 開啟命令提示字元 (cmd)，執行：
```cmd
GetPrinterCount.exe --excel printers.xlsx --out output.csv
```

### 3. 開啟除錯模式：
```cmd
GetPrinterCount.exe --excel printers.xlsx --out output.csv --debug
```

---

## 批次檔版本（方便使用）

建立 `run.bat` 檔案：
```batch
@echo off
echo HP Printer Counter 執行中...
GetPrinterCount.exe --excel printers.xlsx --out hp_usage_output.csv --debug
echo.
echo 完成！請查看 hp_usage_output.csv
pause
```

雙擊 `run.bat` 即可執行。

---

## 所需的 Python 套件

確保已安裝以下套件：
```bash
pip install pandas openpyxl requests pyinstaller
```

---

## 打包檔案大小

- 單一執行檔約 40-60 MB
- 包含所有 Python 執行環境和相關套件
- 不需要在目標電腦安裝 Python

---

## 在 Linux 上打包 Windows 執行檔

如果您在 Linux 上要打包 Windows 執行檔，需要使用 Wine + PyInstaller：

```bash
# 安裝 Wine
sudo apt install wine wine64

# 下載 Windows 版 Python
# 然後使用 Wine 執行 PyInstaller
```

或者使用 Docker：
```bash
docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows
```

---

## 疑難排解

### 問題：執行檔開啟後立即關閉
**解決**：使用 `--console` 參數保留命令列視窗

### 問題：缺少模組錯誤
**解決**：使用 `--hidden-import` 參數加入缺少的模組

### 問題：執行檔太大
**解決**：使用 `--exclude-module` 排除不需要的模組

### 問題：防毒軟體誤報
**解決**：PyInstaller 打包的檔案可能被誤報，需要加入白名單

---

## 建議

1. 在 Windows 電腦上打包效果最佳
2. 測試執行檔確保功能正常
3. 提供 Excel 範例檔案給使用者
4. 建立簡單的使用說明文件
