"""

"""

import pandas as pd

from .decorators import check_file_path


def read_profile(path="PROFILE.OUT"):
    """

    Parameters
    ----------
    path: str, optional
        String with the name of the profile out file. default is
        "PROFILE.OUT".

    Returns
    -------
    data: pandas.DataFrame
        Pandas with the profile data

    """
    data = _read_file(path=path, start="depth", idx_col="n")
    return data


def read_run_inf(path="RUN_INF.OUT", usecols=None):
    """Method to read the RUN_INF.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the run_inf out file. default is
        "RUN_INF.OUT".
    usecols: list of str optional
        List with the names of the columns to import. By default:
        "TLevel", "Time", "dt", "Iter", "ItCum",
        "KodT", "KodB", "Convergency".

    Returns
    -------
    data: pandas.DataFrame
        Pandas with the run_inf data

    """
    data = _read_file(path=path, start="TLevel", idx_col="TLevel")
    return data


def read_i_check(path="I_CHECK.OUT", usecols=None, times=None):
    """Method to read the I_CHECK.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the I_Check out file. default is
        "I_Check.OUT".
    usecols: list, optional
    times

    Returns
    -------
    data: dict
        Dictionary with the node as a key and a Pandas DataFrame as a
        value.

    """
    raise NotImplementedError


def read_tlevel(path="T_LEVEL.OUT", usecols=None):
    """Method to read the T_LEVEL.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the t_level out file. default is
        "T_LEVEL.OUT".
    usecols: list of str optional
        List with the names of the columns to import. By default
        only the real fluxes are imported and not the cumulative
        fluxes. Options are: "rTop", "rRoot", "vTop", "vRoot", "vBot",
        "sum(rTop)", "sum(rRoot)", "sum(vTop)", "sum(vRoot)", "sum(vBot)",
        "hTop", "hRoot", "hBot", "RunOff", "sum(RunOff)", "Volume",
        "sum(Infil)", "sum(Evap)", "TLevel", "Cum(WTrans)", "SnowLayer".

    Returns
    -------
    data: pandas.DataFrame
        Pandas with the t_level data

    """
    data = _read_file(path=path, start="rTop", idx_col="Time",
                      remove_first_row=True)
    return data

def read_alevel(path="A_LEVEL.OUT", usecols=None):
    """Method to read the A_LEVEL.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the t_level out file. default is
        "A_LEVEL.OUT".
    usecols: list of str optional
        List with the names of the columns to import.

    Returns
    -------
    data: pandas.DataFrame
        Pandas with the a_level data

    """
    data = _read_file(path=path, start="Time", idx_col="Time",
                      remove_first_row=True)
    return data

def read_solute(path="SOLUTE1.OUT"):
    data = _read_file(path=path, start="Time", idx_col="Time",
                      remove_first_row=True)
    return data

@check_file_path
def _read_file(path, start, end="end", usecols=None, idx_col=None,
               remove_first_row=False):
    """Internal method to read Hydrus output files.

    Parameters
    ----------
    path: str
        String with the filepath.
    start: str
        String that determines the start of the data to be imported.
    end: str, optional
        String that determines the end of the data to be imported.
    usecols: list, optional
        List with the names of the columns to import. Default is all
        columns.
    idx_col: str, optional
        String with the name used for the index column.
    remove_first_row: bool, optional
        Remove the first row if True. Default is False.

    Returns
    -------
    data: pandas.DataFrame
        Pandas DataFrame with the imported data.

    """
    with open(path) as file:
        # Find the starting line
        for i, line in enumerate(file.readlines()):
            if start in line:
                s = i
            elif end in line:
                e = i
                break
        file.seek(0)  # Go back to start of file

        # Read data into a Pandas DataFrame
        data = pd.read_csv(file, skiprows=s, nrows=e - s - 2,
                           index_col=idx_col, skipinitialspace=True,
                           delim_whitespace=True, usecols=usecols)

        if remove_first_row:
            data = data.drop(index=data.index[0]).apply(pd.to_numeric)

    return data


@check_file_path
def read_obs_node(path="OBS_NODE.OUT", nodes=None, times=None):
    """Method to read the OBS_NODE.OUT output file.

    Parameters
    ----------
    nodes
    path: str, optional
        String with the name of the OBS_NODE out file. default is
        "OBS_NODE.OUT".
    times

    Returns
    -------
    data: dict
        Dictionary with the node as a key and a Pandas DataFrame as a
        value.

    """
    data = {}
    with open(path) as file:
        # Find the starting times to read the information
        for i, line in enumerate(file.readlines()):
            if "time" in line:
                start = i
            elif "end" in line:
                end = i
                break

        for i, node in enumerate(nodes):
            file.seek(0)
            if i == 0:
                usecols = ["time", "h", "theta", "Temp"]
            else:
                usecols = ["time", "h." + str(i), "theta." + str(i),
                           "Temp." + str(i)]
            df = pd.read_csv(file, skiprows=start, index_col=0,
                             skipinitialspace=True, delim_whitespace=True,
                             nrows=end - start - 1, usecols=usecols)
            df.columns = ["h", "theta", "Temp"]
            data[node] = df

    return data


@check_file_path
def read_nod_inf(path="NOD_INF.OUT", times=None):
    """Method to read the NOD_INF.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the NOD_INF out file. default is
        "NOD_INF.OUT".
    times: int, optional
        Create a DataFrame with nodal values of the pressure head,
        the water content, the solution and sorbed concentrations, and
        temperature, etc, at the time "times". default is None.

    Returns
    -------
    data: dict
        Dictionary with the time as a key and a Pandas DataFrame as a
        value.

    """
    use_times = []
    start = []
    end = []
    data = {}

    with open(path) as file:
        # Find the starting times to read the information
        for i, line in enumerate(file.readlines()):
            if "Time" in line and not "Date" in line:
                time = float(line.replace(" ", "").split(":")[
                                 1].replace("\n", ""))
                use_times.append(time)
            elif "Node" in line:
                start.append(i)
            elif "end" in line:
                end.append(i)

        if times is None:
            times = use_times

        # Read the profile data into a Pandas DataFrame
        for start, end, time in zip(start, end, use_times):
            if time in times:
                file.seek(0)  # Go back to start of file
                df = pd.read_csv(file, skiprows=start + 2, header=None,
                                 skipinitialspace=True, delim_whitespace=True,
                                 nrows=end - start - 3)
                data[time] = df
    if len(data) is 1:
        return next(iter(data.values()))
    else:
        return data


@check_file_path
def read_balance(path="BALANCE.OUT", usecols=None):
    """Method to read the BALANCE.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the run_inf out file. default is
        "BALANCE.OUT".
    usecols: list of str optional
        List with the names of the columns to import. By default:
        "Area","W-volume","In-flow","h Mean","Top Flux",
        "Bot Flux","WatBalT","WatBalR".

    Returns
    -------
    data: pandas.DataFrame
        Pandas with the balance data

    """
    if usecols is None:
        usecols = ["Area", "W-volume", "In-flow", "h Mean", "Top Flux",
                   "Bot Flux", "WatBalT", "WatBalR"]

    lines = open(path).readlines()
    use_times = []
    start = []
    end = [16]
    for i, line in enumerate(lines):
        for x in usecols:
            if x in line:
                line1 = x
                line2 = line.replace("\n", "").split(" ")[-1]
                line3 = line.replace("  ", " ").split(" ")[-2]
                lines[i] = [line1, line2, line3]

        if "Time" in line and "Date" not in line:
            time = float(
                line.replace(" ", "").split("]")[1].replace("\n", ""))
            use_times.append(time)
        if "Area" in line:
            start.append(i)
        if "WatBalR" in line:
            end.append(i + 1)
        if "Sub-region" in line:
            subregions = \
                line.replace("  ", " ").replace("\n", "").split(" ")[-1]
    print(lines)
    data = {}
    for s, e, time in zip(start, end, use_times):
        df = pd.DataFrame(lines[s:e]).set_index(0).T
        index = {}
        for x in range(int(subregions) + 1):
            index[x + 1] = x
            df = df.rename(index=index)
        data[time] = df

    return data
