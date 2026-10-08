from __future__ import annotations

import argparse

from .runner import evaluate_file

def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a generated CrewAI content package")
    parser.add_argument("content", help="Markdown article to evaluate")
    parser.add_argument("--verification", help="VerificationReport JSON file")
    parser.add_argument("--output", help="Write JSON evaluation report to this file")
    parser.add_argument("--minimum-score", type=float, default=0.80)
    args = parser.parse_args()
    report = evaluate_file(args.content, args.verification, args.output, minimum_score=args.minimum_score)
    print(f"overall={report.overall:.3f} passed={report.passed}")
    for name, score in report.scores.items():
        print(f"{name}={score:.3f}")
    if report.notes:
        print("notes=" + ",".join(report.notes))
    return 0 if report.passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
