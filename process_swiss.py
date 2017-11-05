import os
import re
import time
import pandas
from pandas import DataFrame
import pdb
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
import sys
import matplotlib 
import glob
matplotlib.use('Agg')

sys.path.insert(0, '/Users/maxtby/Dropbox/swisschicks/syncher')

import matplotlib.pyplot as plt
#from zvision.zv_iterm import zv_dispFig
from parse_skov_data import get_bins_indices

NUM_MINS_PER_BIN = 30

def parse_data_from_file(path):
    """
    parse the date, time and stald number from the 
    results filepath. 

    Args:
        path (pathlib.Path): path to an of results file

    Returns:
        (dt, stald_num): a datetime object and an 
        integer representing the time and stald which the
        results relate to.
    
    Example:

        /a/b/c/name_20161122235959_20161123000005_1170027.of
        implies a video from:
            year = 2016, month = 12, day = 22, time 23:59:59
        to
            year = 2016, month = 12, day = 23, time 00:00:05
    """
    print(path.stem)
    
    raw = path.stem.split('-')

    rawdate = raw[0][2:]
    print(rawdate)
    date = rawdate[6:] + "/" + rawdate[4:6] + '/' + rawdate[0:4]
    rawtime = raw[1]
    time = rawtime[0:2] + "h" + rawtime[2:4] + "m" + rawtime[4:6] + "s"
    dt = datetime.strptime(rawdate+rawtime, '%Y%m%d%H%M%S')
    print(dt)
    return dt

def to_timestamp(index, base_dt, fps=4):
    """
    computes a Unix timestemp for each statistic based on its 
    index and a base datetime representing the first index in 
    the sequence. 

    Args:
        index (int): a position in the sequence
        base_dt (datetime.datetime): the datetime of the first index

    Returns:
        (int): a Unix timestamp
    """
    ts = time.mktime(base_dt.timetuple())
    return ts + index * (1.0 / fps)

def get_timestamped_of_stats(path):
    """
    loads a collection of opticflock statistics into a data frame
    and adds timestamp information to set of statistics

    Args:
        path (pathlib.Path): the path to the file containing the raw
           statistics
    Returns:
        pandas.DataFrame: a dataframe combining the statistics with 
           datetimes and Unix timestamps
    """
    dt = parse_data_from_file(path)
    data = pandas.read_csv(str(path), delimiter=' ', header=None, 
            names=['index', 'mean', 'var', 'skew', 'kurt'])
    unixify = lambda x: to_timestamp(x, dt)
    datetimer = lambda x: datetime.fromtimestamp(x)
    data['UnixStamp'] = data['index'].apply(unixify)
    data['DateTime'] = data['UnixStamp'].apply(datetimer)
    return data

def get_of_medians(of_stat_dir, num_mins_per_bin):
    """
    generates a set of median summary statistics from the raw OF
    statistics files contained in a given directory

    Args:
        path (pathlib.Path): the path to the directory containing raw
            statistics
        num_mins_per_bin (int): the bin interval used when computing
            median summaries

    Returns:
        pandas.DataFrame: a dataframe of summary medians
    """
    stat_files = list(Path.glob(of_stat_dir, '*.of'))
    data_frames = []
    for stat_file in stat_files:
        df = get_timestamped_of_stats(stat_file)
        data_frames.append(df)

    #¬†merge statistics for a single session and sort by timestamp
    res = pandas.concat(data_frames, axis=0)
    res.sort_values('UnixStamp', ascending=True, inplace=True)

    bins = get_bins_indices(res, num_mins_per_bin, align_to_hour=False)
    medians = res.groupby(bins).median()

    # remove index and unix stamps since they are no longer needed
    medians = medians.drop('index', axis=1)
    return medians

def combine_stald_stats(stald_num, of_stat_dirs):
    """
    combine the statistics computed across all sessions recorded
    in a given Stald.

    Args:
        stald_num (int): The number of the Stald

    Returns:
        pandas.DataFrame: the combined statistics gathered across
            sessions
    """
    stald_dirs = [d for d in of_stat_dirs if 
                    int(re.split('_|-',d.stem)[0]) == stald_num]
    meds = []
    for of_stat_dir in tqdm(stald_dirs):
        meds.append(get_of_medians(of_stat_dir, num_mins_per_bin=30))
    stald_meds = pandas.concat(meds, axis=0)
    stald_meds.sort_values('UnixStamp', ascending=True, inplace=True)
    stald_meds = stald_meds.drop('UnixStamp', axis=1)
    return stald_meds

# set paths to raw of statistics and skov production data

#====main======#
#of_dir#
res_dir_HD4 = Path('/Users/maxtby/Documents/swissdata/HD4')
res_dir_HD2 = Path('/Users/maxtby/Documents/swissdata/HD2')
res_dir_HD5 = Path('/Users/maxtby/Documents/swissdata/HD5')


stald_num = []
summary_dir = Path('/Users/maxtby/Documents/resultsSummaryHD5.csv')

string_files = glob.glob('/Users/maxtby/Documents/swissdata/HD5/**/**/*.of')
stats_files = [Path(x) for x in string_files]

for stat_file in stats_files:
    print('processing: {}'.format(stat_file))
    #----
    df = get_timestamped_of_stats(stat_file)
    df.sort_values('UnixStamp', ascending=True, inplace=True)
    bins = get_bins_indices(df, NUM_MINS_PER_BIN, align_to_hour=True)
    medians = df.groupby(bins).median()
    medians = medians.drop('index', axis=1)
    medians = medians.drop('UnixStamp', axis=1)
    stald_num.append(medians)

results = DataFrame().append(stald_num)
#result = pandas.concat(stald_num, keys=['mean', 'var', 'skew', 'kurt'])
#stald_meds = combine_stald_stats(stald_num, stats_files)
#med_path = production_dir / 'Stald-{}.of'.format(stald_num)
results.to_csv(str(summary_dir), columns=['mean', 'var', 'skew', 'kurt'],
						    float_format='%.4f')



