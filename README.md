# HP Printer Counter

批次擷取 HP 印表機使用量統計的工具，支援 Python 和 Node.js 版本。

## 功能特色

- ✅ 批次讀取多台 HP 印表機的列印張數
- ✅ 支援 HTTP/HTTPS 自動切換
- ✅ 支援 Basic Auth 認證
- ✅ 支援多種 HP 印表機型號
- ✅ Excel 輸入，CSV 輸出
- ✅ 提供 Python 和 Node.js 兩種版本

## 支援的印表機型號

### M225/M425/M426 系列（黑白多功能事務機）
- M225、M225dw
- M425、M425dn
- M426、M426fdn

### CP1525/M251/M254/M255 系列（彩色雷射印表機）
- CP1525、CP1525nw
- M251nw
- M254dw、M255dw

### 4103fdn 系列（新款雷射印表機）
- 4103fdn、M4103fdn
- LaserJet Pro 4103fdn

## Python 版本

### 安裝依賴

```bash
pip install pandas openpyxl requests
```

### 使用方式

```bash
python GetPrinterCount.py --excel printers.xlsx --out output.csv --debug
```

### 參數說明

- `--excel <path>` (必填): Excel 檔案路徑
- `--out <path>` (選填): 輸出 CSV 路徑，預設為 `hp_usage_output.csv`
- `--debug` (選填): 啟用除錯模式

## Node.js 版本

### 安裝依賴

```bash
npm install
```

### 使用方式

```bash
node GetPrinterCount.js --excel printers.xlsx --out output.csv --debug
```
python3 GetPrinterCount.py --excel printers.xlsx --out output.csv --debug
## Excel 檔案格式

### 必填欄位

| 欄位名稱 | 說明 |
|---------|------|
| ip / IP / host | 印表機 IP 位址 |
| model / Model / 型號 / 機型 | 印表機型號 |

### 選填欄位（如需認證）

| 欄位名稱 | 說明 |
|---------|------|
| username / user | 使用者帳號 |
| password / pass | 密碼 |

### Excel 範例

| ip | model |
|---|---|
| 192.168.1.100 | M225dw |
| 192.168.1.101 | M426fdn |
| 192.168.1.102 | CP1525nw |

## 輸出結果

程式會產生 CSV 檔案，包含：

- `host`: 印表機 IP
- `model`: 印表機型號
- `parser_used`: 使用的解析器
- `printer_total_impressions`: 列印總張數
- `copy_total_impressions`: 影印總張數
- `fax_total_impressions`: 傳真總張數
- `mono_impressions`: 黑白列印張數
- `color_impressions`: 彩色列印張數
- `pcl6_total_impressions`: PCL6 列印總張數
- `status`: 處理狀態

## 打包成 Windows 執行檔

詳見 [BUILD_EXE_README.md](BUILD_EXE_README.md)

### 快速打包（在 Windows 上）

```bash
pip install pyinstaller
pyinstaller --onefile --name=GetPrinterCount --console GetPrinterCount.py
```

執行檔會產生在 `dist/GetPrinterCount.exe`

## 技術說明

### 連線方式
- 使用 HP LEDM (Ledger Enterprise Data Manager) 協定
- 透過 HTTP/HTTPS 存取印表機 EWS (Embedded Web Server)
- 支援自簽憑證環境

### 嘗試的 URL 路徑
1. `/DevMgmt/ProductUsageDyn.xml`
2. `/hp/device/ProductUsageDyn.xml`
3. `/hp/device/this.Device/ProductUsageDyn.xml`
4. `/ProductUsageDyn.xml`

## 授權

MIT License

## 作者

Franco Liu


 candidate_paths = candidate_paths or [
        "/DevMgmt/ProductUsageDyn.xml",
        "/hp/device/ProductUsageDyn.xml",
        "/hp/device/this.Device/ProductUsageDyn.xml",
        "/ProductUsageDyn.xml",
    ]

M402 -> /DevMgmt/ProductUsageDyn.xml