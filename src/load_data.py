import pandas as pd


def load_netflow_csv(csv_path: str) -> pd.DataFrame:
    """
    Loads a NetFlow CSV file into a pandas DataFrame.

    Parameters:
        csv_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded NetFlow data.
    """
    df = pd.read_csv(csv_path)

    return df
