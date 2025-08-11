#!/bin/python3
from config import *
from data_retrieving import *
from data_transformation import *
from data_analysis import *
from data_visualization import *

if __name__ == "__main__":    
    measurement_info = get_measurement_info(MEASUREMENT_ID)
    start_time, end_time = get_time_range(MEASUREMENT_ID)

    print("Dowloading measurement results...")
    download_measurement(MEASUREMENT_ID)
    print("Downloading probes history...")
    download_probes_history(PROBES, start_time, end_time) 
    print("Data saved into data directory...")   
    
    print("Transforming measurement data...")
    measurement_df = transform_measurement(MEASUREMENT_ID, save=True)
    probes_history_df = transform_probes_history(PROBES, save=True)
    print("Saving transformed data to csv files...")
    
    print("Analyzing probe connection status...")
    connection_analysis_df = probe_connection_analysis(probes_history_df, start_time, end_time)
    plot_probe_connection(connection_analysis_df, save=SAVE_PLOTS, show=SHOW_PLOTS)
    
    print("Analyzing probe PoP IPs...")
    pop_ip_analysis_df = probe_pop_ip_analysis(probes_history_df, save=True)
    
    print("Analyzing segment latency proportions (user <-> Starlink <-> ground)...")
    segment_analysis_df = segment_analysis(measurement_df, save=True)
    
    print("Analyzing bent pipe latency...")
    bent_pipe_analysis_df = bent_pipe_analysis(measurement_df)
    ml = 200  # max latency for cdf plots
    plot_bent_pipe_cdf(bent_pipe_analysis_df, max_latency=ml, save=SAVE_PLOTS, show=SHOW_PLOTS)
    plot_bent_pipe_cdf(bent_pipe_analysis_df, max_latency=ml, group_by='continent', save=SAVE_PLOTS, show=SHOW_PLOTS)
    plot_bent_pipe_cdf(bent_pipe_analysis_df, max_latency=ml, group_by='country', save=SAVE_PLOTS, show=SHOW_PLOTS)
    
    plot_bent_pipe_boxplot(bent_pipe_analysis_df, save=SAVE_PLOTS, show=SHOW_PLOTS)
    plot_bent_pipe_boxplot(bent_pipe_analysis_df, group_by='continent', save=SAVE_PLOTS, show=SHOW_PLOTS)
    plot_bent_pipe_boxplot(bent_pipe_analysis_df, group_by='country', save=SAVE_PLOTS, show=SHOW_PLOTS)
    
    if PLOT_INDIVIDUAL_PROBES:
        print("Plotting individual probe bent pipe latency...")
        for id in PROBES:
            p = {id: PROBES[id]}
            plot_bent_pipe_latency(bent_pipe_analysis_df, probes=p, save=SAVE_PLOTS, show=SHOW_PLOTS)
            plot_bent_pipe_histogram(bent_pipe_analysis_df, probes=p, save=SAVE_PLOTS, show=SHOW_PLOTS)
            plot_bent_pipe_cdf(bent_pipe_analysis_df, probes=p, save=SAVE_PLOTS, show=SHOW_PLOTS)
         
    print("All analyses completed.")
    if SAVE_PLOTS:
        print("All plots saved to 'plots' directory.")