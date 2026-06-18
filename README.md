# qrcode-gen

> 命令行 QR 码生成器 · Python 单文件 · 4 个 EC 等级 · 支持 vCard/批量

## 特性

- ✅ **单文件零配置**：`pip install qrcode[pil]` 后即可用
- 🎨 **6 种输入**：文本 / URL / vCard 文件 / vCard 内联 / 批量
- 🔧 **4 个错误纠正等级**：L(7%)/M(15%)/Q(25%)/H(30%)
- 🎨 **自定义颜色**：前景色 + 背景色任意
- 📦 **批量生成**：每行一个 + name:url 格式
- 🧪 **自带 smoke 测试**：8 个测试用例

## 安装

```bash
pip install qrcode[pil]
```

## 快速使用

### 1. 基本文本/URL
```bash
python qrcode_gen.py "Hello World" -o out.png
python qrcode_gen.py "https://github.com" -o gh.png
```

### 2. 高错误纠正 (30% 损坏可还原)
```bash
python qrcode_gen.py "Hello" --ec H -o hi.png
```

### 3. 自定义颜色
```bash
python qrcode_gen.py "Hello" --fill red --back yellow -o color.png
```

### 4. vCard 联系人
```bash
# 方式 A: 文件
cat contact.txt
# FN:张三
# ORG:测试公司
# TEL:13800138000
# EMAIL:zhang@example.com

python qrcode_gen.py --vcard --vcard-file contact.txt -o vc.png

# 方式 B: 内联(用 | 分隔)
python qrcode_gen.py --vcard --vcard-text "FN:李四|TEL:13900139000" -o vc2.png
```

### 5. 批量生成
```bash
# urls.txt 格式:每行一个,支持 name:url
cat urls.txt
# github:https://github.com
# gitee:https://gitee.com
# https://example.com

python qrcode_gen.py --batch urls.txt -o ./out/
# 输出:
#   [1/3] github.png  (330x330)  https://github.com
#   [2/3] gitee.png  (330x330)  https://gitee.com
#   [3/3] qr_003.png  (330x330)  https://example.com
# ✓ 完成 3/3 → ./out/
```

## 完整参数

```
python qrcode_gen.py --help
```

| 参数 | 说明 | 默认 |
|------|------|------|
| `text` | QR 内容(文本/URL) | - |
| `-o / --output` | 输出文件/目录 | `qrcode.png` |
| `--ec` | 错误纠正 L/M/Q/H | M |
| `--size` | QR 版本 1-40 | 自动 |
| `--border` | 边框宽度 | 2 |
| `--fill` | 前景色 | black |
| `--back` | 背景色 | white |
| `--vcard` | vCard 模式 | - |
| `--vcard-file` | vCard 文件 | - |
| `--vcard-text` | vCard 内联 | - |
| `--batch` | 批量文件 | - |

## 测试

```bash
python test_smoke.py
```

8 个测试用例覆盖：基本文本/URL/vCard 文件/vCard 内联/批量/EC 等级/颜色/错误处理。

## 应用场景

- 📱 公众号/小程序推广二维码
- 👤 联系人 vCard 分享
- 🌐 网站 URL 分享
- 📋 WiFi 密码分享
- 🎫 活动入场凭证
- 📦 商品溯源码

## 技术栈

- Python 3.8+
- [qrcode](https://github.com/lincolnloop/python-qrcode) 库
- PIL/Pillow

## License

MIT

## 仓库地址

- GitHub: https://github.com/fast1188/qrcode-gen
- Gitee: https://gitee.com/wudijia2026/qrcode-gen

## 维护

属于 30 天 60 个开源软件计划 · 2026-06-19 发布
