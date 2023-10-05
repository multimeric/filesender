import click
from typing import List, Optional, Tuple
from typing_extensions import Annotated, TypeVar
from filesender.config import ConfigFileProcessor
from filesender.api import create_guest
import filesender.request_types as request
from typer import Typer, Option, Argument
from rich import print
from typer_config import ini_loader, use_config, conf_callback_factory
from typer_config.loaders import loader_transformer
from pathlib import Path
from configparser import ConfigParser
from functools import cache

OptionStr = Annotated[str, Option()]

def sign_request() -> dict:
    

def get_defaults() -> dict:
    defaults = {}
    path = Path.home() / ".filesender" / "filesender.py.ini"
    if path.exists():
        parser = ConfigParser()
        parser.read(path)
        if parser.has_option("system", "base_url"):
            defaults["base_url"] = parser.get("system", "base_url")
        if parser.has_option("system", "default_transfer_days_valid"):
            defaults["default_transfer_days_valid"] = parser.get("system", "default_transfer_days_valid")
        if parser.has_option("user", "username"):
            defaults["username"] = parser.get("user", "username")
        if parser.has_option("user", "apikey"):
            defaults["apikey"] = parser.get("user", "apikey")

    return defaults

app = Typer(context_settings={
    "default_map": get_defaults()
})

# BaseUrl = Annotated[str, Option(default_factory=lambda: get_config_parser().get("system", "base_url"))]
# DefaultTransferDaysValid = Annotated[int, Option(default_factory=lambda: get_config_parser().getint("system", "base_url", fallback=10))]
# UserName = Annotated[str, Option(default_factory=lambda: get_config_parser().get("user", "username", fallback=None))]
# ApiKey = Annotated[str, Option(default_factory=lambda: get_config_parser().get("user", "apikey", fallback=None))]

@app.command()
def invite_guest(base_url: OptionStr, username: OptionStr, recipient: OptionStr):
    body: request.Guest = {
        "from": username,
        "recipient": recipient
    }
    print(create_guest(base_url, body))

# @main.command(context_settings={"default_map": ConfigFileProcessor.read_config()})
# @click.argument("files", type=click.Path(exists=True), nargs=-1)
# @verbose
# @insecure
# @progress
# @click.option("-s", "--subject")
# @click.option("-m", "--message")
# @click.option("--threads", type=int)
# @click.option("--timeout", type=int)
# @click.option("--retries", type=int)
# @click.option("-u", "--username")
# @click.option("-a", "--apikey")
# @click.option("-r", "--recipients", required=True)
# @click.option("-f", "--from_address", help="filesender email from address", required=True)
# def upload(files: List[str], verbose: bool, insecure: bool, progress: bool, subject: str, message: str, guest: bool, threads: int, timeout: int, retries: int, username: str, apikey: str, recipients: str, from_address: str):
#     pass

# @main.command()
# def download():
#     pass

if __name__ == "__main__":
    app()
