# Timeout 處理改進說明

## 問題
原本程式在連線印表機 timeout 時會停下來，影響其他設備的處理。

## 解決方案

### 1. 降低 Timeout 時間
```python
# 原本：(5, 10) 秒
# 修改為：(3, 5) 秒
def make_session(timeout: Tuple[int, int]=(3, 5))
```
- **連線 timeout**: 5秒 → 3秒
- **讀取 timeout**: 10秒 → 5秒
- 加快失敗設備的跳過速度

### 2. 減少重試次數
```python
# 原本：total=3 (失敗後重試3次)
# 修改為：total=1 (失敗後重試1次)
retries = Retry(total=1, backoff_factor=0.3, ...)
```

### 3. 明確的錯誤處理
分別處理不同類型的錯誤：
- `requests.Timeout`: 連線逾時
- `requests.ConnectionError`: 連線錯誤（設備離線或IP不存在）
- `requests.RequestException`: 其他請求錯誤
- `Exception`: 捕捉所有其他異常

所有錯誤都使用 `continue`，確保程式繼續處理下一台設備。

### 4. 進度顯示
新增即時進度顯示：
```
開始處理 10 台印表機...
[1/10] 正在連線 192.168.1.100 (M225dw)... ✓ 成功
[2/10] 正在連線 192.168.1.101 (M426fdn)... ❌ 無法連線或逾時
[3/10] 正在連線 192.168.1.102 (CP1525nw)... ✓ 成功
...
==================================================
處理完成！成功: 8 台，失敗: 2 台
結果已儲存至: hp_usage_output.csv
==================================================
```

## 調整參數

如果您需要更長或更短的 timeout，可以修改：

```python
# 在 GetPrinterCount.py 第 247 行
session = make_session(timeout=(3, 5))  # (連線timeout, 讀取timeout)

# 範例：
session = make_session(timeout=(2, 3))   # 更快速，適合內網
session = make_session(timeout=(5, 10))  # 更寬容，適合慢速網路
```

## 測試

執行程式時會看到每台設備的處理狀態：
```bash
python GetPrinterCount.py --excel printers.xlsx --out output.csv --debug
```

## 優點

1. ✅ **不會中斷**: Timeout 不會停止整個程式
2. ✅ **快速跳過**: 失敗的設備快速跳過（約3-6秒）
3. ✅ **清楚回饋**: 即時顯示每台設備的處理狀態
4. ✅ **完整記錄**: 所有設備都會記錄在輸出檔案中，包含失敗狀態
5. ✅ **除錯友善**: debug 模式會顯示詳細錯誤訊息
