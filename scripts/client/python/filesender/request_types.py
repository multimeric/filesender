from typing import List
from typing_extensions import TypedDict, NotRequired

class File(TypedDict):
    name: str
    size: int
    mime_type: str
    cid: str

Transfer = TypedDict("Transfer", {
    "files": List[File],
    "recipients": List[str],
    "options": List[str],
    "expires": NotRequired[int],
    "from": str,
    "subject": NotRequired[str],
    "message": NotRequired[str]
})

Guest = TypedDict("Guest", {
    "recipient": str,
    "from": str,
    "subject": NotRequired[str],
    "message": NotRequired[str],
    "options": NotRequired[List[str]],
    "transfer_options": NotRequired[List[str]],
    "expires": NotRequired[int]
})
