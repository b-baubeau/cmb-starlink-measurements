#!/bin/python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from config import *
from data_retrieving import *
from data_transformation import *
from data_analysis import *

def plot_probe_connection(analysis: pd.DataFrame, 
                          save=False, show=True) -> None:
    """
    Plot the connection status of probes over a specified time period.
    
    Parameters
    ----------
    analysis : pd.DataFrame
        DataFrame containing probe connection analysis data.
    save : bool
        Whether to save the plot to a file.
    show : bool
        Whether to display the plot.
    
    Returns
    -------
    None
        The function displays the plot and optionally saves it to a file.
    """
    df = analysis.copy()
    df['probe_id'] = df['probe_id'].astype(str) # make probe_id as string for better plotting
    # Sort by connection time for better visualization
    df = df.sort_values(by=['starlink', 'other', 'disconnected'], ascending=False)
    
    plt.figure(figsize=FIG_SIZE)
    
    # Plot stacked bar chart
    plt.bar(df['probe_id'], df['starlink'], label='Starlink', color='blue', alpha=0.6)
    plt.bar(df['probe_id'], df['other'], bottom=df['starlink'], label='Other', color='orange', alpha=0.6)
    plt.bar(df['probe_id'], df['disconnected'], bottom=df['starlink'] + df['other'], label='Disconnected', color='red', alpha=0.6)
    
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
        
    if save:
        name = PROBE_CONNECTION_FILE(PROBES, ext='png')
        plt.savefig(name)
        print(f"Plot saved as '{name}'")
    
    if show:
        plt.show()
    plt.close()
 

def plot_bent_pipe_latency(analysis: pd.DataFrame, 
                           max_latency: int|None=None, probes: Probes|None=None, 
                           save=False, show=True) -> None:
    """
    Plot the bent pipe latency for each probe in the measurement data.
    
    Parameters
    ----------
    analysis : pd.DataFrame
        DataFrame containing bent pipe latency analysis data.
    max_latency : int|None
        Optional maximum latency value to limit the values. If None, no limit is applied.
    probes : Probes|None
        Optional dictionary of probes to limit the y-axis. If None, all probes are included.
    save : bool
        Whether to save the plot to a file.
    show : bool
        Whether to display the plot.
    
    Returns
    -------
    None
        The function displays the plot and optionally saves it to a file.
    """
    df = analysis.copy()
    if probes is not None:
        df = df[df['probe_id'].isin(probes.keys())]
    if df is None or df.empty:
        print("No data available for the specified probes.")
        return
    
    plt.figure(figsize=FIG_SIZE)
    for probe_id in df['probe_id'].unique():
        probe_data = df[df['probe_id'] == probe_id]
        probe_data.sort_values(by='timestamp', inplace=True)
        sizes = [1] * probe_data.shape[0]  # Default size for scatter points
        plt.scatter(probe_data['timestamp'], probe_data['bent_pipe_latency'], 
                    sizes=sizes, label=f'Probe {probe_id}')
    
    if probes is not None:
        plt.legend() # else too much data to show
    plt.xticks(rotation=45)
    plt.ylim(bottom=0)
    if max_latency is not None:
        plt.ylim(top=min(max_latency, df['bent_pipe_latency'].max()*1.1))

    plt.tight_layout()
    
    if save:
        name = BENT_PIPE_FILE(probes if probes is not None else PROBES,
                              type='latency', group_by=None, ext='png')
        plt.savefig(name)
        print(f"Plot saved as '{name}'")
    
    if show:
        plt.show()
    plt.close()


def plot_bent_pipe_histogram(analysis: pd.DataFrame, 
                             max_latency: int|None=None, probes: Probes|None=None, 
                             save=False, show=True) -> None:
    """
    Plot a histogram of bent pipe latency for each probe in the measurement data.
    
    Parameters
    ----------
    analysis : pd.DataFrame
        DataFrame containing bent pipe latency analysis data.
    max_latency : int|None
        Optional maximum latency value to limit the x-axis. If None, no limit is applied.
    probes : Probes|None
        Optional dictionary of probes to filter the measurement data. If None, all probes are included.
    save : bool
        Whether to save the plot to a file.
    show : bool
        Whether to display the plot.
    
    Returns
    -------
    None
        The function displays the plot and optionally saves it to a file.
    """
    df = analysis.copy()
    if probes is not None:
        df = df[df['probe_id'].isin(probes)]
    if df is None or df.empty:
        print("No data available for the specified probes.")
        return
    
    plt.figure(figsize=FIG_SIZE)
    
    # Distribution histogram with bins of 1ms
    bins = [i for i in range(0, int(df['bent_pipe_latency'].max()) + 2)]
    for probe_id in df['probe_id'].unique():
        probe_data = df[df['probe_id'] == probe_id]
        plt.hist(probe_data['bent_pipe_latency'], bins=bins, density=True,
                 alpha=0.5, label=f'Probe {probe_id}')
    
    if probes is not None:
        plt.legend() # else too much data to show
    plt.xlim(left=0)
    if max_latency is not None:
        plt.xlim(right=min(max_latency, df['bent_pipe_latency'].max()))
    plt.tight_layout()
    
    if save:
        name = BENT_PIPE_FILE(probes if probes is not None else PROBES,
                              type='histogram', group_by=None, ext='png')
        plt.savefig(name)
        print(f"Plot saved as '{name}'")
    
    if show:
        plt.show()
    plt.close()


def plot_bent_pipe_cdf(analysis: pd.DataFrame, 
                       max_latency: int|None=None, probes: Probes|None=None,
                       group_by: str|None=None, 
                       save=False, show=True) -> None:
    """
    Plot the cumulative distribution function (CDF) of bent pipe latency for each probe.
    
    Parameters
    ----------
    analysis : pd.DataFrame
        DataFrame containing bent pipe latency analysis data.
    probes : Probes|None
        Optional dictionary of probes to filter the measurement data. If None, all probes are included.
    max_latency : int|None
        Optional maximum latency value to limit the x-axis. If None, no limit is applied.
    save : bool
        Whether to save the plot to a file.
    
    Returns
    -------
    None
        The function displays the plot and optionally saves it to a file.
    """
    df = analysis.copy()
    if probes is not None:
        df = df[df['probe_id'].isin(probes)]
    if df is None or df.empty:
        print("No data available for the specified probes.")
        return
    
    plt.figure(figsize=FIG_SIZE)
    
    key = 'probe_id' if group_by is None else group_by
    
    for value in df[key].unique():
        probe_data = df[df[key] == value]
        sorted_data = probe_data['bent_pipe_latency'].sort_values()
        cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
        
        label = f'Probe {value}' if group_by is None else f'{value}'
        plt.plot(sorted_data, cdf, label=label)
    
    if probes is not None or group_by is not None:
        plt.legend() # else too much data to show
    plt.xlim(left=0)
    if max_latency is not None:
        plt.xlim(right=min(max_latency, df['bent_pipe_latency'].max()))
    plt.tight_layout()
    
    if save:
        name = BENT_PIPE_FILE(probes if probes is not None else PROBES,
                              type='cdf', group_by=group_by, ext='png')
        plt.savefig(name)
        print(f"Plot saved as '{name}'")
    
    if show:
        plt.show()
    plt.close()


def plot_bent_pipe_boxplot(analysis: pd.DataFrame, 
                          max_latency: int|None=None, probes: Probes|None=None,
                          group_by: str|None=None,
                          save=False, show=True) -> None:
    """
    Plot a boxplot of bent pipe latency for each probe in the measurement data.
    
    Parameters
    ----------
    analysis : pd.DataFrame
        DataFrame containing bent pipe latency analysis data.
    probes : Probes|None
        Optional dictionary of probes to filter the measurement data. If None, all probes are included.
    max_latency : int|None
        Optional maximum latency value to limit the y-axis. If None, no limit is applied.
    save : bool
        Whether to save the plot to a file.
    show : bool
        Whether to display the plot.
    
    Returns
    -------
    None
        The function displays the plot and optionally saves it to a file.
    """
    df = analysis.copy()
    if probes is not None:
        df = df[df['probe_id'].isin(probes)]
    if df is None or df.empty:
        print("No data available for the specified probes.")
        return
    
    plt.figure(figsize=FIG_SIZE)
    
    boxprops = dict(facecolor='lightgrey', color='black')
    medianprops = dict(color='red', linewidth=2)
    whiskerprops = dict(color='black')
    by = group_by if group_by is not None else 'probe_id'
    df = df[[by, 'bent_pipe_latency']]
    df.boxplot(by=by, grid=False, showfliers=False, patch_artist=True,
               boxprops=boxprops, medianprops=medianprops, whiskerprops=whiskerprops)
    
    plt.title('')
    plt.suptitle('')
    plt.xlabel('')
    plt.xticks(rotation=45)
    plt.ylim(bottom=0)
    if max_latency is not None:
        plt.ylim(top=min(max_latency, df['bent_pipe_latency'].max()*1.1))
    plt.tight_layout()
    
    if save:
        name = BENT_PIPE_FILE(probes if probes is not None else PROBES,
                              type='boxplot', group_by=group_by, ext='png')
        plt.savefig(name)
        print(f"Plot saved as '{name}'")
    
    if show:
        plt.show()
    plt.close()


if __name__ == "__main__":        
    measurement_df = transform_measurement(MEASUREMENT_ID, save=True)
    probes_history_df = transform_probes_history(PROBES, save=True)
    start_time, end_time = get_time_range(MEASUREMENT_ID)
    
    connection_analysis_df = probe_connection_analysis(probes_history_df, start_time, end_time)
    plot_probe_connection(connection_analysis_df, save=SAVE_PLOTS, show=SHOW_PLOTS)
    
    bent_pipe_analysis_df = bent_pipe_analysis(measurement_df)
    ml = 200  # max latency for cdf plots
    plot_bent_pipe_cdf(bent_pipe_analysis_df, max_latency=ml, save=SAVE_PLOTS, show=SHOW_PLOTS)
    plot_bent_pipe_cdf(bent_pipe_analysis_df, max_latency=ml, group_by='continent', save=SAVE_PLOTS, show=SHOW_PLOTS)
    plot_bent_pipe_cdf(bent_pipe_analysis_df, max_latency=ml, group_by='country', save=SAVE_PLOTS, show=SHOW_PLOTS)
    
    plot_bent_pipe_boxplot(bent_pipe_analysis_df, save=SAVE_PLOTS, show=SHOW_PLOTS)
    plot_bent_pipe_boxplot(bent_pipe_analysis_df, group_by='continent', save=SAVE_PLOTS, show=SHOW_PLOTS)
    plot_bent_pipe_boxplot(bent_pipe_analysis_df, group_by='country', save=SAVE_PLOTS, show=SHOW_PLOTS)
    
    if PLOT_INDIVIDUAL_PROBES:
        for id in PROBES:
            p = {id: PROBES[id]}
            plot_bent_pipe_latency(bent_pipe_analysis_df, probes=p, save=SAVE_PLOTS, show=SHOW_PLOTS)
            plot_bent_pipe_histogram(bent_pipe_analysis_df, probes=p, save=SAVE_PLOTS, show=SHOW_PLOTS)
            plot_bent_pipe_cdf(bent_pipe_analysis_df, probes=p, save=SAVE_PLOTS, show=SHOW_PLOTS)