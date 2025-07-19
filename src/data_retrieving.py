#!/bin/python3
import requests
from datetime import datetime
from config import MEASUREMENT_FILE, PROBES_HISTORY_FILE

def unix_time_to_iso8601(unix_time: int) -> str:
    """
    Convert Unix timestamp to ISO 8601 format.
    
    Parameters
    ----------
    unix_time : int
        The Unix timestamp to convert (seconds since epoch).
    
    Returns
    -------
    str
        The ISO 8601 formatted date string (e.g., "2023-10-01T12:00:00Z").
    """
    return datetime.fromtimestamp(unix_time).isoformat() + 'Z'


def get_measurement_info(measurement_id: int) -> dict:
    """
    Fetch measurement information from Ripe Atlas API.
    
    Parameters
    ----------
    measurement_id : int
        The ID of the measurement to fetch.
    
    Returns
    -------
    dict
        A dictionary containing measurement information.
    """
    url = f"https://atlas.ripe.net/api/v2/measurements/{measurement_id}/"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch measurement info. Status code: {response.status_code}")


def download_measurement(measurement_id: int) -> None:
    """
    Use Ripe Atlas API to download all measurement results by its ID.
    
    Parameters
    ----------
    measurement_id : int
        The ID of the measurement to download.
    start_time : int
        The start time of the measurement in Unix timestamp.
    end_time : int
        The end time of the measurement in Unix timestamp.
    
    Returns
    -------
    None
        The function saves the measurement data to a file.
    """
    measurement_info = get_measurement_info(measurement_id)
    start_time = measurement_info['start_time']
    end_time = measurement_info['stop_time']
    
    url = f"https://atlas.ripe.net/api/v2/measurements/{measurement_id}/results/?start={start_time}&stop={end_time}&format=txt"
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(MEASUREMENT_FILE(measurement_id), "w") as file:
            file.write(response.text)
        print(f"Measurement {measurement_id} downloaded successfully.")
    else:
        print(f"Failed to download measurement {measurement_id}. Status code: {response.status_code}")


def download_probes_history(probes: list[int], start_time: int, end_time: int) -> None:
    """
    Use Ripe Atlas API to download probes history by their IDs.
    
    Parameters
    ----------
    probes : list[int]
        A list of probe IDs to download history for.
    
    Returns
    -------
    None
        The function saves the probes history to a file.
    """
    url = "https://atlas.ripe.net/api/v2/probes/archive/"
    params = {
        "probe": ",".join(map(str, probes)),
        "date__gte": unix_time_to_iso8601(start_time).split('T')[0],
        "date__lte": unix_time_to_iso8601(end_time).split('T')[0],
        "format": "txt"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        with open(PROBES_HISTORY_FILE(probes), "w") as file:
            file.write(response.text)
        print(f"Probes history downloaded successfully.")
    else:
        print(f"Failed to download probes history. Status code: {response.status_code}")
    

if __name__ == "__main__":
    from config import MEASUREMENT_ID, PROBES
    measurement_info = get_measurement_info(MEASUREMENT_ID)
    print(f"Measurement Info: {measurement_info}")
    print("Download measurement results? (Y/n): ", end="")
    if input().strip().lower() != 'y':
        download_measurement(MEASUREMENT_ID)
    print("Download probes history? (Y/n): ", end="")
    if input().strip().lower() != 'y':
        download_probes_history(PROBES, measurement_info['start_time'], measurement_info['stop_time'])