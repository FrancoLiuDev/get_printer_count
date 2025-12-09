#!/bin/bash
# 使用 Docker 在 Linux 上打包 Windows exe

echo "使用 Docker 打包 Windows 執行檔..."
echo "注意：需要先安裝 Docker"

docker run -v "$(pwd):/src" \
  cdrx/pyinstaller-windows:python3 \
  "pyinstaller --onefile --name=GetPrinterCount --console GetPrinterCount.py"

echo "完成！執行檔位於 dist/GetPrinterCount.exe"
