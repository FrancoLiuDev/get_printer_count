#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNMP 查詢工具 - 圖形介面版本
支援輸入 IP 位址和 MIB OID，並透過 SNMP 協定查詢裝置資訊
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from pysnmp.hlapi import *

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
        
        # SNMP 版本選擇
        ttk.Label(main_frame, text="SNMP 版本:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.version_var = tk.StringVar(value="2c")
        version_frame = ttk.Frame(main_frame)
        version_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(version_frame, text="v2c", variable=self.version_var, 
                       value="2c", command=self.on_version_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(version_frame, text="v3", variable=self.version_var, 
                       value="3", command=self.on_version_change).pack(side=tk.LEFT, padx=5)
        
        # 使用者名稱 (v3 專用)
        ttk.Label(main_frame, text="使用者名稱:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.username_entry.insert(0, "admin")  # 預設值
        
        # 密碼/Community String
        ttk.Label(main_frame, text="密碼:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.community_entry = ttk.Entry(main_frame, width=30, show="*")
        self.community_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.community_entry.insert(0, "public")  # 預設值
        
        # v3 安全級別 (v3 專用)
        ttk.Label(main_frame, text="v3 安全級別:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.v3_level_var = tk.StringVar(value="noAuthNoPriv")
        v3_level_frame = ttk.Frame(main_frame)
        v3_level_frame.grid(row=4, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(v3_level_frame, text="無驗證", variable=self.v3_level_var, 
                       value="noAuthNoPriv", command=self.on_v3_level_change).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(v3_level_frame, text="驗證", variable=self.v3_level_var, 
                       value="authNoPriv", command=self.on_v3_level_change).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(v3_level_frame, text="驗證+加密", variable=self.v3_level_var, 
                       value="authPriv", command=self.on_v3_level_change).pack(side=tk.LEFT, padx=2)
        
        # v3 認證協定 (v3 專用)
        ttk.Label(main_frame, text="v3 認證協定:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.v3_auth_var = tk.StringVar(value="MD5")
        v3_auth_frame = ttk.Frame(main_frame)
        v3_auth_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(v3_auth_frame, text="MD5", variable=self.v3_auth_var, value="MD5").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(v3_auth_frame, text="SHA", variable=self.v3_auth_var, value="SHA").pack(side=tk.LEFT, padx=5)
        
        # v3 加密協定 (v3 專用)
        ttk.Label(main_frame, text="v3 加密協定:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.v3_priv_var = tk.StringVar(value="DES")
        v3_priv_frame = ttk.Frame(main_frame)
        v3_priv_frame.grid(row=6, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(v3_priv_frame, text="DES", variable=self.v3_priv_var, value="DES").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(v3_priv_frame, text="AES", variable=self.v3_priv_var, value="AES").pack(side=tk.LEFT, padx=5)
        
        # v3 加密密碼 (v3 專用)
        ttk.Label(main_frame, text="v3 加密密碼:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.v3_priv_pass_entry = ttk.Entry(main_frame, width=30, show="*")
        self.v3_priv_pass_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5)
        self.v3_priv_pass_entry.insert(0, "")  # 預設空白
        
        # MIB OID 輸入
        ttk.Label(main_frame, text="MIB OID:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.oid_entry = ttk.Entry(main_frame, width=30)
        self.oid_entry.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5)
        self.oid_entry.insert(0, "1.3.6.1.2.1.1.1.0")  # 預設值：sysDescr
        
        # 常用 OID 快捷按鈕
        oid_buttons_frame = ttk.LabelFrame(main_frame, text="常用 OID", padding="5")
        oid_buttons_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
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
        self.query_button.grid(row=10, column=0, columnspan=2, pady=10)
        
        # 結果顯示區域
        ttk.Label(main_frame, text="查詢結果:").grid(row=11, column=0, sticky=tk.W, pady=5)
        self.result_text = scrolledtext.ScrolledText(main_frame, width=60, height=15, wrap=tk.WORD)
        self.result_text.grid(row=12, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 設定網格權重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(12, weight=1)
        
        # 初始化欄位顯示狀態
        self.on_version_change()
    
    def on_v3_level_change(self):
        """根據 v3 安全級別顯示/隱藏相關欄位"""
        level = self.v3_level_var.get()
        version = self.version_var.get()
        
        if version == "3":
            if level == "noAuthNoPriv":
                # 無驗證模式：不需要密碼
                self.community_entry.config(state="disabled")
                # 隱藏 v3 認證和加密選項
                for child in self.root.grid_slaves():
                    if child.grid_info().get('row') in [5, 6, 7]:
                        for widget in child.winfo_children():
                            widget.config(state="disabled")
            elif level == "authNoPriv":
                # 驗證模式：需要密碼和認證協定
                self.community_entry.config(state="normal")
                self.v3_priv_pass_entry.config(state="disabled")
            else:  # authPriv
                # 驗證+加密模式：需要所有欄位
                self.community_entry.config(state="normal")
                self.v3_priv_pass_entry.config(state="normal")
    
    def on_version_change(self):
        """根據版本選擇顯示/隱藏相關欄位"""
        version = self.version_var.get()
        if version == "3":
            # v3 需要使用者名稱
            self.username_entry.config(state="normal")
            self.on_v3_level_change()
        else:
            # v2c 不需要使用者名稱，但需要 community
            self.username_entry.config(state="disabled")
            self.community_entry.config(state="normal")
            # 禁用 v3 相關選項
            self.v3_priv_pass_entry.config(state="disabled")
        
    def perform_query(self):
        """執行 SNMP 查詢"""
        ip_address = self.ip_entry.get().strip()
        community = self.community_entry.get().strip()
        username = self.username_entry.get().strip()
        oid = self.oid_entry.get().strip()
        version = self.version_var.get()
        
        # 驗證輸入
        if not ip_address:
            messagebox.showerror("錯誤", "請輸入 IP 位址")
            return
        
        if version == "3" and not username:
            messagebox.showerror("錯誤", "SNMPv3 需要使用者名稱")
            return
        
        # v3 密碼驗證
        if version == "3":
            level = self.v3_level_var.get()
            if level != "noAuthNoPriv":
                if not community:
                    messagebox.showerror("錯誤", "SNMPv3 驗證模式需要密碼")
                    return
                if len(community) < 8:
                    messagebox.showerror("錯誤", "SNMPv3 認證密碼至少需要 8 個字元")
                    return
            
            if level == "authPriv":
                priv_pass = self.v3_priv_pass_entry.get().strip()
                if not priv_pass:
                    messagebox.showerror("錯誤", "SNMPv3 加密模式需要加密密碼")
                    return
                if len(priv_pass) < 8:
                    messagebox.showerror("錯誤", "SNMPv3 加密密碼至少需要 8 個字元")
                    return
        else:
            # v2c 驗證
            if not community:
                messagebox.showerror("錯誤", "請輸入密碼")
                return
        
        if not oid:
            messagebox.showerror("錯誤", "請輸入 MIB OID")
            return
        
        # 清空結果區域
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"正在查詢 {ip_address} ...\n")
        self.result_text.insert(tk.END, f"OID: {oid}\n")
        if version == "3":
            self.result_text.insert(tk.END, f"使用者: {username}\n")
        self.result_text.insert(tk.END, f"密碼: {'*' * len(community)}\n")
        self.result_text.insert(tk.END, f"版本: SNMPv{version}\n")
        self.result_text.insert(tk.END, "-" * 60 + "\n\n")
        self.root.update()
        
        # 在後台執行查詢
        thread = threading.Thread(target=self.sync_query, args=(ip_address, community, username, oid, version))
        thread.daemon = True
        thread.start()
    
    def sync_query(self, ip_address, community, username, oid, version):
        """執行 SNMP 查詢 (支援 v2c 和 v3)"""
        try:
            # 設定 SNMP 認證資訊
            if version == "3":
                # SNMPv3 認證配置
                level = self.v3_level_var.get()
                auth_protocol = self.v3_auth_var.get()
                priv_protocol = self.v3_priv_var.get()
                priv_pass = self.v3_priv_pass_entry.get().strip()
                
                try:
                    if level == "noAuthNoPriv":
                        # 無驗證無加密
                        snmp_auth = UsmUserData(username)
                    elif level == "authNoPriv":
                        # 有驗證無加密
                        auth_proto = usmHMACMD5AuthProtocol if auth_protocol == "MD5" else usmHMACSHAAuthProtocol
                        snmp_auth = UsmUserData(username, community, authProtocol=auth_proto)
                    else:  # authPriv
                        # 有驗證有加密
                        auth_proto = usmHMACMD5AuthProtocol if auth_protocol == "MD5" else usmHMACSHAAuthProtocol
                        priv_proto = usmDESPrivProtocol if priv_protocol == "DES" else usmAesCfb128Protocol
                        snmp_auth = UsmUserData(username, community, priv_pass, 
                                               authProtocol=auth_proto, privProtocol=priv_proto)
                except Exception as auth_error:
                    self.update_result(f"\n認證配置錯誤: {str(auth_error)}\n")
                    self.update_result("請確認:\n")
                    self.update_result("  - 認證密碼至少 8 個字元\n")
                    self.update_result("  - 加密密碼至少 8 個字元\n")
                    self.update_result("  - 使用者名稱和密碼正確\n")
                    return
            else:
                # SNMPv2c 使用 CommunityData
                snmp_auth = CommunityData(community, mpModel=1)
            
            # 執行 SNMP GET 請求
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(
                    SnmpEngine(),
                    snmp_auth,
                    UdpTransportTarget((ip_address, 161), timeout=2.0, retries=3),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid))
                )
            )
            
            if errorIndication:
                error_msg = str(errorIndication)
                self.update_result(f"錯誤: {error_msg}\n\n")
                
                # 提供常見錯誤的解決建議
                if "Unknown USM user" in error_msg or "usmStatsUnknownUserNames" in error_msg:
                    self.update_result("💡 使用者不存在，請確認：\n")
                    self.update_result("  1. 使用者名稱在設備上已建立\n")
                    self.update_result("  2. 使用者名稱拼寫正確（區分大小寫）\n\n")
                elif "authorizationError" in error_msg or "usmStatsWrongDigests" in error_msg:
                    self.update_result("💡 認證失敗，請確認：\n")
                    self.update_result("  1. 認證密碼正確\n")
                    self.update_result("  2. 認證協定匹配（MD5/SHA）\n")
                    self.update_result("  3. 設備端使用相同的認證設定\n\n")
                elif "Decryption error" in error_msg or "usmStatsDecryptionErrors" in error_msg:
                    self.update_result("💡 解密失敗，請確認：\n")
                    self.update_result("  1. 加密密碼正確\n")
                    self.update_result("  2. 加密協定匹配（DES/AES）\n")
                    self.update_result("  3. 設備端使用相同的加密設定\n\n")
                elif "Timeout" in error_msg:
                    self.update_result("💡 連線逾時，請確認：\n")
                    self.update_result("  1. IP 位址正確且設備在線\n")
                    self.update_result("  2. 網路連線正常\n")
                    self.update_result("  3. SNMP 服務已啟用（端口 161）\n\n")
                
                self.update_result("📋 SNMPv3 設備端配置建議（DES 範例）：\n")
                self.update_result("  使用者名稱: admin\n")
                self.update_result("  認證協定: MD5 或 SHA\n")
                self.update_result("  認證密碼: 至少 8 字元（例如：auth12345）\n")
                self.update_result("  加密協定: DES\n")
                self.update_result("  加密密碼: 至少 8 字元（例如：priv12345）\n")
                self.update_result("  安全級別: authPriv（驗證+加密）\n")
                
            elif errorStatus:
                self.update_result(
                    f'錯誤: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or "?"}\n')
            else:
                self.update_result("查詢成功！\n\n")
                for varBind in varBinds:
                    oid_str = varBind[0].prettyPrint()
                    value_str = varBind[1].prettyPrint()
                    self.update_result(f"OID: {oid_str}\n")
                    self.update_result(f"值: {value_str}\n")
                    
        except Exception as e:
            self.update_result(f"\n發生異常錯誤:\n{str(e)}\n")
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"查詢失敗: {str(e)}"))
    
    def update_result(self, text):
        """線程安全地更新結果區域"""
        self.root.after(0, lambda: self.result_text.insert(tk.END, text))

def main():
    root = tk.Tk()
    app = SNMPQueryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
