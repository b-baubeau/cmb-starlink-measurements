# Connected mobility basics course - Assignment 3 - Group 4 repository

## Requirements

The libraries needed to run this project are listed in ```requirements.txt```. You can install them quickly by running:
```bash
pip install -r requirements.txt
```

## Code structure

The code is separated in 5 files:

- ```config```, which is used to store common variable for the other files,
- ```data_retrieving```, which uses the RIPE Atlas API to retrieve the results of the measurement and the history of the probes connections,
- ```data_transformation```, which takes the raw JSON data and extract relevant data into a Pandas DataFrame to be able to analyse it more easily. It also save the DataFrame as a CSV file as an intermediary representation to be able to look into the data manually,
- ```data_analysis```, which takes the transformed data and manipulate it to extract relevant metrics,
- ```data_visualization```, which takes plots the relevant metrics.

## Running the data processing pipeline

To run the full data processing pipeline, run ```PYTHONPATH=src python3 run.py```. If you want to only run part of the pipeline, you can run the corresponding file. It will run the previous data processing steps needed to carry its role.

```config.py``` contains parameters usefull to control the processing pipeline, such as wether to show plots during the process and wheter to save them or not.
