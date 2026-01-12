# -*- coding: utf-8 -*-
"""
用於打包 GetPrinterCount.py 成 Windows 執行檔的設定
使用 PyInstaller 打包

安裝方式：
    pip install pyinstaller

打包指令：
    python build_windows_exe.py
    
或直接使用 PyInstaller：
    pyinstaller --onefile --name=GetPrinterCount --icon=printer.ico GetPrinterCount.py
"""

import PyInstaller.__main__
import os

# 取得當前目錄
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, 'GetPrinterCount.py')

# PyInstaller 參數
pyinstaller_args = [
    script_path,                    # 主程式
    '--onefile',                    # 打包成單一執行檔
    '--name=GetPrinterCount',       # 執行檔名稱
    '--console',                    # 保留命令列視窗
    '--clean',                      # 清除暫存檔
    '--noconfirm',                  # 不詢問覆蓋
    # '--icon=printer.ico',         # 如果有圖示檔可以加上
    # 排除不需要的大型依賴
    '--exclude-module=torch',
    '--exclude-module=torchvision',
    '--exclude-module=matplotlib',
    '--exclude-module=scipy',
    '--exclude-module=PIL',
    '--exclude-module=cv2',
    '--exclude-module=tensorflow',
    '--exclude-module=transformers',
    '--exclude-module=onnxruntime',
    '--exclude-module=triton',
    '--exclude-module=nvidia',
    '--exclude-module=sympy',
]

if __name__ == '__main__':
    print("=" * 60)
    print("開始打包 GetPrinterCount.py 成 Windows 執行檔")
    print("=" * 60)
    
    PyInstaller.__main__.run(pyinstaller_args)
    
    print("\n" + "=" * 60)
    print("打包完成！")
    print("執行檔位置：dist/GetPrinterCount.exe")
    print("=" * 60)
    print("\n使用方式：")
    print("  GetPrinterCount.exe --excel printers.xlsx --out output.csv --debug")
