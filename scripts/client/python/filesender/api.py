import requests
import filesender.response_types as response
import filesender.request_types as request

def list_my_transfers(base_url: str):
    return requests.get(f"{base_url}/transfer").json()

def describe_transfer(base_url: str, transfer_id: str):
    return requests.get(f"{base_url}/transfer/{transfer_id}").json()

def describe_transfer_options(base_url: str, transfer_id: str):
    return requests.get(f"{base_url}/transfer/{transfer_id}/options").json()

def describe_transfer_audit(base_url: str, transfer_id: str):
    return requests.get(f"{base_url}/transfer/{transfer_id}/auditlog").json()

def email_transfer_audit(base_url: str, transfer_id: str):
    return requests.get(f"{base_url}/transfer/{transfer_id}/auditlog/mail").json()

def send_transfer(
    base_url: str,
    body: request.Transfer
) -> response.Transfer:
    return requests.post(f"{base_url}/transfer", json=body).json()

def upload_chunk(
    base_url: str,
    file_id: str,
    offset: int,
    chunk: bytes
) -> response.File:
    return requests.put(
        f"{base_url}/file/{file_id}/chunk/{offset}",
        data=chunk,
        headers={
            "Content-Type": "application/octet-stream"
        }    
    ).json()

def create_guest(
    base_url: str,
    body: request.Guest
):
    return requests.post(
        f"{base_url}/guest",
        json=body
    ).json()
