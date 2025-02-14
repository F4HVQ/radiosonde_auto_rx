
#!/bin/python3
#
# auto_rx debug utils - Plot an rtl_power output file.
#
# Usage: python plot_rtl_power.py log_power.csv
# Requires Numpy & Matplotlib
#

# Global imports
import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from io import StringIO
from typing import Tuple


FILE_NAME = Path(__file__).name


# Functions definition
# Need to keep this in sync with auto_rx.py as we're not set up to do relative imports yet.
def read_rtl_power(filename : Path) -> Tuple:
    """ Read in frequency samples from a single-shot log file produced by rtl_power
    :param filename The filename of log_power.csv file
    :return Tuple
    """

    # Output buffers.
    freq  = np.array([])
    power = np.array([])

    freq_step = 0

    # Open file.
    with filename.open(mode='r') as f:

        # rtl_power log files are csv's, with the first 6 fields in each line describing the time and frequency scan parameters
        # for the remaining fields, which contain the power samples.

        for line in f:
            # Split line into fields.
            fields = line.split(',')

            if len(fields) < 6:
                logging.error("Invalid number of samples in input file - corrupt?")
                raise Exception("Invalid number of samples in input file - corrupt?")

            start_date = fields[0]
            start_time = fields[1]
            start_freq = float(fields[2])
            stop_freq  = float(fields[3])
            freq_step  = float(fields[4])
            n_samples  = int(fields[5])

            #freq_range = np.arange(start_freq,stop_freq,freq_step)
            samples     = np.loadtxt(StringIO(",".join(fields[6:])),delimiter=',')
            freq_range  = np.linspace(start_freq,stop_freq,len(samples))

            # Add frequency range and samples to output buffers.
            freq  = np.append(freq, freq_range)
            power = np.append(power, samples)

    # Sanitize power values, to remove the nan's that rtl_power puts in there occasionally.
    power = np.nan_to_num(power)

    return (freq, power, freq_step)

if __name__ == '__main__':
    """ Main entry point """

    # Messages
    epilog_msg = '''\
                See above examples
                    - [?]$ ./{0} ../log/log_power_0.csv
                '''.format(FILE_NAME)

    # Specify command arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="Plot an rtl_power output file.",
                                     epilog=epilog_msg)

    parser.add_argument("log_file",
                        default="../log/log_power_0.csv",
                        help="log power file")

    args = parser.parse_args()

    (freq, power, freq_step) = read_rtl_power(Path(args.log_file))

    plt.plot(freq / 1e6, power)
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Power (dB?)")
    plt.title("rtl_power output: {}".format(args.log_file))
    plt.show()
