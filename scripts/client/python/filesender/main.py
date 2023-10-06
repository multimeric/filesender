from typing import List, Optional, Tuple
from typing_extensions import Annotated, TypeVar
from filesender.api import create_guest, create_transfer, update_transfer, upload_chunk, update_file, get_server_info
import filesender.request_types as request
from typer import Typer, Option, Argument
from rich import print
from pathlib import Path
from configparser import ConfigParser

OptionStr = Annotated[str, Option()]

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

context = {
    "default_map": get_defaults()
}
app = Typer()

# BaseUrl = Annotated[str, Option(default_factory=lambda: get_config_parser().get("system", "base_url"))]
# DefaultTransferDaysValid = Annotated[int, Option(default_factory=lambda: get_config_parser().getint("system", "base_url", fallback=10))]
# UserName = Annotated[str, Option(default_factory=lambda: get_config_parser().get("user", "username", fallback=None))]
# ApiKey = Annotated[str, Option(default_factory=lambda: get_config_parser().get("user", "apikey", fallback=None))]

@app.command(context_settings=context)
def invite(base_url: OptionStr, username: OptionStr, apikey: OptionStr, recipient: OptionStr):
    body: request.Guest = {
        "from": username,
        "recipient": recipient
    }
    print(create_guest(
        base_url=base_url,
        user_name=username,
        api_key=apikey,
        body=body,
    ))

@app.command(context_settings=context)
def upload(files: Annotated[List[Path], Argument(file_okay=True, dir_okay=False, resolve_path=True, exists=True)], base_url: OptionStr, username: OptionStr, apikey: OptionStr, recipients: Annotated[List[str], Option()]):
    info = get_server_info(base_url)
    files_by_name = {
        path.name: path for path in files
    }

    transfer = create_transfer(
        base_url=base_url,
        api_key=apikey,
        user_name=username,
        body={
            "files": [{
                "name": file.name,
                "size": file.stat().st_size
            } for file in files],
            "from": username,
            "recipients": recipients
        }
    )
    for file in transfer["files"]:
        with files_by_name[file["name"]].open("rb") as fp:
            upload_chunk(
                file_id=file["id"],
                api_key=apikey,
                base_url=base_url,
                user_name=username,
                chunk=fp,
                offset=0
            )
            update_file(
                file_id=file["id"],
                api_key=apikey,
                base_url=base_url,
                user_name=username,
                body={
                    "complete": True
                }
            )

            
    transfer = update_transfer(
        base_url=base_url,
        user_name=username,
        api_key=apikey,
        transfer_id=transfer["id"],
        body={
            "complete": True
        }
    )
    print(transfer)

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
