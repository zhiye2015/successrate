---
description: 更新支付成功率数据并部署到 Netlify
---

# /update_successrate 工作流

将用户提供的支付成功率原始数据追加到 CSV 和 HTML 图表，然后部署到 Netlify 线上。

## 🔴 必读前置文档

执行前必须先阅读 Skill 文档：
- `.agent/skills/update_successrate/SKILL.md`

## 前提条件

- 用户提供了原始支付数据（包含 Date / Currency / Provider 等字段）
- 所有命令在项目目录 `/Users/mac/ws/tools/successrate/` 下执行

---

## 步骤

### 1. 保存原始数据

将用户粘贴的原始数据保存到临时文件：

```bash
cat > /tmp/raw_data.txt << 'RAWEOF'
<用户粘贴的原始数据>
RAWEOF
```

### 2. 运行解析脚本，更新 CSV + HTML

// turbo
```bash
python3 .agent/skills/update_successrate/scripts/build_csvs.py < /tmp/raw_data.txt
```

**验证输出**：
- 确认每个币种都有 `+N rows` 或 `+N dates` 的输出
- 确认没有 error 报错
- 如果所有币种都显示 `no new dates`，说明数据已存在，无需更新

### 3. 部署到 Netlify

// turbo
```bash
bash .agent/skills/update_successrate/scripts/deploy_netlify.sh
```

**验证输出**：
- 确认显示 `✅ Deploy successful!`
- 确认显示线上 URL: `https://idrchargechart.netlify.app/`

### 4. 报告结果

向用户汇报：
1. 各币种新增了多少天的数据
2. 是否有数据被裁剪（超过 35 天）
3. 线上可访问地址：https://idrchargechart.netlify.app/
4. 各子页面链接
