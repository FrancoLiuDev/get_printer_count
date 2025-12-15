#!/usr/bin/env node
 // -*- coding: utf-8 -*-
// HP LEDM ProductUsageDyn 批次擷取（含 debug）
// 解析器合併規則：
//   - M225_M425_M426：M225dw / M425dn / M426fdn
//   - CP1525_M251nw_M254dw_M255dw：CP1525 / CP1525nw / M251nw / M254dw / M255dw
//   - M4103fdn：PCL6Impressions 的 TotalImpressions
//
// 使用：
//   node GetPrinterCount.js --excel printers.xlsx --out hp_usage_output.csv --debug
//
// Excel 欄位：
//   必填：ip / model   （大小寫不拘，也接受「host」、「型號」、「機型」）
//   選填：username / password  （若 EWS 需要 Basic Auth）

const fs = require('fs');
const path = require('path');
const https = require('https');
const axios = require('axios');
const xlsx = require('xlsx');
const { parseStringPromise } = require('xml2js');
const { Command } = require('commander');

// ---------------------------
// XML Namespaces (for reference)
// ---------------------------
const NS = {
    dd: "http://www.hp.com/schemas/imaging/con/dictionaries/1.0/",
    pudyn: "http://www.hp.com/schemas/imaging/con/ledm/productusagedyn/2007/12/11",
};

// ---------------------------
// 工具函數
// ---------------------------
function getText(obj) {
    if (!obj || obj.length === 0) return null;
    const text = obj[0];
    return typeof text === 'string' ? text.trim() : null;
}

function toInt(x) {
    if (x === null || x === undefined) return null;
    try {
        return parseInt(parseFloat(x));
    } catch (e) {
        return null;
    }
}

function normalizeModel(s) {
    // 標準化型號字串：小寫、移除非英數（空白、斜線、減號等）
    return s.toLowerCase().replace(/[^a-z0-9]/g, '');
}

async function looksLikeProductUsageDyn(content, debug = false) {
    try {
        const result = await parseStringPromise(content, {
            explicitArray: true,
            preserveChildrenOrder: true
        });
        const rootTag = Object.keys(result)[0];
        const ok = rootTag.endsWith('ProductUsageDyn');
        return ok;
    } catch (e) {
        if (debug) {
            console.log(`[DEBUG] XML parse error: ${e.message}`);
        }
        return false;
    }
}

// ---------------------------
// 解析器（同結構合併）
// ---------------------------
async function M225_M425_M426(xmlContent) {
    // M225dw / M425dn / M426fdn：三個 total
    const result = await parseStringPromise(xmlContent, { explicitArray: true });
    const rootTag = Object.keys(result)[0];
    const root = result[rootTag];

    let printerTotal = null;
    let copyTotal = null;
    let faxTotal = null;

    // 嘗試找到 PrinterSubunit -> TotalImpressions
    if (root['pudyn:PrinterSubunit']) {
        const printerSubunit = root['pudyn:PrinterSubunit'][0];
        if (printerSubunit['dd:TotalImpressions']) {
            printerTotal = getText(printerSubunit['dd:TotalImpressions']);
        }
    }

    // 嘗試找到 CopyApplicationSubunit -> TotalImpressions
    if (root['pudyn:CopyApplicationSubunit']) {
        const copySubunit = root['pudyn:CopyApplicationSubunit'][0];
        if (copySubunit['dd:TotalImpressions']) {
            copyTotal = getText(copySubunit['dd:TotalImpressions']);
        }
    }

    // 嘗試找到 FaxApplicationSubunit -> TotalImpressions
    if (root['pudyn:FaxApplicationSubunit']) {
        const faxSubunit = root['pudyn:FaxApplicationSubunit'][0];
        if (faxSubunit['dd:TotalImpressions']) {
            faxTotal = getText(faxSubunit['dd:TotalImpressions']);
        }
    }

    return {
        printer_total_impressions: toInt(printerTotal),
        copy_total_impressions: toInt(copyTotal),
        fax_total_impressions: toInt(faxTotal),
    };
}

async function CP1525_M251nw_M254dw_M255dw(xmlContent) {
    // CP1525 / CP1525nw / M251nw / M254dw / M255dw：彩機兩值
    const result = await parseStringPromise(xmlContent, { explicitArray: true });
    const rootTag = Object.keys(result)[0];
    const root = result[rootTag];

    let mono = null;
    let color = null;

    if (root['pudyn:PrinterSubunit']) {
        const printerSubunit = root['pudyn:PrinterSubunit'][0];
        if (printerSubunit['dd:MonochromeImpressions']) {
            mono = getText(printerSubunit['dd:MonochromeImpressions']);
        }
        if (printerSubunit['dd:ColorImpressions']) {
            color = getText(printerSubunit['dd:ColorImpressions']);
        }
    }

    return {
        mono_impressions: toInt(mono),
        color_impressions: toInt(color),
    };
}

async function M4103fdn(xmlContent) {
    // 4103fdn：PCL6Impressions 的 TotalImpressions
    const result = await parseStringPromise(xmlContent, { explicitArray: true });
    const rootTag = Object.keys(result)[0];
    const root = result[rootTag];

    let pcl6Total = null;

    // if (root['pudyn:PrinterSubunit']) {
    //     const printerSubunit = root['pudyn:PrinterSubunit'][0];
    //     if (printerSubunit['dd:PCL6Impressions']) {
    //         const pcl6 = printerSubunit['dd:PCL6Impressions'][0];
    //         if (pcl6['dd:TotalImpressions']) {
    //             pcl6Total = getText(pcl6['dd:TotalImpressions']);
    //         }
    //     }
    // }

    if (root['pudyn:PrinterSubunit']) {
        const printerSubunit = root['pudyn:PrinterSubunit'][0];
        if (printerSubunit['dd:TotalImpressions']) {
            pcl6Total = getText(printerSubunit['dd:TotalImpressions']);
        }
    }

    return {
        pcl6_total_impressions: toInt(pcl6Total),
    };
}

// ---------------------------
// 型號字串 -> 解析器
// ---------------------------
const MODEL_KEYWORDS = {
    // M225 / M425 / M426 -> 三 total
    'm225': { name: 'M225_M425_M426', fn: M225_M425_M426 },
    'm225dw': { name: 'M225_M425_M426', fn: M225_M425_M426 },
    'm425': { name: 'M225_M425_M426', fn: M225_M425_M426 },
    'm425dn': { name: 'M225_M425_M426', fn: M225_M425_M426 },
    'm426': { name: 'M225_M425_M426', fn: M225_M425_M426 },
    'm426fdn': { name: 'M225_M425_M426', fn: M225_M425_M426 },

    // CP1525 / CP1525nw / M251nw / M254dw / M255dw -> 彩機兩值
    'cp1525': { name: 'CP1525_M251nw_M254dw_M255dw', fn: CP1525_M251nw_M254dw_M255dw },
    'cp1525nw': { name: 'CP1525_M251nw_M254dw_M255dw', fn: CP1525_M251nw_M254dw_M255dw },
    'm251nw': { name: 'CP1525_M251nw_M254dw_M255dw', fn: CP1525_M251nw_M254dw_M255dw },
    'm254dw': { name: 'CP1525_M251nw_M254dw_M255dw', fn: CP1525_M251nw_M254dw_M255dw },
    'm255dw': { name: 'CP1525_M251nw_M254dw_M255dw', fn: CP1525_M251nw_M254dw_M255dw },

    // 4103fdn -> PCL6 TotalImpressions
    '4103fdn': { name: 'M4103fdn', fn: M4103fdn },
    'm4103fdn': { name: 'M4103fdn', fn: M4103fdn },
    'laserjetpro4103fdn': { name: 'M4103fdn', fn: M4103fdn },
};

function resolveParser(modelStr) {
    if (!modelStr) return { name: null, fn: null };

    const norm = normalizeModel(modelStr);

    // 完全匹配
    if (MODEL_KEYWORDS[norm]) {
        return MODEL_KEYWORDS[norm];
    }

    // Substring 容忍敘述型名稱
    for (const [key, value] of Object.entries(MODEL_KEYWORDS)) {
        if (norm.includes(key)) {
            return value;
        }
    }

    return { name: null, fn: null };
}

// ---------------------------
// HTTP
// ---------------------------
function makeAxiosInstance() {
    return axios.create({
        timeout: 10000,
        httpsAgent: new https.Agent({
            rejectUnauthorized: false, // 自簽憑證環境
        }),
        maxRedirects: 5,
    });
}

async function fetchProductUsageXml(axiosInstance, ip, candidatePaths = null, debug = false, auth = null) {
    candidatePaths = candidatePaths || [
        '/DevMgmt/ProductUsageDyn.xml',
        '/hp/device/ProductUsageDyn.xml',
        '/hp/device/this.Device/ProductUsageDyn.xml',
        '/ProductUsageDyn.xml',
    ];

    const schemes = ['http', 'https'];
    const headers = {
        'Accept': 'application/xml,text/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'nodejs-axios/LEDM-scraper',
    };

    const config = {
        headers,
        validateStatus: () => true, // 接受所有狀態碼
    };

    if (auth) {
        config.auth = {
            username: auth.username,
            password: auth.password,
        };
    }

    for (const scheme of schemes) {
        const base = `${scheme}://${ip}`.replace(/\/$/, '');
        for (const p of candidatePaths) {
            const url = `${base}/${p.replace(/^\//, '')}`;
            try {
                const response = await axiosInstance.get(url, config);

                if (debug) {
                    const ct = response.headers['content-type'] || '';
                    console.log(`[DEBUG] ${response.status} ${ct} ${url}`);
                }

                if (response.status !== 200 || !response.data) {
                    continue;
                }

                const content = typeof response.data === 'string' ?
                    response.data :
                    Buffer.isBuffer(response.data) ?
                    response.data.toString() :
                    JSON.stringify(response.data);

                if (await looksLikeProductUsageDyn(content, debug)) {
                    return content;
                } else {
                    if (debug) {
                        const preview = content.substring(0, 200);
                        console.log(`[DEBUG] not ProductUsageDyn (preview): ${preview}`);
                    }
                }
            } catch (e) {
                if (debug) {
                    console.log(`[DEBUG] request error ${url}: ${e.message}`);
                }
                continue;
            }
        }
    }

    return null;
}

// ---------------------------
// Excel
// ---------------------------
function detectColumns(worksheet) {
    const headers = {};
    const range = xlsx.utils.decode_range(worksheet['!ref']);

    // 讀取第一行作為標題
    for (let C = range.s.c; C <= range.e.c; ++C) {
        const cellAddress = xlsx.utils.encode_cell({ r: range.s.r, c: C });
        const cell = worksheet[cellAddress];
        if (cell && cell.v) {
            headers[C] = cell.v.toString().trim();
        }
    }

    const ipCandidates = ['ip', 'IP', 'Ip', 'host', 'Host'];
    const modelCandidates = ['model', 'Model', '型號', '機型'];
    const userCandidates = ['username', 'Username', 'user', 'User'];
    const passCandidates = ['password', 'Password', 'pass', 'Pass'];

    let ipCol = null;
    let modelCol = null;
    let userCol = null;
    let passCol = null;

    for (const [col, header] of Object.entries(headers)) {
        if (ipCandidates.includes(header)) ipCol = header;
        if (modelCandidates.includes(header)) modelCol = header;
        if (userCandidates.includes(header)) userCol = header;
        if (passCandidates.includes(header)) passCol = header;
    }

    if (!ipCol || !modelCol) {
        const missing = [];
        if (!ipCol) missing.push('IP 欄位（可用 ip/IP/host）');
        if (!modelCol) missing.push('型號欄位（可用 model/型號/機型）');
        throw new Error(`Excel 欄位缺少：${missing.join('、')}`);
    }

    return { ipCol, modelCol, userCol, passCol };
}

async function processExcel(excelPath, outputCsv = 'hp_usage_output.csv', debug = false) {
    const workbook = xlsx.readFile(excelPath);
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];

    const { ipCol, modelCol, userCol, passCol } = detectColumns(worksheet);

    // 轉換為 JSON 格式
    const data = xlsx.utils.sheet_to_json(worksheet);

    const axiosInstance = makeAxiosInstance();
    const rows = [];

    for (let idx = 0; idx < data.length; idx++) {
        const row = data[idx];
        const ip = (row[ipCol] || '').toString().trim();
        const model = (row[modelCol] || '').toString().trim();

        // Optional Basic Auth
        let auth = null;
        if (userCol && passCol) {
            const u = row[userCol];
            const p = row[passCol];
            if (u && p) {
                auth = { username: u.toString(), password: p.toString() };
            }
        }

        const { name: parserName, fn: parserFn } = resolveParser(model);

        const result = {
            host: ip,
            model: model,
            parser_used: parserName,
            printer_total_impressions: null,
            copy_total_impressions: null,
            fax_total_impressions: null,
            mono_impressions: null,
            color_impressions: null,
            pcl6_total_impressions: null,
            status: 'ok',
        };

        if (!parserFn) {
            result.status = 'unknown_model';
            if (debug) {
                console.log(`[DEBUG] row ${idx}: unknown_model -> '${model}'`);
            }
            rows.push(result);
            continue;
        }

        const xmlContent = await fetchProductUsageXml(axiosInstance, ip, null, debug, auth);
        if (!xmlContent) {
            result.status = 'no_xml';
            if (debug) {
                console.log(`[DEBUG] row ${idx}: no_xml for ${ip}`);
            }
            rows.push(result);
            continue;
        }

        try {
            const parsed = await parserFn(xmlContent);
            Object.assign(result, parsed);
        } catch (e) {
            result.status = `parse_error:${e.constructor.name}`;
            if (debug) {
                console.log(`[DEBUG] row ${idx}: parse_error ${e.constructor.name}: ${e.message}`);
            }
        }

        rows.push(result);
    }

    // 寫入 CSV
    const outputWorksheet = xlsx.utils.json_to_sheet(rows);
    const outputWorkbook = xlsx.utils.book_new();
    xlsx.utils.book_append_sheet(outputWorkbook, outputWorksheet, 'Results');
    xlsx.writeFile(outputWorkbook, outputCsv);

    if (debug) {
        console.log(`[DEBUG] wrote ${outputCsv} with ${rows.length} rows`);
    }

    return rows;
}

// ---------------------------
// CLI
// ---------------------------
async function main() {
    const program = new Command();

    program
        .description('Fetch HP LEDM ProductUsageDyn stats')
        .requiredOption('--excel <path>', 'path to printers.xlsx')
        .option('--out <path>', 'output CSV path', 'hp_usage_output.csv')
        .option('--debug', 'enable debug logging', false);

    program.parse(process.argv);
    const options = program.opts();

    try {
        await processExcel(options.excel, options.out, options.debug);
        console.log(`✓ 完成！結果已儲存至 ${options.out}`);
    } catch (error) {
        console.error(`✗ 錯誤: ${error.message}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { processExcel, resolveParser, fetchProductUsageXml };