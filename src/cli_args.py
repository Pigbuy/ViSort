import argparse

def build_parser():
    parser = argparse.ArgumentParser(description="Image processing pipeline")

    # config
    parser.add_argument(
        "-c", "--config-location",
        default="config.toml",
        help="Path to config file (default: config.toml)"
    )
    parser.add_argument(
        "-l", "--locationiq_key",
        default="",
        help="LocationIQ secret key"
    )
    parser.add_argument(
        "-o", "--openai_key",
        default="",
        help="openai secret key"
    )
    parser.add_argument(
        "-r", "--max_simultaneous_llm_requests",
        default=3,
        help="max amount of llm requests to be sent at once so ollama doesn't get overloaded"
    )
    args = parser.parse_args()

    return args

args = build_parser()