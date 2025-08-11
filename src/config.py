"""Global configuration settings."""

# --- Measurement constants ---
MEASUREMENT_ID = 113897643
STARLINK_ASN = 14593
STARLINK_GATEWAY = "100.64.0.1"

# --- Output settings ---
FIG_SIZE = (6, 4)
SHOW_PLOTS = False  # Show plots in the output
SAVE_PLOTS = True  # Save plots to files
PLOT_INDIVIDUAL_PROBES = True  # Plot data for individual probes

# --- Constants for Continents ---
AFRICA = "Africa"
OCEANIA = "Oceania"
SOUTH_AMERICA = "South America"
NORTH_AMERICA = "North America"
EUROPE = "Europe"

# --- Constants for Countries ---
BENIN = "Benin"
CAMEROON = "Cameroon"
AUSTRALIA = "Australia"
COLOMBIA = "Colombia"
CHILE = "Chile"
CANADA = "Canada"
USA = "USA"
GERMANY = "Germany"
FRANCE = "France"
HUNGARY = "Hungary"
UK = "UK"
SPAIN = "Spain"

# --- List of Probes ---
Probes = dict[int, tuple[str, str]]  # for type hinting
PROBES = {
    60812: (BENIN, AFRICA),
    17889: (CAMEROON, AFRICA),
    1011163: (AUSTRALIA, OCEANIA),
    1001130: (COLOMBIA, SOUTH_AMERICA),
    1007645: (CHILE, SOUTH_AMERICA),
    61435: (CANADA, NORTH_AMERICA),
    1009606: (CANADA, NORTH_AMERICA),
    26201: (CANADA, NORTH_AMERICA),
    22802: (USA, NORTH_AMERICA),
    60929: (USA, NORTH_AMERICA),
    64532: (USA, NORTH_AMERICA),
    1008318: (USA, NORTH_AMERICA),
    51593: (GERMANY, EUROPE),
    60323: (GERMANY, EUROPE),
    1000295: (GERMANY, EUROPE),
    32686: (FRANCE, EUROPE),
    1010025: (HUNGARY, EUROPE),
    51475: (UK, EUROPE),
    54866: (UK, EUROPE),
    1007637: (SPAIN, EUROPE)
}

# --- File paths ---
DATA_DIR = "data/"
PLOT_DIR = "plots/"
def MEASUREMENT_FILE(measurement_id: int, ext: str="json") -> str:
    """Return the file path for a specific measurement."""
    return f"{DATA_DIR}measurement_{measurement_id}.{ext}"
def PROBES_HISTORY_FILE(probes: Probes, ext: str="json") -> str:
    """Return the file path for the probes history."""
    if len(probes) == 1:
        return f"{DATA_DIR}probes_history_{list(probes.keys())[0]}.{ext}"
    return f"{DATA_DIR}probes_history_{min(probes.keys())}_to_{max(probes.keys())}.{ext}"
def PROBE_CONNECTION_FILE(probes: Probes, ext: str="csv") -> str:
    """Return the file path for the probe connection analysis."""
    dir = DATA_DIR if ext == "csv" else PLOT_DIR
    if len(probes) == 1:
        return f"{dir}probe_connection_{list(probes.keys())[0]}.{ext}"
    return f"{dir}probe_connection_{min(probes.keys())}_to_{max(probes.keys())}.{ext}"
def PROBE_POP_IPS_FILE(probes: Probes, ext: str="csv") -> str:
    """Return the file path for the probe PoP IPs analysis."""
    dir = DATA_DIR if ext == "csv" else PLOT_DIR
    if len(probes) == 1:
        return f"{dir}probe_pop_ips_{list(probes.keys())[0]}.{ext}"
    return f"{dir}probe_pop_ips_{min(probes.keys())}_to_{max(probes.keys())}.{ext}"
def BENT_PIPE_FILE(probes: Probes, 
                   type: str, group_by: str|None = None,
                   ext: str="csv") -> str:
    """Return the file path for the probe bent pipe analysis."""
    details = f"{type}{'_' + group_by if not group_by is None else ''}"
    dir = DATA_DIR if ext == "csv" else PLOT_DIR
    if len(probes) == 1:
        return f"{dir}bent_pipe_{details}_{list(probes.keys())[0]}.{ext}"
    return f"{dir}bent_pipe_{details}_{min(probes.keys())}_to_{max(probes.keys())}.{ext}"