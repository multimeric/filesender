import requests
import filesender.response_types as response
import filesender.request_types as request
from requests import Request, Response, HTTPError
import hashlib
import hmac
import time
from typing_extensions import Self, TypedDict, Unpack
from urllib.parse import urlparse, urlunparse, unquote
from io import IOBase
from contextlib import contextmanager

def raise_status(response: Response):
    try:
        response.raise_for_status()
    except HTTPError as e:
        raise Exception(f"Request failed with content {e.response.json()}")

class CommonArgs(TypedDict):
    base_url: str

class SignatureArgs(TypedDict):
    api_key: str
    user_name: str

class CommonAndSignature(CommonArgs, SignatureArgs):
    pass

class FileSenderRequest(Request):
    def url_without_scheme(self) -> str:
        """
        Returns the URL in the appropriate format for the signature calculation, namely:
        • Without a scheme
        • Without URL encoding
        • With query parameters
        """
        return unquote(urlunparse(urlparse(self.prepare().url)._replace(scheme="")).lstrip("/"))

    def sign(self, **kwargs: Unpack[SignatureArgs]) -> Self:
        """
        Signs the request by calculating and adding appropriate query parameters
        """
        self.params.update(
            remote_user = kwargs["user_name"],
            timestamp = str(round(time.time()))
        ) 
        signature = hmac.new(
            key=kwargs["api_key"].encode(),
            digestmod=hashlib.sha1
        )
        signature.update(self.method.lower().encode())
        signature.update(b"&")
        signature.update(self.url_without_scheme().encode())
        signature.update(b"&")

        prepared = self.prepare()
        if prepared.body is None:
            pass
        elif isinstance(prepared.body, str):
            signature.update(prepared.body.encode())
        elif isinstance(prepared.body, bytes):
            signature.update(prepared.body)
        elif isinstance(prepared.body, IOBase):
            while True:
                chunk = prepared.body.read(1024)
                if not chunk:
                    break
                signature.update(chunk.encode())
            prepared.body.seek(0)
        else:
            raise Exception("Unknown body type")

        self.params["signature"] = signature.hexdigest()
        return self

    def send(self, **kwargs) -> Response:
        """
        Shortcut for sending the request, raising if the request fails
        """
        with requests.Session() as session:
            response = session.send(self.prepare(), **kwargs)
            raise_status(response)
            return response

def list_my_transfers(base_url: str):
    return requests.get(f"{base_url}/transfer").json()

def describe_transfer(base_url: str, transfer_id: str):
    return requests.get(f"{base_url}/transfer/{transfer_id}").json()

def create_transfer(
    body: request.Transfer,
    **kwargs: Unpack[CommonAndSignature]
) -> response.Transfer:
    return FileSenderRequest(
        "POST",
        f"{kwargs['base_url']}/transfer",
        json=body,
    ).sign(**kwargs).send().json()

def update_transfer(
    transfer_id: int,
    body: request.TransferUpdate,
    **kwargs: Unpack[CommonAndSignature]
) -> response.Transfer:
    return FileSenderRequest(
        "PUT",
        f"{kwargs['base_url']}/transfer/{transfer_id}",
        json=body,
    ).sign(**kwargs).send().json()

def update_file(
    file_id: int,
    body: request.FileUpdate,
    **kwargs: Unpack[CommonAndSignature]
):
    return FileSenderRequest(
        "PUT",
        f"{kwargs['base_url']}/file/{file_id}",
        json=body,
    ).sign(**kwargs).send().json()

def upload_chunk(
    file_id: int,
    offset: int,
    chunk: IOBase,
    **kwargs: Unpack[CommonAndSignature]
) -> response.File:
    data = chunk.read()
    return FileSenderRequest(
        "PUT",
        f"{kwargs['base_url']}/file/{file_id}/chunk/{offset}",
        data=data,
        headers={
            "Content-Type": 'application/octet-stream',
            "X-Filesender-File-Size": str(len(data)),
            "X-Filesender-Chunk-Offset": str(0),
            "X-Filesender-Chunk-Size": str(len(data))
        },
    ).sign(**kwargs).send(timeout=10).json()
    

def create_guest(
    body: request.Guest,
    **kwargs: Unpack[CommonAndSignature]
) -> response.Guest:
    return FileSenderRequest(
        "POST",
        f"{kwargs['base_url']}/guest",
        json=body
    ).sign(**kwargs).send().json()

def get_server_info(base_url: str) -> dict:
    return FileSenderRequest(
        "GET",
        f"{base_url}/info",
    ).send().json()
