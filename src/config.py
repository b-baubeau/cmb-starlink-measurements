"""Global configuration settings."""

# Constants for the Starlink measurement system
MEASUREMENT_ID = 113897643
# 'probes' field in measurement info is empty, so we use a hardcoded list of probes
PROBES = [54866, 1008318, 51475, 60323, 22802, 
          1000295, 64532, 1001130, 61435, 26201,
          1007637, 60929, 1011163, 32686, 1009606,
          60812, 1010025, 51593, 17889, 1007645]
STARLINK_GATEWAY = "100.64.0.1"

# File paths
DATA_DIR = "data/"
def MEASUREMENT_FILE(measurement_id: int) -> str:
    """Return the file path for a specific measurement."""
    return f"{DATA_DIR}measurement_{measurement_id}.json"
def PROBES_HISTORY_FILE(probes: list[int]) -> str:
    """Return the file path for the probes history."""
    return f"{DATA_DIR}probes_history_{probes[0]}_to_{probes[-1]}.json"