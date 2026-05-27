import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def find_step_segments(force_data_df, start_threshold=1.0, end_threshold=0.1, gap_threshold=1000):
    channel_cols = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Channel7', 'Channel8']

    times = force_data_df['DateTime'].values
    channel_data = force_data_df[channel_cols].values
    
    steps = []
    in_step = False
    current_start = None
    
    for i in range(len(times)):
        max_force = np.max(channel_data[i])
        
        if not in_step:
            if max_force > start_threshold:
                in_step = True
                current_start = times[i]
                
        elif in_step:
            if max_force <= end_threshold:
                in_step = False
                current_end = times[i]
                steps.append([current_start, current_end])
                
    if in_step:
        steps.append([current_start, times[-1]])
    
    gap_threshold = pd.Timedelta(milliseconds=gap_threshold)

    merged_steps = [] #prevent duplicate for one step
    for s in steps: 
        if merged_steps and (s[0] - merged_steps[-1][1]) <= gap_threshold:
            merged_steps[-1][1] = s[1] 
        else:
            merged_steps.append(s)
    #subtract 300ms from start
    subtracted_start_steps = []
    for s in merged_steps:
        if(s[1]-s[0] >= np.timedelta64(10, 'ms')): #if step less than 10ms it's not a step, it's a glitch
            s[0] = s[0]-np.timedelta64(300, 'ms')
            subtracted_start_steps.append(s)

    print(len(subtracted_start_steps))
    return subtracted_start_steps