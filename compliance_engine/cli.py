"""CLI 入口：audit / list-rules / demo。

示例：
  python -m compliance_engine audit --type contract --input 合同.txt --output 报告.html
  python -m compliance_engine audit --type regulation --input 制度.txt --format json
  python -m compliance_engine list-rules --type contract
  python -m compliance_engine demo
"""

import argparse
import sys
from pathlib import Path

from .engine import ComplianceEngine
from .models import DocType
from .report import to_html, to_json, to_markdown


def _read_input(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"输入文件不存在: {p}")
    return p.read_text(encoding="utf-8")


def _write_output(path: str, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")
    print(f"报告已写入: {path}")


def cmd_audit(args: argparse.Namespace) -> int:
    text = _read_input(args.input)
    doc_type = DocType.from_str(args.type)
    engine = ComplianceEngine(rules_dir=Path(args.rules_dir) if args.rules_dir else None)
    report = engine.audit(text, doc_type, title=args.title or Path(args.input).stem)

    fmt = args.format
    if args.output:
        fmt = fmt or ("html" if args.output.endswith(".html") else "json")
    fmt = fmt or "html"

    if fmt == "json":
        content = to_json(report)
    elif fmt == "md":
        content = to_markdown(report)
    else:
        content = to_html(report)

    if args.output:
        _write_output(args.output, content)
    else:
        print(content)
    return 0


def cmd_list_rules(args: argparse.Namespace) -> int:
    engine = ComplianceEngine(rules_dir=Path(args.rules_dir) if args.rules_dir else None)
    doc_type = DocType.from_str(args.type) if args.type else None
    rules = engine.rule_engine.list_rules(doc_type)
    for r in rules:
        print(
            f"{r['id']:<16} [{r.get('scope','generic'):<12}] {r.get('severity','WARNING'):<8} "
            f"{r.get('category','')} — {r.get('message','')}"
        )
    print(f"\n共 {len(rules)} 条规则")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    from .demo import run_demo

    out_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    run_demo(out_dir, doc_type=DocType.from_str(args.type) if args.type else None)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="compliance_engine",
        description="企业级文书合规审计引擎（纯规则库，零依赖，可离线）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_audit = sub.add_parser("audit", help="审计一份文书")
    p_audit.add_argument("--type", required=True, choices=[t.value for t in DocType],
                         help="文书类型")
    p_audit.add_argument("--input", required=True, help="输入文书文件路径（UTF-8）")
    p_audit.add_argument("--title", default="", help="文书标题（默认取文件名）")
    p_audit.add_argument("--format", choices=["html", "json", "md"], default=None,
                         help="输出格式（默认 html；指定 --output 时按扩展名推断）")
    p_audit.add_argument("--output", default="", help="输出文件路径")
    p_audit.add_argument("--rules-dir", default="", help="自定义规则目录")
    p_audit.set_defaults(func=cmd_audit)

    p_list = sub.add_parser("list-rules", help="列出规则库")
    p_list.add_argument("--type", default="", choices=[t.value for t in DocType],
                        help="按类型过滤")
    p_list.add_argument("--rules-dir", default="", help="自定义规则目录")
    p_list.set_defaults(func=cmd_list_rules)

    p_demo = sub.add_parser("demo", help="运行内置演示（生成示例报告）")
    p_demo.add_argument("--type", default="", choices=[t.value for t in DocType],
                        help="仅演示指定类型")
    p_demo.add_argument("--output-dir", default="", help="报告输出目录（默认当前目录）")
    p_demo.set_defaults(func=cmd_demo)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
