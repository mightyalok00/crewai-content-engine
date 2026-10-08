import argparse
import sys
from pathlib import Path

# Configure UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from crew import train


def main():
    parser = argparse.ArgumentParser(
        description="Train the CrewAI 9-Agent Studio on sample topics."
    )
    parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=2,
        help="Number of training iterations (default: 2)",
    )
    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        default="trained_agents.pkl",
        help="Output pickle file for trained agents (default: trained_agents.pkl)",
    )
    parser.add_argument(
        "-t",
        "--topic",
        type=str,
        default="AI vs ML vs Data Science",
        help="Training topic (default: 'AI vs ML vs Data Science')",
    )
    parser.add_argument(
        "-c",
        "--channel",
        type=str,
        default="@krishnaik06",
        help="Training target channel / video (default: '@krishnaik06')",
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("🚀 CrewAI Master Studio Training Session")
    print(f"   Iterations: {args.iterations}")
    print(f"   Output:     {args.filename}")
    print(f"   Topic:      {args.topic}")
    print(f"   Channel:    {args.channel}")
    print("=" * 60 + "\n")

    train(
        n_iterations=args.iterations,
        filename=args.filename,
        topic=args.topic,
        channel=args.channel,
    )


if __name__ == "__main__":
    main()
