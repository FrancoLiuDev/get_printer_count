# -*- coding: utf-8 -*-
# HP LEDM ProductUsageDyn 批次擷取（含 debug）
# 解析器合併規則：
#   - M225_M425_M426：M225dw / M425dn / M426fdn
#   - CP1525_M251nw_M254dw_M255dw：CP1525 / CP1525nw / M251nw / M254dw / M255dw
#   - M4103fdn：PCL6Impressions 的 TotalImpressions
#
# 使用：
#   python script.py --excel printers.xlsx --out hp_usage_output.csv --debug
#
# Excel 欄位：
#   必填：ip / model   （大小寫不拘，也接受「host」、「型號」、「機型」）
#   選填：username / password  （若 EWS 需要 Basic Auth）

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Tuple, Union, Dict, Any, List

import pandas as pd
import requests
from requests.adapters import HTTPAdapter, Retry

# ---------------------------
# XML Namespaces
# ---------------------------
NS = {
    "dd": "http://www.hp.com/schemas/imaging/con/dictionaries/1.0/",
    "pudyn": "http://www.hp.com/schemas/imaging/con/ledm/productusagedyn/2007/12/11",
}

# ---------------------------
# 工具
# ---------------------------
def _get_text(elem: Optional[ET.Element]) -> Optional[str]:
    return elem.text.strip() if elem is not None and elem.text is not None else None

def _to_int(x: Optional[str]) -> Optional[int]:
    if x is None:
        return None
    try:
        return int(float(x))  # 少數機型可能回傳小數字串
    except ValueError:
        return None

def _load_xml_root(xml_source: Union[str, Path, bytes]) -> ET.Element:
    if isinstance(xml_source, (str, Path)) and Path(xml_source).exists():
        return ET.parse(xml_source).getroot()
    return ET.fromstring(xml_source if isinstance(xml_source, (str, bytes)) else str(xml_source))

def _normalize_model(s: str) -> str:
    """標準化型號字串：小寫、移除非英數（空白、斜線、減號等）"""
    return re.sub(r"[^a-z0-9]", "", s.lower())

def _looks_like_productusagedyn(content: bytes, debug: bool = False) -> bool:
    """嘗試解析 XML；若 root tag 以 'ProductUsageDyn' 結尾即視為符合"""
    try:
        root = ET.fromstring(content)
        ok = root.tag.endswith("ProductUsageDyn")
        return ok
    except ET.ParseError:
        if debug:
            # 留給呼叫端印 preview
            pass
        return False

# ---------------------------
# 解析器（同結構合併）
# ---------------------------
def M225_M425_M426(xml_source: Union[str, Path, bytes]) -> Dict[str, Any]:
    """M225dw / M425dn / M426fdn：三個 total"""
    root = _load_xml_root(xml_source)
    printer_total = _get_text(root.find("./pudyn:PrinterSubunit/dd:TotalImpressions", NS))
    copy_total    = _get_text(root.find("./pudyn:CopyApplicationSubunit/dd:TotalImpressions", NS))
    fax_total     = _get_text(root.find("./pudyn:FaxApplicationSubunit/dd:TotalImpressions", NS))
    return {
        "printer_total_impressions": _to_int(printer_total),
        "copy_total_impressions": _to_int(copy_total),
        "fax_total_impressions": _to_int(fax_total),
    }

def CP1525_M251nw_M254dw_M255dw(xml_source: Union[str, Path, bytes]) -> Dict[str, Any]:
    """CP1525 / CP1525nw / M251nw / M254dw / M255dw：彩機兩值"""
    root = _load_xml_root(xml_source)
    mono  = _get_text(root.find("./pudyn:PrinterSubunit/dd:MonochromeImpressions", NS))
    color = _get_text(root.find("./pudyn:PrinterSubunit/dd:ColorImpressions", NS))
    return {
        "mono_impressions": _to_int(mono),
        "color_impressions": _to_int(color),
    }

def M4103fdn(xml_source: Union[str, Path, bytes]) -> Dict[str, Any]:
    """4103fdn：PCL6Impressions 的 TotalImpressions"""
    root = _load_xml_root(xml_source)
    pcl6_total = _get_text(root.find("./pudyn:PrinterSubunit/dd:PCL6Impressions/dd:TotalImpressions", NS))
    return {
        "pcl6_total_impressions": _to_int(pcl6_total),
    }

# ---------------------------
# 型號字串 -> 解析器
# ---------------------------
MODEL_KEYWORDS: Dict[str, Tuple[str, Any]] = {
    # M225 / M425 / M426 -> 三 total
    "m225": ("M225_M425_M426", M225_M425_M426),
    "m225dw": ("M225_M425_M426", M225_M425_M426),
    "m425": ("M225_M425_M426", M225_M425_M426),
    "m425dn": ("M225_M425_M426", M225_M425_M426),
    "m426": ("M225_M425_M426", M225_M425_M426),
    "m426fdn": ("M225_M425_M426", M225_M425_M426),

    # CP1525 / CP1525nw / M251nw / M254dw / M255dw -> 彩機兩值
    "cp1525": ("CP1525_M251nw_M254dw_M255dw", CP1525_M251nw_M254dw_M255dw),
    "cp1525nw": ("CP1525_M251nw_M254dw_M255dw", CP1525_M251nw_M254dw_M255dw),
    "m251nw": ("CP1525_M251nw_M254dw_M255dw", CP1525_M251nw_M254dw_M255dw),
    "m254dw": ("CP1525_M251nw_M254dw_M255dw", CP1525_M251nw_M254dw_M255dw),
    "m255dw": ("CP1525_M251nw_M254dw_M255dw", CP1525_M251nw_M254dw_M255dw),

    # 4103fdn -> PCL6 TotalImpressions
    "4103fdn": ("M4103fdn", M4103fdn),
    "m4103fdn": ("M4103fdn", M4103fdn),
    "laserjetpro4103fdn": ("M4103fdn", M4103fdn),
}

def resolve_parser(model_str: str) -> Tuple[Optional[str], Optional[Any]]:
    if not model_str:
        return None, None
    norm = _normalize_model(model_str)
    if norm in MODEL_KEYWORDS:
        name, fn = MODEL_KEYWORDS[norm]
        return name, fn
    for key, (name, fn) in MODEL_KEYWORDS.items():
        if key in norm:  # substring 容忍敘述型名稱
            return name, fn
    return None, None

# ---------------------------
# HTTP
# ---------------------------
def make_session(timeout: Tuple[int, int]=(5, 10)) -> requests.Session:
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5,
                    status_forcelist=[429, 500, 502, 503, 504])
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.request_timeout = timeout
    return s

def fetch_product_usage_xml(session: requests.Session,
                            ip: str,
                            candidate_paths: Optional[List[str]] = None,
                            debug: bool = False,
                            auth: Optional[Tuple[str, str]] = None) -> Optional[bytes]:
    candidate_paths = candidate_paths or [
        "/DevMgmt/ProductUsageDyn.xml",
        "/hp/device/ProductUsageDyn.xml",
        "/hp/device/this.Device/ProductUsageDyn.xml",
        "/ProductUsageDyn.xml",
    ]
    schemes = ["http", "https"]
    headers = {
        "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "python-requests/LEDM-scraper"
    }

    for scheme in schemes:
        base = f"{scheme}://{ip}".rstrip("/")
        for p in candidate_paths:
            url = f"{base}/{p.lstrip('/')}"
            try:
                r = session.get(url,
                                headers=headers,
                                timeout=session.request_timeout,
                                verify=False,                # 自簽憑證環境
                                allow_redirects=True,
                                auth=auth)
                if debug:
                    ct = r.headers.get("Content-Type", "")
                    print(f"[DEBUG] {r.status_code} {ct} {url}")
                if not r.ok or not r.content:
                    continue
                if _looks_like_productusagedyn(r.content, debug=debug):
                    return r.content
                else:
                    if debug:
                        preview = r.content[:200]
                        print(f"[DEBUG] not ProductUsageDyn (preview): {preview!r}")
            except requests.RequestException as e:
                if debug:
                    print(f"[DEBUG] request error {url}: {type(e).__name__} {e}")
                continue
    return None

# ---------------------------
# Excel
# ---------------------------
def detect_columns(df: pd.DataFrame) -> Tuple[str, str, Optional[str], Optional[str]]:
    """自動偵測 IP / 型號，以及可選的 username / password 欄位"""
    ip_candidates = ["ip", "IP", "Ip", "host", "Host"]
    model_candidates = ["model", "Model", "型號", "機型"]
    user_candidates = ["username", "Username", "user", "User"]
    pass_candidates = ["password", "Password", "pass", "Pass"]

    ip_col = next((c for c in ip_candidates if c in df.columns), None)
    model_col = next((c for c in model_candidates if c in df.columns), None)
    user_col = next((c for c in user_candidates if c in df.columns), None)
    pass_col = next((c for c in pass_candidates if c in df.columns), None)

    if not ip_col or not model_col:
        missing = []
        if not ip_col: missing.append("IP 欄位（可用 ip/IP/host）")
        if not model_col: missing.append("型號欄位（可用 model/型號/機型）")
        raise ValueError("Excel 欄位缺少：" + "、".join(missing))
    return ip_col, model_col, user_col, pass_col

def process_excel(excel_path: str,
                  output_csv: str = "hp_usage_output.csv",
                  debug: bool = False) -> pd.DataFrame:
    df = pd.read_excel(excel_path)
    ip_col, model_col, user_col, pass_col = detect_columns(df)

    session = make_session()
    rows = []
    for idx, row in df.iterrows():
        ip = str(row[ip_col]).strip()
        model_raw = row[model_col]
        model = "" if pd.isna(model_raw) else str(model_raw).strip()

        # Optional Basic Auth
        auth = None
        if user_col and pass_col:
            u = row[user_col]
            p = row[pass_col]
            if pd.notna(u) and pd.notna(p):
                auth = (str(u), str(p))

        parser_name, parser_fn = resolve_parser(model)

        result: Dict[str, Any] = {
            "host": ip,
            "model": model,
            "parser_used": parser_name,
            "printer_total_impressions": None,
            "copy_total_impressions": None,
            "fax_total_impressions": None,
            "mono_impressions": None,
            "color_impressions": None,
            "pcl6_total_impressions": None,
            "status": "ok",
        }

        if parser_fn is None:
            result["status"] = "unknown_model"
            if debug:
                print(f"[DEBUG] row {idx}: unknown_model -> '{model}'")
            rows.append(result)
            continue

        xml_bytes = fetch_product_usage_xml(session, ip, debug=debug, auth=auth)
        if xml_bytes is None:
            result["status"] = "no_xml"
            if debug:
                print(f"[DEBUG] row {idx}: no_xml for {ip}")
            rows.append(result)
            continue

        try:
            parsed = parser_fn(xml_bytes)
            for k, v in parsed.items():
                result[k] = v
        except Exception as e:
            result["status"] = f"parse_error:{type(e).__name__}"
            if debug:
                print(f"[DEBUG] row {idx}: parse_error {type(e).__name__}: {e}")

        rows.append(result)

    out = pd.DataFrame(rows)
    out.to_csv(output_csv, index=False)
    if debug:
        print(f"[DEBUG] wrote {output_csv} with {len(out)} rows")
    return out

# ---------------------------
# CLI
# ---------------------------
def main():
    ap = argparse.ArgumentParser(description="Fetch HP LEDM ProductUsageDyn stats")
    ap.add_argument("--excel", required=True, help="path to printers.xlsx")
    ap.add_argument("--out", default="hp_usage_output.csv", help="output CSV path")
    ap.add_argument("--debug", action="store_true", help="enable debug logging")
    args = ap.parse_args()

    process_excel(args.excel, output_csv=args.out, debug=args.debug)

if __name__ == "__main__":
    main()

