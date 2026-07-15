"""
Variance calculator for multi-line 835 ERA underpayment analysis.

Accepts service line data via --lines (JSON) or --csv, computes per-line and
total variance, flags sequestration (CO-253/OA-23) as non-disputable, and
applies multiple-procedure reduction checks.

Usage:
    python compute_variance.py --lines '[{"cpt":"27447","billed":42500,"expected":38750,"paid":31200,"carc":"CO-45"},...]'
    python compute_variance.py --csv service_lines.csv
    python compute_variance.py --demo
"""

import argparse
import csv
import io
import json
import sys

NON_DISPUTABLE_CARCS = {"OA-23", "CO-253"}
MPR_CARCS = {"CO-97"}


def parse_lines_json(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON for --lines: {e}", file=sys.stderr)
        sys.exit(1)


def parse_lines_csv(path):
    lines = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lines.append({
                "cpt": row.get("cpt", ""),
                "description": row.get("description", ""),
                "billed": float(row["billed"]),
                "expected": float(row["expected"]),
                "paid": float(row["paid"]),
                "carc": row.get("carc", ""),
                "rarc": row.get("rarc", ""),
                "modifier": row.get("modifier", ""),
            })
    return lines


def demo_lines():
    return [
        {"cpt": "27447", "description": "Total knee arthroplasty", "billed": 42500.00, "expected": 38750.00, "paid": 31200.00, "carc": "CO-45", "rarc": "", "modifier": ""},
        {"cpt": "20610", "description": "Arthrocentesis, major joint", "billed": 520.00, "expected": 260.00, "paid": 130.00, "carc": "CO-97", "rarc": "", "modifier": "-51"},
        {"cpt": "99213", "description": "Office visit, established patient", "billed": 180.00, "expected": 95.00, "paid": 92.10, "carc": "OA-23", "rarc": "", "modifier": ""},
    ]


def analyze(lines):
    results = []
    for sl in lines:
        billed = float(sl["billed"])
        expected = float(sl["expected"])
        paid = float(sl["paid"])
        carc = sl.get("carc", "").strip()
        variance = expected - paid
        variance_pct = (variance / expected * 100) if expected else 0.0

        non_disputable = carc.upper() in {c.upper() for c in NON_DISPUTABLE_CARCS}
        mpr = carc.upper() in {c.upper() for c in MPR_CARCS}

        if variance < 0:
            status = "OVERPAYMENT"
            disputable = False
        elif non_disputable:
            status = "NON-DISPUTABLE"
            disputable = False
        elif variance < 25:
            status = "BELOW THRESHOLD"
            disputable = False
        elif 25 <= variance <= 100:
            status = "PURSUE IF PATTERN"
            disputable = True
        else:
            status = "PURSUE"
            disputable = True

        results.append({
            "cpt": sl.get("cpt", ""),
            "description": sl.get("description", ""),
            "billed": billed,
            "expected": expected,
            "paid": paid,
            "variance": variance,
            "variance_pct": variance_pct,
            "carc": carc,
            "rarc": sl.get("rarc", ""),
            "modifier": sl.get("modifier", ""),
            "mpr_flag": mpr,
            "status": status,
            "disputable": disputable,
        })
    return results


def summarize(results):
    total_billed = sum(r["billed"] for r in results)
    total_expected = sum(r["expected"] for r in results)
    total_paid = sum(r["paid"] for r in results)
    total_variance = sum(r["variance"] for r in results)
    disputable_variance = sum(r["variance"] for r in results if r["disputable"])
    total_variance_pct = (total_variance / total_expected * 100) if total_expected else 0.0
    return {
        "total_billed": total_billed,
        "total_expected": total_expected,
        "total_paid": total_paid,
        "total_variance": total_variance,
        "total_variance_pct": total_variance_pct,
        "disputable_variance": disputable_variance,
        "line_count": len(results),
        "disputable_count": sum(1 for r in results if r["disputable"]),
    }


def print_report(results, summary):
    sep = "-" * 90
    print(sep)
    print(f"{'CPT':<8} {'Description':<32} {'Expected':>10} {'Paid':>10} {'Variance':>10} {'%':>6}  Status")
    print(sep)
    for r in results:
        desc = (r["description"][:30] + "..") if len(r["description"]) > 32 else r["description"]
        flags = ""
        if r["mpr_flag"]:
            flags += " [MPR]"
        if r["modifier"]:
            flags += f" [{r['modifier']}]"
        print(
            f"{r['cpt']:<8} {desc:<32} ${r['expected']:>9,.2f} ${r['paid']:>9,.2f} "
            f"${r['variance']:>9,.2f} {r['variance_pct']:>5.1f}%  {r['status']}{flags}"
        )
        if r["carc"]:
            print(f"         CARC: {r['carc']}" + (f"  RARC: {r['rarc']}" if r["rarc"] else ""))
    print(sep)
    print(f"{'TOTAL':<8} {'':<32} ${summary['total_expected']:>9,.2f} ${summary['total_paid']:>9,.2f} "
          f"${summary['total_variance']:>9,.2f} {summary['total_variance_pct']:>5.1f}%")
    print(sep)
    print(f"\nService lines: {summary['line_count']}  |  Disputable: {summary['disputable_count']}  |  "
          f"Disputable variance: ${summary['disputable_variance']:,.2f}")

    mpr_lines = [r for r in results if r["mpr_flag"]]
    if mpr_lines:
        print(f"\n⚠  MPR (CO-97) lines detected — verify reduction % and whether modifier -59 applies:")
        for r in mpr_lines:
            print(f"   CPT {r['cpt']}: paid ${r['paid']:,.2f} vs expected ${r['expected']:,.2f} — confirm 50% reduction is correct")

    non_disp = [r for r in results if r["status"] == "NON-DISPUTABLE"]
    if non_disp:
        print(f"\n⚠  Non-disputable lines (sequestration) — do NOT include in dispute letter:")
        for r in non_disp:
            print(f"   CPT {r['cpt']}: ${r['variance']:,.2f} variance (CARC {r['carc']}) — mandatory, not an error")


def main():
    parser = argparse.ArgumentParser(
        description="Compute per-line and total variance for 835 ERA underpayment analysis."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--lines",
        metavar="JSON",
        help='JSON array of service lines: [{"cpt","billed","expected","paid","carc","rarc","modifier","description"},...]',
    )
    group.add_argument(
        "--csv",
        metavar="FILE",
        help="CSV file with columns: cpt, description, billed, expected, paid, carc, rarc, modifier",
    )
    group.add_argument(
        "--demo",
        action="store_true",
        help="Run with built-in demo data (3-line claim with CO-45, CO-97, and sequestration)",
    )
    parser.add_argument(
        "--json-out",
        action="store_true",
        help="Output results as JSON instead of human-readable report",
    )
    args = parser.parse_args()

    if args.demo:
        lines = demo_lines()
    elif args.lines:
        lines = parse_lines_json(args.lines)
    else:
        lines = parse_lines_csv(args.csv)

    if not lines:
        print("ERROR: No service lines provided.", file=sys.stderr)
        sys.exit(1)

    results = analyze(lines)
    summary = summarize(results)

    if args.json_out:
        print(json.dumps({"lines": results, "summary": summary}, indent=2))
    else:
        print_report(results, summary)


if __name__ == "__main__":
    main()
