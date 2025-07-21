#!/bin/python3
import pandas as pd
from config import *
from data_retrieving import *
from data_transformation import *

def probe_connection_analysis(probe_history: pd.DataFrame, start_time: int, end_time: int) -> pd.DataFrame:
    """
    Analyze probe connection over a specified time period.
    The connection is split into 3 categories: 
    - connected to starlink
    - connected to another network
    - disconnected
    
    Parameters
    ----------
    probe_history : pd.DataFrame
        DataFrame containing probe history data.
    start_time : int
        Start time of the analysis period in Unix timestamp.
    end_time : int
        End time of the analysis period in Unix timestamp.
    
    Returns
    -------
    pd.DataFrame
        A DataFrame summarizing probe availability statistics.
    """
    columns = ['probe_id', 'starlink', 'other', 'disconnected']
    data = []
    for probe_id in probe_history['probe_id'].unique():
        probe_data = probe_history[probe_history['probe_id'] == probe_id]
        probe_data = probe_data.sort_values(by='since')
        # filter data within the specified time range
        probe_data['until'] = probe_data['since'].shift(-1, fill_value=end_time)
        probe_data = probe_data[(probe_data['since'] < end_time) & (probe_data['until'] > start_time)]
        # adjust start and end times
        probe_data['since'] = probe_data['since'].clip(lower=start_time)
        probe_data['until'] = probe_data['until'].clip(upper=end_time)
        
        disconnected_time = 0
        starlink_time = 0
        other_time = 0
        for _, row in probe_data.iterrows():
            if row['status'] == 'Connected':
                if row['asn'] == STARLINK_ASN:
                    starlink_time += (row['until'] - row['since'])
                else:
                    other_time += (row['until'] - row['since'])
            elif row['status'] == 'Disconnected':
                disconnected_time += (row['until'] - row['since'])
        
        data.append([probe_id, starlink_time, other_time, disconnected_time])
        
    df = pd.DataFrame(data, columns=columns)
    df['starlink'] = df['starlink'].apply(lambda x: x / (end_time - start_time))
    df['other'] = df['other'].apply(lambda x: x / (end_time - start_time))
    df['disconnected'] = df['disconnected'].apply(lambda x: x / (end_time - start_time))
    
    return df

def probe_pop_ip_analysis(probe_history: pd.DataFrame, save=False) -> pd.DataFrame:
    """
    Analyze the pop IP addresses of probes.
    
    Parameters
    ----------
    probe_history : pd.DataFrame
        DataFrame containing probe history data.
    
    Returns
    -------
    pd.DataFrame
        A DataFrame summarizing the PoP IP addresses used by each probe.
    """
    probe_pop_ips = probe_history[probe_history['status'] == 'Connected'] # Filter only connected probes
    probe_pop_ips = probe_pop_ips[probe_pop_ips['asn'] == STARLINK_ASN] # Filter only Starlink probes
    probe_pop_ips = probe_pop_ips.drop_duplicates(subset=['probe_id', 'ip_address']) # Keep only unique probe_id and ip_address pairs
    
    probe_pop_ips = probe_pop_ips.groupby('probe_id')['ip_address'].apply(lambda x: ','.join(x)).reset_index()
    probe_pop_ips.columns = ['probe_id', 'pop_ips']
    
    if save:
        # Suppress "" for better readability (one ip per line) 
        with open(f"{PLOT_DIR}probe_pop_ips.csv", 'w') as f:
            f.write(probe_pop_ips.to_csv(index=False).replace('"', ''))
        print("Probe PoP IP analysis saved to 'probe_pop_ips.csv'")
    
    return probe_pop_ips

def bent_pipe_analysis(measurement_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze the bent pipe data from the measurement.
    
    Parameters
    ----------
    measurement_df : pd.DataFrame
        DataFrame containing measurement data.
    probe_history : pd.DataFrame
        DataFrame containing probe history data.
    
    Returns
    -------
    pd.DataFrame
        A DataFrame summarizing the bent pipe analysis.
    """
    df = measurement_df.copy()
    
    # Filtering
    n = df.shape[0]
    # errors='coerce' will convert non-numeric to NaN -> filter errors
    df['bent_pipe_latency'] = pd.to_numeric(df['bent_pipe_latency'], errors='coerce')
    df = df[df['bent_pipe_latency'].notna()]
    print(f"Filtered {n - df.shape[0]} rows with missing of invalid data.")
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    
    df.reset_index(drop=True, inplace=True)
    
    return df.astype({
        'continent': str,
        'country': str,
        'probe_id': int,
        'timestamp': 'datetime64[ns]',
        'bent_pipe_latency': float
    })

if __name__ == "__main__":
    measurement_info = get_measurement_info(MEASUREMENT_ID)
    start_time = measurement_info['start_time']
    end_time = measurement_info['stop_time']
    probes_history_df = transform_probes_history(PROBES, save=True)
    measurement_df = transform_measurement(MEASUREMENT_ID, save=True)
    
    connection_analysis_df = probe_connection_analysis(probes_history_df, start_time, end_time)
    print("Probe Connection Analysis:")
    print(connection_analysis_df)
    
    pop_ip_analysis_df = probe_pop_ip_analysis(probes_history_df, save=True)
    print("\nProbe PoP IP Analysis:")
    print(pop_ip_analysis_df)
        
    bent_pipe_analysis_df = bent_pipe_analysis(measurement_df)
    print("\nBent Pipe Analysis:")
    bent_pipe_analysis_df = bent_pipe_analysis_df[bent_pipe_analysis_df['probe_id'] == 51475]  # Filter out non-positive latencies
    print(bent_pipe_analysis_df.head())