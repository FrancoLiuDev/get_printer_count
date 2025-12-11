# GetPrinterCount User Manual

## Overview
GetPrinterCount is a tool for batch retrieving HP printer usage statistics. It supports multiple HP printer models and can automatically obtain print volume information from the printer's LEDM (Lightweight Embedded Device Management) interface.

## Features
- 🖨️ Support for multiple HP printer models
- 📊 Batch retrieval of printer usage statistics
- 📁 Excel input file support
- 💾 CSV format report output
- 🔍 Built-in debug mode
- 🚀 Single executable file, no Python environment required

## System Requirements
- Windows 10/11
- Network connectivity (must be able to access target printers)

## File Description
- `GetPrinterCount.exe` - Main program executable
- `printers.xlsx` - Sample printer list file
- `README_EN.md` - This manual

## Preparation

### 1. Prepare Printer List Excel File
Create an Excel file (recommended name: `printers.xlsx`) with the following columns:

| Column Name | Required | Description | Example |
|-------------|----------|-------------|---------|
| ip | ✅ | Printer IP address | 192.168.1.100 |
| model | ✅ | Printer model | M426fdn |
| username | ⭕ | Login username (if authentication required) | admin |
| password | ⭕ | Login password (if authentication required) | password |

**Notes:**
- Column names are case-insensitive
- Alternative names like `host` are also supported
- If printer doesn't require authentication, username/password can be omitted

### 2. Supported Printer Models
Currently supports the following HP printer series:
- M225 series (M225dw)
- M425 series (M425dn)
- M426 series (M426fdn)
- CP1525 series (CP1525, CP1525nw)
- M251 series (M251nw)
- M254 series (M254dw)
- M255 series (M255dw)
- M4103 series (M4103fdn)

## Usage

### Basic Usage
```cmd
GetPrinterCount.exe --excel printers.xlsx --out output.csv
```

### Complete Parameter Description
```cmd
GetPrinterCount.exe [options]

Required parameters:
  --excel EXCEL    Specify printer list Excel file path

Optional parameters:
  --out OUT        Specify output CSV file path (default: hp_usage_output.csv)
  --debug          Enable debug mode, show detailed execution information
  -h, --help       Show help message
```

### Usage Examples

#### 1. Basic Usage
```cmd
GetPrinterCount.exe --excel printers.xlsx --out report.csv
```

#### 2. Enable Debug Mode
```cmd
GetPrinterCount.exe --excel printers.xlsx --out report.csv --debug
```

#### 3. Use Default Output Filename
```cmd
GetPrinterCount.exe --excel printers.xlsx
```
> Will output to `hp_usage_output.csv`

## Output Report Description

After execution, a CSV report file will be generated with the following columns:

| Column Name | Description |
|-------------|-------------|
| host | Printer IP address |
| model | Printer model |
| parser_used | Parser used |
| printer_total_impressions | Total print count |
| copy_total_impressions | Total copy count |
| fax_total_impressions | Total fax count |
| mono_impressions | Monochrome print count |
| color_impressions | Color print count |
| pcl6_total_impressions | PCL6 total print count |
| status | Retrieval status |

### Status Description
- `ok` - Successfully retrieved data
- `error: [error message]` - Retrieval failed, showing error reason

## Troubleshooting

### Common Issues

#### 1. Connection Failed
**Error Message:** `Connection timeout` or `Connection refused`
**Solution:**
- Check if printer IP address is correct
- Confirm printer is powered on and connected to network
- Check firewall settings
- Try ping printer IP

#### 2. Authentication Failed
**Error Message:** `401 Unauthorized`
**Solution:**
- Add correct username and password in Excel file
- Check printer EWS settings

#### 3. Unsupported Printer Model
**Error Message:** `Unsupported model` or no data output
**Solution:**
- Confirm printer model is in supported list
- Check if printer supports LEDM interface
- Try manually accessing `http://[printer IP]/DevMgmt/ProductUsageDyn.xml`

#### 4. Excel File Format Error
**Error Message:** `File not found` or `Invalid format`
**Solution:**
- Confirm file path is correct
- Check Excel file format (must be .xlsx)
- Confirm required columns (ip, model) exist

### Debug Mode
Use `--debug` parameter to see detailed execution process:
```cmd
GetPrinterCount.exe --excel printers.xlsx --out report.csv --debug
```

Debug output example:
```
[DEBUG] 200 text/xml; charset=utf-8 http://192.168.1.100/DevMgmt/ProductUsageDyn.xml
[DEBUG] wrote report.csv with 5 rows
```

## Technical Support

### Contact Information
If you encounter problems or need technical support, please provide:
1. Error message screenshot
2. Excel file format used
3. Printer model and IP address
4. Debug mode output results

### Version Information
- Version: 1.0
- Build Date: 2025-12-09
- Compatibility: Windows 10/11

---

**Note:** This tool is only compatible with HP printers. Other printer brands are not supported. Please ensure appropriate network access permissions before use.