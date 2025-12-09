# HP Printer Counter - Node.js 版本

這是從 Python 版本轉換的 Node.js 版本，用於批次擷取 HP 印表機的使用量統計。

## 安裝

```bash
npm install
```

## 使用方式

### 基本用法

```bash
node GetPrinterCount.js --excel printers.xlsx --out hp_usage_output.csv
```

### 開啟除錯模式

```bash
node GetPrinterCount.js --excel printers.xlsx --out results.csv --debug
```

## 參數說明

- `--excel <path>` (必填): Excel 檔案路徑
- `--out <path>` (選填): 輸出 CSV 檔案路徑，預設為 `hp_usage_output.csv`
- `--debug` (選填): 啟用除錯模式

## Excel 檔案格式

### 必填欄位

| 欄位名稱 | 說明 |
|---------|------|
| ip / IP / host | 印表機 IP 位址 |
| model / Model / 型號 / 機型 | 印表機型號 |

### 選填欄位 (如需認證)

| 欄位名稱 | 說明 |
|---------|------|
| username / user | 使用者帳號 |
| password / pass | 密碼 |

### Excel 範例

```
| ip            | model    |
|---------------|----------|
| 192.168.1.100 | M225dw   |
| 192.168.1.101 | M426fdn  |
| 192.168.1.102 | CP1525nw |
```

## 支援的印表機型號

### M225/M425/M426 系列
- M225、M225dw
- M425、M425dn
- M426、M426fdn

**輸出欄位**: printer_total_impressions, copy_total_impressions, fax_total_impressions

### 彩色雷射系列
- CP1525、CP1525nw
- M251nw
- M254dw
- M255dw

**輸出欄位**: mono_impressions, color_impressions

### 4103fdn 系列
- 4103fdn
- M4103fdn
- LaserJet Pro 4103fdn

**輸出欄位**: pcl6_total_impressions

## 輸出結果

程式會產生 CSV 檔案，包含以下欄位：

- `host`: 印表機 IP
- `model`: 印表機型號
- `parser_used`: 使用的解析器名稱
- `printer_total_impressions`: 列印總張數
- `copy_total_impressions`: 影印總張數
- `fax_total_impressions`: 傳真總張數
- `mono_impressions`: 黑白列印張數
- `color_impressions`: 彩色列印張數
- `pcl6_total_impressions`: PCL6 列印總張數
- `status`: 處理狀態 (ok / unknown_model / no_xml / parse_error)

## 依賴套件

- `axios`: HTTP 請求
- `commander`: CLI 參數解析
- `xml2js`: XML 解析
- `xlsx`: Excel 檔案處理

## 與 Python 版本的差異

1. 使用 `axios` 取代 Python 的 `requests`
2. 使用 `xml2js` 解析 XML
3. 使用 `xlsx` 處理 Excel 檔案
4. 使用 `commander` 處理命令列參數
5. 功能完全相同，支援相同的印表機型號和輸出格式

## 故障排除

如果遇到連線問題：

1. 確認印表機 IP 是否可連線
2. 確認印表機支援 HP LEDM 協定
3. 使用 `--debug` 參數查看詳細錯誤訊息
4. 檢查是否需要提供帳號密碼

## 授權

MIT
