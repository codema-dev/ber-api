from pathlib import Path
from typing import Dict

import requests
from tqdm import tqdm
from tqdm.std import Comparable

import ber_api

HERE = Path(__file__).parent
BerForm = Dict[str, Dict[str, str]]


def _download_file_from_response(
    response: requests.Response, filepath: str, tqdm_bar: Comparable = tqdm
) -> None:
    """Download file to filepath via a HTTP response from a POST or GET request.

    Args:
        response (requests.Response): A HTTP response from a POST or GET request
        filepath (str): Save path destination for downloaded file
        tqdm_bar (Comparable): Progress bar (either tqdm or stqdm)
    """
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kilobyte
    progress_bar = tqdm_bar(total=total_size_in_bytes, unit="iB", unit_scale=True)
    with open(filepath, "wb") as save_destination:
        for stream_data in response.iter_content(block_size):
            progress_bar.update(len(stream_data))
            save_destination.write(stream_data)
    progress_bar.close()


def _login_to_portal(
    session: requests.Session, email_address: str, form_data: BerForm
) -> None:
    response = session.post(
        url="https://ndber.seai.ie/BERResearchTool/Register/Register.aspx",
        headers=form_data["headers"],
        data=form_data["login"],
    )
    response.raise_for_status()
    if "not registered" in str(response.content):
        raise ValueError(
            f"{email_address} does not have access to the BER Public"
            f" search database, please login to {email_address} and"
            " respond to your registration email and try again."
        )


def _request_all_data(session: requests.Session, form_data: BerForm, savepath: Path):
    with session.post(
        url="https://ndber.seai.ie/BERResearchTool/ber/search.aspx",
        headers=form_data["headers"],
        data=form_data["download_all_data"],
        stream=True,
    ) as response:
        response.raise_for_status()
        _download_file_from_response(response, savepath)


def request_public_ber_db(
    email_address: str,
    savedir: str = Path.cwd(),
    form_data: BerForm = ber_api.DEFAULTS,
    tqdm_bar: Comparable = tqdm,
) -> None:
    """Login & Download BERPublicsearch.zip.

    Args:
        email_address (str): Your Email address
        savedir (str): Save directory for data
        tqdm_bar (Comparable): Progress bar (either tqdm or stqdm)
    """
    savepath = Path(savedir) / "BERPublicsearch.zip"
    form_data["login"]["ctl00$DefaultContent$Register$dfRegister$Name"] = email_address
    with requests.Session() as session:
        _login_to_portal(
            session=session, email_address=email_address, form_data=form_data
        )
        _request_all_data(
            session=session, form_data=form_data, savepath=savepath, tqdm_bar=tqdm_bar
        )
