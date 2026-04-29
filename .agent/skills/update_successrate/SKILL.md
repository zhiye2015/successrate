---
name: update_successrate
description: 追加支付成功率数据到 CSV 和 HTML 图表，并部署到 Netlify
---

# 支付成功率数据追加 & 部署流程

## 📌 概述

将用户提供的支付渠道成功率原始数据，追加到 CSV 文件和 HTML 趋势图表中，然后部署到 Netlify。

**支持币种**: BDT, BRL, IDR, PHP  
**项目目录**: `/Users/mac/ws/tools/successrate/`  
**数据保留**: 最近 **120 天**（脚本自动裁剪超出的旧数据）  
**线上地址**: https://idrchargechart.netlify.app/  
**Netlify Site ID**: `bf7e3d36-3b33-45c2-a7db-712231ba0895`

---

## 📥 输入格式

用户粘贴的原始数据格式如下（每天一个 Date 块，包含 charge 和 withdraw 两部分）：

```
Date: 2026-04-15
 Currency: BDT
 s_bdt_zenithpay: 175/73.14      # provider名: 订单数/成功率
     s_bdt_gtpay: 17/76.92
     s_bdt_gopay: 6/100.00
 s_bdt_starpagopay: 5/20.00
  s_bdt_tigerpay: 3/33.33
   s_bdt_axispay: 1/100.00       # 无成功率表示数据不可用
 [charge] total num: 207          # 充值总单数

 s_bdt_zenithpay: 81/100.00
 [withdraw] total num: 81         # 提现总单数

 Currency: BRL
 ...（继续其他币种）
```

> **重点**: `[charge] total num` 之前的是**充值数据**，之后到 `[withdraw] total num` 之间是**提现数据**。

---

## 📂 文件结构

### CSV 文件（8 个）
| 文件名 | 说明 |
|--------|------|
| `charge_bdt.csv` | BDT 充值数据 |
| `charge_brl.csv` | BRL 充值数据 |
| `charge_idr.csv` | IDR 充值数据 |
| `charge_php.csv` | PHP 充值数据 |
| `withdraw_bdt.csv` | BDT 提现数据 |
| `withdraw_brl.csv` | BRL 提现数据 |
| `withdraw_idr.csv` | IDR 提现数据 |
| `withdraw_php.csv` | PHP 提现数据 |

**CSV 格式**:
```csv
Date,Provider,Num,Rate
2026-04-15,s_bdt_zenithpay,175,73.14
2026-04-15,s_bdt_gtpay,17,76.92
```
- 按日期升序排列
- Rate 字段为空表示无成功率（只有订单数、成功率未统计到）

### HTML 图表（5 个）
| 文件名 | 说明 |
|--------|------|
| `index.html` | 首页导航（4 个币种卡片入口） |
| `bdt_charge_chart.html` | BDT 充值趋势图 |
| `brl_charge_chart.html` | BRL 充值趋势图 |
| `idr_charge_chart.html` | IDR 充值趋势图 |
| `php_charge_chart.html` | PHP 充值趋势图 |

每个子页面顶部和底部有**上翻页/下翻页**导航按钮，顺序为：  
`IDR → BDT → BRL → PHP`（首尾链接到首页）

### 模板参考
- `example/brl_charge_chart.html` - 作为新建图表时的模板

---

## 🔧 操作步骤

### 第一步：解析数据 & 更新文件

1. **保存原始数据**到 `/tmp/raw_data.txt`

2. **运行解析脚本**（在项目根目录下执行）：
   ```bash
   python3 .agent/skills/update_successrate/scripts/build_csvs.py < /tmp/raw_data.txt
   ```

3. **脚本功能**:
   - 解析原始数据 → 按币种分拆
   - **合并**到现有 CSV（跳过已存在的日期、按日期排序）
   - **合并**到 HTML 图表的 `rawData` 模板字符串（跳过已有日期）
   - 更新 HTML 标题中的日期范围
   - 自动裁剪超过 120 天的旧数据

### 第二步：部署到 Netlify

```bash
bash .agent/skills/update_successrate/scripts/deploy_netlify.sh
```

**脚本功能**：
- 将 5 个 HTML 文件（index + 4 个图表）打包为 zip
- 通过 Netlify API 部署到 `idrchargechart.netlify.app`
- 打印部署结果和各页面 URL

---

## ⚠️ 注意事项

1. **不要推送到 GitHub** - 用户明确表示不需要自动推送
2. **日期去重** - 脚本会自动跳过已存在的日期，不会重复插入
3. **数据裁剪** - 超过 120 天的旧数据会被自动删除
4. **新 Provider 颜色** - 如果原始数据中出现了新的 Provider（之前不在 HTML 的 `colors` 对象中），需要手动在 HTML 的 `colors` 对象中添加颜色映射
5. **问题通道分组** - HTML 中的 `groups.problem` 数组定义了"问题通道"，新增的问题通道需要手动更新
6. **CSV 按日期升序** - 所有 CSV 行按日期从早到晚排列
7. **HTML 图表仅包含充值数据** - 提现数据只存 CSV，不进图表
8. **导航按钮** - 各子页面有上翻页/下翻页按钮，链接到相邻币种页面，新增页面时需要同步更新导航
9. **Netlify Token** - 部署脚本使用 `NETLIFY_TOKEN` 环境变量，或使用内置的默认 token
