import keyoscacquire as koa
import numpy as np 

def set_time_per_division(scope: koa.Oscilloscope, dt: float) -> None: 
    """Set the time per vision 

    Args:
        scope (koa.Oscilloscope): _description_
        dt (float): time in seconds between divisions
    """
    scope.write(':TIMebase:RANGe {}'.format(dt*10))
    
def set_range(scope: koa.Oscilloscope, channel: int, dv: float, total_divisions = 8) -> None:
    """sets the volts per division for the oscilloscope, assuming there's 8 division 
    
    The :CHANnel<n>:RANGe command defines the full-scale vertical axis of
    the selected channel. When using 1:1 probe attenuation, legal values for
    the range are from 16 mV to 40 V.

    Args:
        scope (koa.Oscilloscope): _description_
        channel (int): _description_
        dv (float): _description_
    """
    scope.write(':CHANnel{}:RANGe {}'.format(channel, dv*total_divisions))
    
def get_range(scope: koa.Oscilloscope, channel: int) -> float:
    """The :CHANnel<n>:RANGe command defines the full-scale vertical axis of
        the selected channel. When using 1:1 probe attenuation, legal values for
        the range are from 16 mV to 40 V.

    Args:
        scope (koa.Oscilloscope): _description_
        channel (int): _description_
        dv (float): _description_
    """
    return float(scope.query(':CHANnel{}:RANGe?'.format(channel)))/8

def get_acq_mode(scope: koa.Oscilloscope,) -> str:
    """Returns the acqusition mode
    
    Will return "RTIME" for real time, or "SGMT" for segmented acquisition 
    """
    return scope.query(':ACQuire:MODE?')

def set_seg_count(scope: koa.Oscilloscope, count: int) -> None:
    """Sets the number of segments to acquire
    """
    return scope.write(':ACQuire:SEGMented:COUNt {}'.format(count))

def set_current_seg(scope: koa.Oscilloscope, idx: int) -> None:
    """Sets the current viewed segment on the oscilloscope to be the number specified by idx 
    """
    return scope.write(':ACQuire:SEGMented:INDex {}'.format(idx))

def get_seg_count(scope: koa.Oscilloscope) -> str:
    """Asks for the the number of segments to acquire
    """
    return scope.query(':ACQuire:SEGMented:COUNt?')

def get_current_seg_number(scope: koa.Oscilloscope) -> str:
    """Ask for how many segments have been acquired so far. This command can be called during the oscilloscope makes the acquisition!
    """
    return scope.query(':WAVeform:SEGMented:COUNt?')

def get_current_seg_timetag(scope: koa.Oscilloscope) -> str:
    """Ask for the time tag of the selected segment. Used for existing segments
    """
    return scope.query(':WAVeform:SEGMented:TTAG?')

def run(scope: koa.Oscilloscope) -> None:
    """The :RUN command starts repetitive acquisitions. This is the same as pressing the Run key on the front panel. Use this this command to continuously acquire data
    """
    return scope.write(':RUN')

def stop(scope: koa.Oscilloscope) -> None:
    """Stop the current acquistion
    """
    return scope.write(':STOP')

def save_segmented_data(scope: koa.Oscilloscope, fname: str) -> None: 
    """Code credit to 
    ```
    https://github.com/jlpoltrack/DSOX-Scripts/blob/cf9b97e2e47b6a6d069a232bda9699bfedf8a023/Keysight%20Examples/InfiniiVision_SegmentedMemory_Waveform_and_Measurement_Grabber.py
    ```

    KEY POINT:
    Using fewer segments can result in a higher sample rate.
    If the user sets the scope to acquire the maximum number for segments, and STOPS it before it is done,
    It is likely that a higher sample rate could have been achieved.
    
    Args:
        scope (koa.Oscilloscope): _description_
        fname (str): _description_
    """
    GET_WFM_DATA = "YES" 
    BASE_FILE_NAME = fname
    NSEG = int(scope.query(":WAVeform:SEGMented:COUNt?"))
    print(str(NSEG) + " segments were acquired.")
    ## pre-allocate TimeTag data array
    Tags =  np.zeros(NSEG)

    ## Flip through segments...
    for n in range(1,NSEG+1,1): ## Python indices start at 0, segments start at 1

        scope.write(":ACQuire:SEGMented:INDex " + str(n)) # Go to segment n

        Tags[n-1] = scope.query(":WAVeform:SEGMented:TTAG?") # Get time tag of segment n ; always get time tags

        if GET_WFM_DATA == "YES":
            if n == 1: # Only need to do some things once

                ## Determine which channels are on, and which have acquired data, and get the vertical pre-amble info accordingly
                    ## Use brute force method for readability

                CHS_ON = [0,0,0,0] # Create empty array to store channel states
                NUMBER_CHANNELS_ON = 0

                ## Channel 1
                on_off = int(scope.query(":CHANnel1:DISPlay?"))
                Channel_acquired = int(scope.query(":WAVeform:SOURce CHANnel1;:WAVeform:POIN?")) # If there are no points available
                    ## this channel did not capture data and thus there are no points (but was turned on)
                if Channel_acquired == 0 or on_off == 0:
                    scope.write(":CHANnel1:DISPlay OFF") # Setting a channel to be a waveform source turns it on...
                    CHS_ON[0] = 0
                    Y_INCrement_Ch1 = "BLANK"
                    Y_ORIGin_Ch1    = "BLANK"
                    Y_REFerence_Ch1 = "BLANK"
                else:
                    CHS_ON[0] = 1
                    NUMBER_CHANNELS_ON += 1
                    Pre = scope.query(":WAVeform:SOURce CHANnel1;:WAVeform:PREamble?").split(',')
                    Y_INCrement_Ch1 = float(Pre[7]) # Voltage difference between data points
                    Y_ORIGin_Ch1    = float(Pre[8]) # Voltage at center screen
                    Y_REFerence_Ch1 = float(Pre[9]) # Specifies the data point where y-origin occurs, alwasy zero
                        ## The programmer's guide has a very good description of this, under the info on :WAVeform:PREamble.

                ## Channel 2
                on_off = int(scope.query(":CHANnel2:DISPlay?"))
                Channel_acquired = int(scope.query(":WAVeform:SOURce CHANnel2;:WAVeform:POIN?"))
                if Channel_acquired == 0 or on_off == 0:
                    scope.write(":CHANnel2:DISPlay OFF")
                    CHS_ON[1] = 0
                    Y_INCrement_Ch2 = "BLANK"
                    Y_ORIGin_Ch2    = "BLANK"
                    Y_REFerence_Ch2 = "BLANK"
                else:
                    CHS_ON[1] = 1
                    NUMBER_CHANNELS_ON += 1
                    Pre = scope.query(":WAVeform:SOURce CHANnel2;:WAVeform:PREamble?").split(',')
                    Y_INCrement_Ch2 = float(Pre[7])
                    Y_ORIGin_Ch2    = float(Pre[8])
                    Y_REFerence_Ch2 = float(Pre[9])

                ## Channel 3
                on_off = int(scope.query(":CHANnel3:DISPlay?"))
                Channel_acquired = int(scope.query(":WAVeform:SOURce CHANnel3;:WAVeform:POIN?"))
                if Channel_acquired == 0 or on_off == 0:
                    scope.write(":CHANnel3:DISPlay OFF")
                    CHS_ON[2] = 0
                    Y_INCrement_Ch3 = "BLANK"
                    Y_ORIGin_Ch3    = "BLANK"
                    Y_REFerence_Ch3 = "BLANK"
                else:
                    CHS_ON[2] = 1
                    NUMBER_CHANNELS_ON += 1
                    Pre = scope.query(":WAVeform:SOURce CHANnel3;:WAVeform:PREamble?").split(',')
                    Y_INCrement_Ch3 = float(Pre[7])
                    Y_ORIGin_Ch3    = float(Pre[8])
                    Y_REFerence_Ch3 = float(Pre[9])

                ## Channel 4
                on_off = int(scope.query(":CHANnel4:DISPlay?"))
                Channel_acquired = int(scope.query(":WAVeform:SOURce CHANnel4;:WAVeform:POIN?"))
                if Channel_acquired == 0 or on_off == 0:
                    scope.write(":CHANnel4:DISPlay OFF")
                    CHS_ON[3] = 0
                    Y_INCrement_Ch4 = "BLANK"
                    Y_ORIGin_Ch4    = "BLANK"
                    Y_REFerence_Ch4 = "BLANK"
                else:
                    CHS_ON[3] = 1
                    NUMBER_CHANNELS_ON += 1
                    Pre = scope.query(":WAVeform:SOURce CHANnel4;:WAVeform:PREamble?").split(',')
                    Y_INCrement_Ch4 = float(Pre[7])
                    Y_ORIGin_Ch4    = float(Pre[8])
                    Y_REFerence_Ch4 = float(Pre[9])

                ANALOGVERTPRES = (Y_INCrement_Ch1, Y_INCrement_Ch2, Y_INCrement_Ch3, Y_INCrement_Ch4, Y_ORIGin_Ch1, Y_ORIGin_Ch2, Y_ORIGin_Ch3, Y_ORIGin_Ch4, Y_REFerence_Ch1, Y_REFerence_Ch2, Y_REFerence_Ch3, Y_REFerence_Ch4)
                del Pre, on_off, Channel_acquired

                ## Find first channel on
                ch = 1
                for each_value in CHS_ON:
                    if each_value ==1:
                        FIRST_CHANNEL_ON = ch
                        break
                    ch +=1
                del ch, each_value

                ## Setup data export
                scope.write(":WAVeform:FORMat WORD")  # 16 bit word format...
                scope.write(":WAVeform:BYTeorder LSBFirst") # Explicitly set this to avoid confusion
                scope.write(":WAVeform:UNSigned 0") # Explicitly set this to avoid confusion
                scope.write(":WAVeform:SOURce CHANnel" + str(FIRST_CHANNEL_ON))  # Set waveform source to any enabled channel, here the FIRST_CHANNEL_ON
                scope.write(":WAVeform:POINts MAX") # Set number of points to max possible for any InfiniiVision; ensures all are available
                    ## If using :WAVeform:POINts MAX, be sure to do this BEFORE setting the :WAVeform:POINts:MODE as it will switch it to MAX
                scope.write(":WAVeform:POINts:MODE RAW")  # Set this now so when the preamble is queried it knows what how many points it can retrieve from
                    ## If measurements are also being made, they are made on a different record, the "measurement record."  This record can be accessed by using:
                    ## :WAVeform:POINts:MODE NORMal isntead of :WAVeform:POINts:MODE RAW
                POINTS = int(scope.query(":WAVeform:POINts?")) # Get number of points.  This is the number of points in each segment.
                print(str(POINTS) + " points were acquired for each channel for each segment.")

                ## Get timing pre-amble data - this can be done at any segment - it does not change segment to segment
                Pre = scope.query(":WAVeform:PREamble?").split(',')
                AMODE        = float(Pre[1]) # Gives the scope acquisition mode
                X_INCrement = float(Pre[4]) # Time difference between data points
                X_ORIGin    = float(Pre[5]) # Always the first data point in memory
                X_REFerence = float(Pre[6]) # Specifies the data point associated with x-origin; The x-reference point is the first point displayed and XREFerence is always 0.
                    ## The programmer's guide has a very good description of this, under the info on :WAVeform:PREamble.
                del Pre

                ## Pre-allocate data array
                if AMODE == 1: # This means peak detect mode
                    Wav_Data = np.zeros([NUMBER_CHANNELS_ON,2*POINTS,NSEG])
                    ## Peak detect mode returns twice as many points as the points query, one point each for LOW and HIGH values
                else: # For all other acquistion modes
                    Wav_Data = np.zeros([NUMBER_CHANNELS_ON,POINTS,NSEG])

                ## Create time axis:
                DataTime = ((np.linspace(0,POINTS-1,POINTS)-X_REFerence)*X_INCrement)+X_ORIGin
                if AMODE == 1: # This means peak detect mode
                    DataTime = np.repeat(DataTime,2)
                    ##  The points come out as Low(time1),High(time1),Low(time2),High(time2)....

            ## Pull waveform data, scale it - for every segment
            ch = 1 # channel number
            i  = 0 # index of Wav_data
            for each_value in  CHS_ON:
                if each_value == 1:
                    ## Gets the waveform in 16 bit WORD format
                    Wav_Data[i,:,n-1] = np.array(scope._inst.query_binary_values(':WAVeform:SOURce CHANnel' + str(ch) + ';DATA?', "h", False))
                    ## Scales the waveform
                    Wav_Data[i,:,n-1] = ((Wav_Data[i,:,n-1]-ANALOGVERTPRES[ch+7])*ANALOGVERTPRES[ch-1])+ANALOGVERTPRES[ch+3]
                        ## For clarity: Scaled_waveform_Data[*] = [(Unscaled_Waveform_Data[*] - Y_reference) * Y_increment] + Y_origin
                    i +=1
                ch +=1
            del ch, i,

    ## End of flipping through segments
    ## Some cleanup
    if GET_WFM_DATA == "YES":
        del  ANALOGVERTPRES,Y_INCrement_Ch1, Y_ORIGin_Ch1, Y_REFerence_Ch1, Y_INCrement_Ch2, Y_ORIGin_Ch2, Y_REFerence_Ch2,Y_INCrement_Ch3, Y_ORIGin_Ch3, Y_REFerence_Ch3, Y_INCrement_Ch4, Y_ORIGin_Ch4, Y_REFerence_Ch4, X_INCrement, X_ORIGin, X_REFerence

    ## Close Connection to scope properly
    # scope.clear()
    # scope.close()

    ## Save waveform data
    if GET_WFM_DATA == "YES":

        segment_indices = np.linspace(1,NSEG,NSEG, dtype = int)

        i = 0
        ch = 1
        for each_value in CHS_ON:
            if each_value == 1:
                filename = BASE_FILE_NAME + ".csv"
                with open(filename, 'w') as filehandle:
                    filehandle.write("Timestamp (s):,")
                    np.savetxt(filehandle, np.atleast_2d(Tags), delimiter=',')
                    filehandle.write("Segment Index:,")
                    np.savetxt(filehandle, np.atleast_2d(segment_indices), delimiter=',')
                    filehandle.write("Time (s), Waveforms...\n")
                    np.savetxt(filehandle, np.insert(Wav_Data[i,:,:],0,DataTime,axis=1), delimiter=',')
                i +=1
            ch +=1
        del each_value, ch, filehandle, filename, segment_indices

