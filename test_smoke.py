"""qrcode-gen 烟雾测试
验证 4 种用法都能跑通
"""
import subprocess
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
EXE = sys.executable
SCRIPT = str(ROOT / "qrcode_gen.py")

def run(args, expect_ok=True):
    """跑子命令,返回 (returncode, stdout, stderr)"""
    r = subprocess.run([EXE, SCRIPT] + args, capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=30)
    return r.returncode, r.stdout, r.stderr

def test_basic_text():
    """测试 1: 基本文本生成"""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "basic.png")
        rc, out_text, err = run(["Hello World", "-o", out])
        assert rc == 0, f"FAIL: {err}"
        assert os.path.exists(out), "未生成文件"
        assert os.path.getsize(out) > 100, "文件太小"
        # 验证是 PNG
        with open(out, "rb") as f:
            header = f.read(8)
        assert header.startswith(b"\x89PNG"), "不是 PNG 文件"
        print(f"  ✓ test_basic_text: {os.path.getsize(out)} bytes")

def test_url():
    """测试 2: URL"""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "url.png")
        rc, out_text, err = run(["https://github.com/fast1188", "-o", out])
        assert rc == 0, f"FAIL: {err}"
        assert os.path.exists(out)
        print(f"  ✓ test_url: {os.path.getsize(out)} bytes")

def test_vcard_file():
    """测试 3: vCard 文件"""
    with tempfile.TemporaryDirectory() as tmp:
        contact = os.path.join(tmp, "contact.txt")
        out = os.path.join(tmp, "vc.png")
        with open(contact, "w", encoding="utf-8") as f:
            f.write("FN:张三\nORG:测试公司\nTEL:13800138000\nEMAIL:test@example.com\n")
        rc, out_text, err = run(["--vcard", "--vcard-file", contact, "-o", out])
        assert rc == 0, f"FAIL: {err}"
        assert os.path.exists(out)
        print(f"  ✓ test_vcard_file: {os.path.getsize(out)} bytes")

def test_vcard_inline():
    """测试 4: vCard 内联"""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "vc2.png")
        rc, out_text, err = run([
            "--vcard", "--vcard-text", "FN:李四|TEL:13900139000",
            "-o", out
        ])
        assert rc == 0, f"FAIL: {err}"
        assert os.path.exists(out)
        print(f"  ✓ test_vcard_inline: {os.path.getsize(out)} bytes")

def test_batch():
    """测试 5: 批量"""
    with tempfile.TemporaryDirectory() as tmp:
        batch_file = os.path.join(tmp, "urls.txt")
        out_dir = os.path.join(tmp, "out")
        with open(batch_file, "w", encoding="utf-8") as f:
            f.write("# 注释行\n")
            f.write("github:https://github.com\n")
            f.write("gitee:https://gitee.com\n")
            f.write("https://example.com\n")
        rc, out_text, err = run(["--batch", batch_file, "-o", out_dir])
        assert rc == 0, f"FAIL: {err}"
        files = list(Path(out_dir).glob("*.png"))
        assert len(files) == 3, f"期望 3 个文件,实际 {len(files)}"
        print(f"  ✓ test_batch: {len(files)} files in {out_dir}")

def test_error_levels():
    """测试 6: 不同错误纠正等级"""
    with tempfile.TemporaryDirectory() as tmp:
        for ec in ["L", "M", "Q", "H"]:
            out = os.path.join(tmp, f"ec_{ec}.png")
            rc, _, err = run(["Hello", "--ec", ec, "-o", out])
            assert rc == 0, f"FAIL {ec}: {err}"
            assert os.path.exists(out)
        print(f"  ✓ test_error_levels: 4 EC levels (L/M/Q/H) all OK")

def test_custom_colors():
    """测试 7: 自定义颜色"""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "color.png")
        rc, _, err = run(["Hello", "--fill", "red", "--back", "yellow", "-o", out])
        assert rc == 0, f"FAIL: {err}"
        assert os.path.exists(out)
        print(f"  ✓ test_custom_colors: red on yellow")

def test_no_args():
    """测试 8: 无参数应报错"""
    rc, out_text, err = run([])
    # 应当返回非 0(有 error)
    assert rc != 0, "无参数应失败"
    assert "ERROR" in err or "usage" in out_text.lower(), "应有错误提示"
    print(f"  ✓ test_no_args: 正确报错 (rc={rc})")

if __name__ == "__main__":
    # 强制 UTF-8 输出
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 50)
    print("qrcode-gen smoke test")
    print("=" * 50)
    tests = [test_basic_text, test_url, test_vcard_file, test_vcard_inline,
             test_batch, test_error_levels, test_custom_colors, test_no_args]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  FAIL {t.__name__}: EXCEPTION {type(e).__name__}: {e}")
            failed += 1
    print("=" * 50)
    if failed:
        print(f"FAILED: {failed}/{len(tests)}")
        sys.exit(1)
    else:
        print(f"PASS: {len(tests)}/{len(tests)}")
        sys.exit(0)
