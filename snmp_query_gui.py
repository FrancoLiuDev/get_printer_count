#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNMP 查詢工具 - 圖形介面版本
支援輸入 IP 位址和 MIB OID，並透過 SNMP 協定查詢裝置資訊
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
from pysnmp.hlapi.asyncio import *

class SNMPQueryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SNMP 查詢工具")
        self.root.geometry("600x500")
        
        # 建立主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # IP 位址輸入
        ttk.Label(main_frame, text="IP 位址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ip_entry = ttk.Entry(main_frame, width=30)
        self.ip_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.ip_entry.insert(0, "192.168.1.1")  # 預設值
        
        # SNMP Community String
        ttk.Label(main_frame, text="Community:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.community_entry = ttk.Entry(main_frame, width=30)
        self.community_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.community_entry.insert(0, "public")  # 預設值
        
        # SNMP 版本
        ttk.Label(main_frame, text="SNMP 版本:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.version_var = tk.StringVar(value="2c")
        version_frame = ttk.Frame(main_frame)
        version_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(version_frame, text="v1", variable=self.version_var, value="1").pack(side=tk.LEFT)
        ttk.Radiobutton(version_frame, text="v2c", variable=self.version_var, value="2c").pack(side=tk.LEFT)
        
        # MIB OID 輸入
        ttk.Label(main_frame, text="MIB OID:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.oid_entry = ttk.Entry(main_frame, width=30)
        self.oid_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.oid_entry.insert(0, "1.3.6.1.2.1.1.1.0")  # 預設值：sysDescr
        
        # 常用 OID 快捷按鈕
        oid_buttons_frame = ttk.LabelFrame(main_frame, text="常用 OID", padding="5")
        oid_buttons_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        common_oids = [
            ("系統描述", "1.3.6.1.2.1.1.1.0"),
            ("系統名稱", "1.3.6.1.2.1.1.5.0"),
            ("系統運行時間", "1.3.6.1.2.1.1.3.0"),
            ("系統聯絡人", "1.3.6.1.2.1.1.4.0"),
        ]
        
        for idx, (name, oid) in enumerate(common_oids):
            btn = ttk.Button(oid_buttons_frame, text=name, 
                           command=lambda o=oid: self.oid_entry.delete(0, tk.END) or self.oid_entry.insert(0, o))
            btn.grid(row=idx//2, column=idx%2, padx=5, pady=2, sticky=(tk.W, tk.E))
        
        # 查詢按鈕
        self.query_button = ttk.Button(main_frame, text="執行查詢", command=self.perform_query)
        self.query_button.grid(row=5, column=0, columnspan=2, pady=10)
        
        # 結果顯示區域
        ttk.Label(main_frame, text="查詢結果:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.result_text = scrolledtext.ScrolledText(main_frame, width=60, height=15, wrap=tk.WORD)
        self.result_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 設定網格權重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
    def perform_query(self):
        """執行 SNMP 查詢"""
        ip_address = self.ip_entry.get().strip()
        community = self.community_entry.get().strip()
        oid = self.oid_entry.get().strip()
        version = self.version_var.get()
        
        # 驗證輸入
        if not ip_address:
            messagebox.showerror("錯誤", "請輸入 IP 位址")
            return
        
        if not oid:
            messagebox.showerror("錯誤", "請輸入 MIB OID")
            return
        
        # 清空結果區域
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"正在查詢 {ip_address} ...\n")
        self.result_text.insert(tk.END, f"OID: {oid}\n")
        self.result_text.insert(tk.END, f"Community: {community}\n")
        self.result_text.insert(tk.END, f"版本: SNMPv{version}\n")
        self.result_text.insert(tk.END, "-" * 60 + "\n\n")
        self.root.update()
        
        # 在後台執行異步查詢
        asyncio.run(self.async_query(ip_address, community, oid, version))
    
    async def async_query(self, ip_address, community, oid, version):
        """異步執行 SNMP 查詢"""
        try:
            # 設定 SNMP 版本
            if version == "1":
                snmp_version = CommunityData(community, mpModel=0)
            else:  # v2c
                snmp_version = CommunityData(community, mpModel=1)
            
            # 執行 SNMP GET 請求
            errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                SnmpEngine(),
                snmp_version,
                UdpTransportTarget((ip_address, 161), timeout=2.0, retries=3),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            if errorIndication:
                self.result_text.insert(tk.END, f"錯誤: {errorIndication}\n")
            elif errorStatus:
                self.result_text.insert(tk.END, 
                    f'錯誤: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or "?"}\n')
            else:
                self.result_text.insert(tk.END, "查詢成功！\n\n")
                for varBind in varBinds:
                    oid_str = varBind[0].prettyPrint()
                    value_str = varBind[1].prettyPrint()
                    self.result_text.insert(tk.END, f"OID: {oid_str}\n")
                    self.result_text.insert(tk.END, f"值: {value_str}\n")
                    
        except Exception as e:
            self.result_text.insert(tk.END, f"\n發生異常錯誤:\n{str(e)}\n")
            messagebox.showerror("錯誤", f"查詢失敗: {str(e)}")

def main():
    root = tk.Tk()
    app = SNMPQueryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
