from glob import glob
import os
import datetime

def list_data_files(dir):
    """Return list of all data files in given directory."""
    files = glob(f"{dir}/*.txt")
    rep1 = os.path.join(f"{dir}", "file_")
    ret = []
    for file in files:
        date_str = file.replace(f"{rep1}", "").replace(".txt", "")
        date = datetime.datetime.strptime(date_str, "%Y%m%d_%H%M%S")
        # The files use UTC time, need to add 3 hours
        date = date + datetime.timedelta(hours=3)
        ret.append((file, date))
    return ret

def get_files_timespan(dir, starttime, endtime):
    """Return list of files that capture data within specific datetime window."""
    all_files = list_data_files(dir)
    filtered_files = filter(lambda x: x[1] > starttime and x[1] < endtime, all_files)
    return list(filtered_files)