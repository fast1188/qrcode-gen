#!/usr/bin/env python3
"""qrcode-gen · 命令行 QR 码生成器
支持:文本/URL/vCard/批量,6 个错误纠正等级,可自定义颜色和尺寸

用法:
  qrcode-gen "https://example.com" -o out.png
  qrcode-gen --text "Hello" --size 10 --ec H -o hi.png
  qrcode-gen --vcard -f contacts.txt -o vc.png
  qrcode-gen --batch urls.txt -o out_dir/
"""
import argparse
import json
import sys
import os
from pathlib import Path

try:
    import qrcode
    from qrcode.constants import (
        ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
    )
except ImportError:
    print("ERROR: 需要 qrcode 库: pip install qrcode[pil]", file=sys.stderr)
    sys.exit(1)

# 错误纠正级别映射
EC_MAP = {
    "L": ERROR_CORRECT_L,  # 7%
    "M": ERROR_CORRECT_M,  # 15%
    "Q": ERROR_CORRECT_Q,  # 25%
    "H": ERROR_CORRECT_H,  # 30%
}


def make_qr(data, ec="M", size=8, border=2, fill="black", back="white"):
    """生成单个 QR 码 PIL Image"""
    qr = qrcode.QRCode(
        version=size,  # 1-40, None=自动
        error_correction=EC_MAP.get(ec.upper(), ERROR_CORRECT_M),
        box_size=10,  # 每点像素
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill, back_color=back)
    return img


def parse_vcard(lines):
    """从 key:value 行解析 vCard 数据,返回字符串"""
    fields = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fields[k.strip().upper()] = v.strip()

    if "FN" not in fields and "NAME" in fields:
        fields["FN"] = fields["NAME"]

    parts = ["BEGIN:VCARD", "VERSION:3.0"]
    if "FN" in fields:
        parts.append(f"FN:{fields['FN']}")
    if "ORG" in fields:
        parts.append(f"ORG:{fields['ORG']}")
    if "TEL" in fields:
        parts.append(f"TEL;TYPE=CELL:{fields['TEL']}")
    if "EMAIL" in fields:
        parts.append(f"EMAIL:{fields['EMAIL']}")
    if "URL" in fields:
        parts.append(f"URL:{fields['URL']}")
    if "NOTE" in fields:
        parts.append(f"NOTE:{fields['NOTE']}")
    parts.append("END:VCARD")
    return "\n".join(parts)


def cmd_text(args):
    """生成单个 QR 码"""
    if args.vcard:
        if args.vcard_file:
            with open(args.vcard_file, "r", encoding="utf-8") as f:
                vcard_text = parse_vcard(f.readlines())
        elif args.vcard_text:
            vcard_text = parse_vcard(args.vcard_text.split("|"))
        else:
            print("ERROR: --vcard needs --vcard-file or --vcard-text", file=sys.stderr)
            return 1
        data = vcard_text
    else:
        data = args.text

    if not data:
        print("ERROR: need --text or --vcard", file=sys.stderr)
        return 1

    img = make_qr(data, ec=args.ec, size=args.version, border=args.border,
                  fill=args.fill, back=args.back)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(out))
        print(f"[OK] Saved: {out} ({img.size[0]}x{img.size[1]})")
    else:
        # 输出到当前目录
        out = Path("qrcode.png")
        img.save(str(out))
        print(f"[OK] Saved: {out.resolve()} ({img.size[0]}x{img.size[1]})")
    return 0


def cmd_batch(args):
    """批量生成:每行一个数据,输出到目录"""
    if not args.batch:
        print("ERROR: --batch needs a file path", file=sys.stderr)
        return 1
    if not os.path.exists(args.batch):
        print(f"ERROR: file not found: {args.batch}", file=sys.stderr)
        return 1

    out_dir = Path(args.output or "qrcode_batch")
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.batch, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    success = 0
    for i, line in enumerate(lines, 1):
        # 支持 name:url 格式
        if ":" in line and not line.startswith("http"):
            name, _, data = line.partition(":")
            name = name.strip().replace(" ", "_")
        else:
            data = line
            name = f"qr_{i:03d}"

        # URL 自动提取
        if data.startswith(("http://", "https://")):
            pass  # 直接用

        try:
            img = make_qr(data, ec=args.ec, size=args.version)
            out_path = out_dir / f"{name}.png"
            img.save(str(out_path))
            print(f"  [{i}/{len(lines)}] {name}.png  ({img.size[0]}x{img.size[1]})  {data[:40]}{'...' if len(data)>40 else ''}")
            success += 1
        except Exception as e:
            print(f"  [{i}/{len(lines)}] FAIL {name}: {e}", file=sys.stderr)

    print(f"\n[OK] {success}/{len(lines)} done -> {out_dir}/")
    return 0 if success == len(lines) else 1


def main():
    p = argparse.ArgumentParser(
        description="qrcode-gen · 命令行 QR 码生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  qrcode-gen "https://github.com" -o gh.png
  qrcode-gen --text "Hello" --ec H --size 5 -o hi.png
  qrcode-gen --vcard --vcard-file contact.txt -o vc.png
  qrcode-gen --batch urls.txt -o ./out/
        """,
    )
    p.add_argument("text", nargs="?", help="QR 内容(文本/URL)")
    p.add_argument("-o", "--output", help="输出文件或目录(默认 qrcode.png)")
    p.add_argument("--ec", choices=["L", "M", "Q", "H"], default="M",
                   help="错误纠正等级(L=7%/M=15%/Q=25%/H=30%, 默认 M)")
    p.add_argument("--size", dest="version", type=int, default=None,
                   help="QR 版本 1-40(默认自动)")
    p.add_argument("--border", type=int, default=2, help="边框宽度(默认 2)")
    p.add_argument("--fill", default="black", help="前景色(默认 black)")
    p.add_argument("--back", default="white", help="背景色(默认 white)")

    # vCard
    p.add_argument("--vcard", action="store_true", help="生成 vCard 格式")
    p.add_argument("--vcard-file", help="vCard 字段文件(每行 KEY:VALUE)")
    p.add_argument("--vcard-text", help="vCard 字段(用 | 分隔,如 FN:张三|TEL:13800138000)")

    # 批量
    p.add_argument("--batch", help="批量模式:每行一个数据,支持 name:url 格式")

    args = p.parse_args()

    if args.batch:
        return cmd_batch(args)
    return cmd_text(args)


if __name__ == "__main__":
    sys.exit(main())
