# ligo_signal

This repository contains `python` scripts to: 
1. Control and make measurements from a Keysight InfiniiVision 2000 X-Series oscilloscope through a **USB** interface. 
    - The scripts are tested on a DSO-X 2024A with the **segmented memory option enabled**
2. Analyze and first-steps to extract ring-down parameters from measured/simulated data
3. To extract the noise floor and estimate the signal to noise ratio (SNR) of a measurement set up 

## Installation

The scripts were tested on a Windows 10 computer, in a `python 3.9.6` environment. User are highly recommended to use [Miniconda](https://docs.conda.io/en/latest/miniconda.html) to create their `python` environment. To ensure that all the scripts work as intended, we recommend installing all the packages listed in `requirements.txt`, by entering the following command in the anaconda prompt
```
$ conda create --name <env> --file requirements.txt
```

For user's who would like to use their existing `python` environment, we suggest to ensure that the following packages are installed (links to their respective documentation in the reference section): 
```
numpy, scipy, pandas, matplotlib, keyoscacquire, pyvisa, lmfit
```
- `numpy, scipy, pandas, matplotlib` commonly packages for data manipulation, analysis, and plotting
- `keyoscacquire` contains commands to establish a `VISA` connection with the oscilloscope. Our scripts extend `keyoscacquire`'s existing functionalities
- `pyvisa` is required to control instruments 
- `lmfit` for fitting and ring-down time extraction 

### NI-VISA Backend
In order for `pyvisa` to work, users should make sure that that they have a VISA backend, such as `NI-VISA` installed on their computer. For more information, see 
- [PyVisa installation](https://pyvisa.readthedocs.io/en/latest/introduction/getting.html)
- [NI-VISA installation](https://www.ni.com/en-ca/support/downloads/drivers/download.ni-visa.html#442805)

In addition to `NI-VISA` we found that the following driver should also be installed [NI-488.2 GPIB driver](https://www.ni.com/en-ca/support/downloads/drivers/download.ni-488-2.html#345631). 

## Usage 
```
scope = koa.Oscilloscope(address='USB0::2391::6038::MY58104655::INSTR', timeout=60e3)
```
The oscilloscope VISA address can be found by the following procedures. 
1. In the front panel of the oscilloscope, under "Tools", select "Utility"
2. Select "IO" in the utilities menu, the VISA address will be displayed

Most scripts in the repository are standalone `jupyter notebooks`. Contained in `scope/`:
1. [`scope_basics.ipynb`](scope/scope_basics.ipynb): goes over basic commands to control the oscilloscope, and basic commands to save data from it 
2. [`scope_segmented_acquisition.ipynb`](scope/scope_segmented_acquisition.ipynb): covers how to start a segmented acquisition on the oscilloscope, save the acquired data to the computer, and how to open it afterwards for analysis 
3. [`infiniivision2000x.py`](scope/infiniivision2000x.py): contains functions that wraps VISA commands

Contained in `analysis/`:
1. [`noise.ipynb`](analysis/noise.ipynb): an overview how to compute the power spectral density, extract the signal to noise ratio, and the noise floor in experimental data  
2. [`filter.ipynb`](analysis/filter.ipynb): overview of how to low pass, and band pass filter signals using python. We look at the difference between applying a one-sided versus a two sided filter. And we also look at the signals in the time and frequency domain after filtering 
4. [`envelope.ipynb`](analysis/envelope.ipynb): using the techniques described in the two previous notebooks, we try to denoise and extract the ring down time of a synthesized noisy signal 

Contained in `data/`: example data files used the notebooks above. 

## Future 

We would like to: 
- Structure what is contained in the acquired data files, and their naming schemes. Use a unified data acquisition scheme such as `QCoDeS` 

## References

- [Agilent InfiniiVision 2000 X-Series Oscilloscope Programmer's Guide](http://sites.science.oregonstate.edu/~hetheriw/whiki/ph415_s12/topics/inst/agilent/files/2000_series_prog_guide.pdf)
- [keyoscacquire: Keysight oscilloscope acquire](https://github.com/asvela/keyoscacquire)
- [Matplotlib documentation](https://matplotlib.org/stable/index.html)
- [NumPy documentation](https://numpy.org/doc/stable/)
- [SciPy documentation](https://docs.scipy.org/doc/scipy/getting_started.html)
- [LMFIT documentation](https://lmfit.github.io/lmfit-py/index.html)