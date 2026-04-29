#!/usr/bin/env python3
"""Parse raw data from stdin, merge with existing CSVs and HTML files."""
import re, sys, os

MAX_DAYS = 120  # 只保留最近 120 天数据

BASE = "/Users/mac/ws/tools/successrate"

def parse_raw(text):
    charge, withdraw = {}, {}
    cur_date = cur_currency = mode = None
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        dm = re.match(r'^Date:\s*([\d-]+)', line)
        if dm: cur_date = dm.group(1); mode = None; continue
        cm = re.match(r'^Currency:\s*(\w+)', line)
        if cm: cur_currency = cm.group(1); mode = 'charge'; continue
        if '[charge] total num:' in line: mode = 'withdraw'; continue
        if '[withdraw] total num:' in line: mode = None; continue
        pm = re.match(r'^(\S+):\s*(\d+)(?:/([\d.]+))?', line)
        if pm and cur_date and cur_currency and mode:
            target = charge if mode == 'charge' else withdraw
            target.setdefault(cur_currency, {}).setdefault(cur_date, []).append(
                (pm.group(1), int(pm.group(2)), pm.group(3) or ''))
    return charge, withdraw

def merge_csv(filename, cur, data):
    fp = os.path.join(BASE, filename)
    existing = open(fp).readlines() if os.path.exists(fp) else []
    header = existing[0] if existing else "Date,Provider,Num,Rate\n"
    
    # Parse existing rows into {date: [row_strings]}
    existing_data = {}
    for r in existing[1:]:
        r = r.strip()
        if not r: continue
        d = r.split(',')[0]
        existing_data.setdefault(d, []).append(r + '\n')
    
    # Add new data
    added = 0
    for d in sorted(data.get(cur, {}).keys()):
        if d in existing_data: continue  # skip existing dates
        rows = []
        for prov, num, rate in data[cur][d]:
            rows.append(f"{d},{prov},{num},{rate}\n")
        existing_data[d] = rows
        added += len(rows)
    
    # Trim to MAX_DAYS
    all_sorted = sorted(existing_data.keys())
    trimmed = 0
    if len(all_sorted) > MAX_DAYS:
        for d in all_sorted[:len(all_sorted) - MAX_DAYS]:
            trimmed += len(existing_data.pop(d))
    
    # Write sorted
    with open(fp, 'w') as f:
        f.write(header)
        for d in sorted(existing_data.keys()):
            f.writelines(existing_data[d])
    
    dates_range = sorted(existing_data.keys())
    print(f"  {filename}: +{added} rows, -{trimmed} trimmed, {len(existing_data)} dates ({dates_range[0]}~{dates_range[-1]})")

def update_html(html_file, cur, charge):
    fp = os.path.join(BASE, html_file)
    content = open(fp).read()
    existing_dates = sorted(set(re.findall(r'Date:\s*([\d-]+)', content)))
    
    new_dates = sorted([d for d in charge.get(cur, {}).keys() if d not in existing_dates])
    
    # Build blocks for new dates and insert them at correct positions
    # Rebuild entire rawData block
    all_dates_data = {}
    # Parse existing rawData
    rawdata_match = re.search(r'const rawData = `(.*?)`;', content, re.DOTALL)
    if rawdata_match:
        raw_text = rawdata_match.group(1)
        cur_d = None
        for line in raw_text.split('\n'):
            line_s = line.strip() if line.strip() else ''
            dm = re.match(r'^Date:\s*([\d-]+)', line_s)
            if dm:
                cur_d = dm.group(1)
                all_dates_data[cur_d] = [line]
                continue
            if cur_d:
                all_dates_data[cur_d].append(line)
    
    # Add new dates
    for d in new_dates:
        lines = [f"Date: {d}", f" Currency: {cur}"]
        for prov, num, rate in charge[cur][d]:
            lines.append(f" {prov}: {num}/{rate}" if rate else f" {prov}: {num}")
        total = sum(n for _,n,_ in charge[cur][d])
        lines.append(f" [charge] total num: {total}")
        lines.append("")
        all_dates_data[d] = lines
    
    # Trim to MAX_DAYS
    all_sorted = sorted(all_dates_data.keys())
    trimmed = 0
    if len(all_sorted) > MAX_DAYS:
        for d in all_sorted[:len(all_sorted) - MAX_DAYS]:
            del all_dates_data[d]
            trimmed += 1
    
    # Rebuild rawData
    new_rawdata = ""
    for d in sorted(all_dates_data.keys()):
        new_rawdata += '\n'.join(all_dates_data[d]) + '\n'
    new_rawdata = new_rawdata.rstrip() 
    
    content = re.sub(r'const rawData = `.*?`;', f'const rawData = `{new_rawdata}`;', content, flags=re.DOTALL)
    
    all_d = sorted(all_dates_data.keys())
    content = re.sub(r'(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})', f"{all_d[0]} ~ {all_d[-1]}", content)
    
    open(fp, 'w').write(content)
    print(f"  {html_file}: +{len(new_dates)}, -{trimmed} trimmed, total: {len(all_d)} ({all_d[0]}~{all_d[-1]})")

raw = sys.stdin.read()
charge, withdraw = parse_raw(raw)
print("Parsed:", {c: len(d) for c,d in charge.items()})

print("\nCSVs:")
for cur, pfx in [('BDT','bdt'),('BRL','brl'),('IDR','idr'),('PHP','php')]:
    merge_csv(f"charge_{pfx}.csv", cur, charge)
    merge_csv(f"withdraw_{pfx}.csv", cur, withdraw)

print("\nHTML:")
for cur, html in [('BDT','bdt_charge_chart.html'),('BRL','brl_charge_chart.html'),('IDR','idr_charge_chart.html'),('PHP','php_charge_chart.html')]:
    update_html(html, cur, charge)
print("\nDone!")
