#!/bin/python3
import json
import pandas as pd
from os.path import isfile
from config import *
from data_retrieving import *

def json_data_extraction(file_path: str, 
                 columns: list[str], fields: list[str], maps: dict|None=None,
                 save: bool=False) -> pd.DataFrame:
    """
    Extract data from JSON file into a DataFrame.
    
    Parameters
    ----------
    file_path : str
        Path to the JSON file.
    columns : list[str]
        List of column names for the DataFrame.
    fields : list[str]
        List of fields to extract from the JSON records.
        If a field is a list, it will be treated as a path to nested fields.
    maps : dict|None
        Optional dictionnary of functions to apply to specific fields.
        The keys are field names and the values are functions to apply.
        If a field is a list, str(field) will be used as the key.
    save : bool
        Whether to save the processed data to a CSV file.
        Default: False.
    
    Returns
    -------
    pd.DataFrame
        A DataFrame containing the processed data.
    """
    data = []
    with open(file_path, "r") as file:
        for line in file:
            record = json.loads(line.strip())
            row = []
            if 'count' in record:
                assert record['count'] == len(data), "Mismatch in data count"
                continue
            for field in fields:
                if isinstance(field, list):
                    nested_value = record
                    for subfield in field:
                        nested_value = nested_value[subfield]
                    value = nested_value
                else:
                    value = record[field]
                if maps and str(field) in maps:
                    value = maps[str(field)](value)
                row.append(value)
            data.append(row)
    
    df = pd.DataFrame(data, columns=columns).sort_values(by=columns[0])
    df.reset_index(drop=True, inplace=True)
    
    if save:
        name = file_path.replace('.json', '.csv')
        df.copy().to_csv(name, index=False)
        print(f"Saved processed data to {name}")
        
    return df


def transform_probes_history(probes: Probes, save: bool=False) -> pd.DataFrame:
    """
    Transform the probes history data into a DataFrame containing only relevant data.
    
    Parameters
    ----------
    probes : Probes
        A dictionary of probe IDs and their corresponding country and continent.
    save : bool
        Whether to save the processed data to csv file.
    
    Returns
    -------
    pd.DataFrame
        A DataFrame containing the processed probes history.
    """
    file_path = PROBES_HISTORY_FILE(probes)
    if not isfile(file_path):
        start_time, end_time = get_time_range(MEASUREMENT_ID)
        download_probes_history(probes, start_time, end_time)
    columns = ['probe_id', 'ip_address', 'asn', 'status', 'since']
    fields = ['id', 'address_v4', 'asn_v4', ['status', 'name'], ['status', 'since']]
    
    df = json_data_extraction(file_path, columns, fields, save=save)
    
    return df.astype({
        'probe_id': str,
        'ip_address': str,
        'asn': int,
        'status': str,
        'since': int
    })


def transform_measurement(measurement_id: int, save: bool=False) -> pd.DataFrame:
    """
    Transform the measurements data into a DataFrame containing only relevant data.
    
    Parameters
    ----------
    measurement_id : int
        The ID of the measurement to process.
    save : bool
        Whether to save the processed data to a csv file.
    
    Returns:
    --------
    pd.DataFrame
        A DataFrame containing the processed measurements.
    """
    file_path = MEASUREMENT_FILE(measurement_id)
    if not isfile(file_path):
        download_measurement(measurement_id)
    columns = ['probe_id', 'timestamp', 'bent_pipe_latency']
    fields = ['prb_id', 'timestamp', 'result']
    
    def process_result(result: dict) -> list[float|str]:
        """
        Get the bent pipe latency from the result.
        
        Parameters
        ----------
        result : dict
            The result field from the measurement.
        
        Returns
        -------
        float | str
            The mean bent pipe latency in milliseconds, or an error message if not available.
        """
        user = 0
        bent_pipe = 0
        ground = 0
        last_rtt = 0 # to get user latency (hop before starlink gateway)
        for hop in result:
            if 'error' in hop:
                return [f"Error: {hop['error']}"] * 3 
            mean_rtt = 0
            for pkt in hop['result']:
                if 'rtt' in pkt:
                    mean_rtt += pkt['rtt']
            mean_rtt /= len(hop['result'])
            if 'from' in hop['result'][0] and hop['result'][0]['from'] == STARLINK_GATEWAY:
                user = last_rtt
                bent_pipe = mean_rtt - user
            elif hop['hop'] == len(result):
                ground = mean_rtt - user - bent_pipe
            last_rtt = mean_rtt
        
        if bent_pipe == 0:
            return [user, "Startlink gateway not in the path", ground]
            
        return [round(user, 2), round(bent_pipe, 2), round(ground, 2)]

    maps = {'result': process_result}
    
    df = json_data_extraction(file_path, columns, fields, maps=maps, save=False)
    
    # Convert list of latencies to separate columns
    df[['user_latency', 'bent_pipe_latency', 'ground_latency']] = pd.DataFrame(df['bent_pipe_latency'].tolist(), index=df.index)
    
    # Add countryuser and continent information
    df['country'] = df['probe_id'].map(lambda x: PROBES[x][0])
    df['continent'] = df['probe_id'].map(lambda x: PROBES[x][1])
    df = df[['continent', 'country', 'probe_id', 'timestamp', 'user_latency', 'bent_pipe_latency', 'ground_latency']]
    df.sort_values(by=['continent', 'country', 'probe_id', 'timestamp'], inplace=True)
    
    if save:
        name = MEASUREMENT_FILE(measurement_id, ext='csv')
        df.copy().to_csv(name, index=False)
        print(f"Saved processed data to {name}")
    
    return df.astype({
        'continent': str, 
        'country': str,
        'probe_id': int, 
        'timestamp': int,
        'user_latency': str, # because it can be an error message
        'bent_pipe_latency': str,
        'ground_latency': str
        })
    
            
if __name__ == "__main__":
    transform_probes_history(PROBES, save=True)
    transform_measurement(MEASUREMENT_ID, save=True)