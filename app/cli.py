"""Command-line entry point for running AvaNegar."""

import argparse

import uvicorn


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="avanegar",
        description="Run the AvaNegar Persian transcription web application.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind to.")
    parser.add_argument("--port", default=8000, type=int, help="Port to listen on.")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Reload the server when source files change.",
    )
    return parser


def main() -> None:
    args = create_parser().parse_args()
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()

