import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.optimize import curve_fit
from stepsegmentation import find_step_segments
import json
from constants import sensor_coords
from scipy.stats import multivariate_normal
from scipy.ndimage import gaussian_filter
from scipy.interpolate import interp1d, LinearNDInterpolator

def serial_recording_df(raw_serial_data):
    data_for_dataframe = []
    for line in raw_serial_data.readlines():
        line = line.strip()
        line_split_by_comma = line.split(",")
        date_epoch = line_split_by_comma[0]
        channel_readings = line_split_by_comma[1].split("\t")
        if(len(channel_readings) == 8):
            ch1 = channel_readings[0]
            ch2 = channel_readings[1]
            ch3 = channel_readings[2]
            ch4 = channel_readings[3]
            ch5 = channel_readings[4]
            ch6 = channel_readings[5]
            ch7 = channel_readings[6]
            ch8 = channel_readings[7]
            data_for_dataframe.append([date_epoch, ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8])
    df = pd.DataFrame(data_for_dataframe, columns=['DateTime', 'Channel1', 'Channel2', 'Channel3', 'Channel4', "Channel5", "Channel6", "Channel7", "Channel8"])
    df['DateTime'] = pd.to_datetime(df['DateTime'].astype(float), unit='s')
    channel_cols = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Channel7', 'Channel8']
    df[channel_cols] = df[channel_cols].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=channel_cols) #avoid categorisation
    df[channel_cols] = df[channel_cols].clip(lower=0.0) # clip at 0 to remove crosstalk / noise
    return df

def fsr_voltage_to_resistance(voltage_in):
    #ref: https://learn.adafruit.com/force-sensitive-resistor-fsr/using-an-fsr
    # The voltage = Vcc * R / (R + FSR) where R = 47K and Vcc = 3.30V
    # so FSR = ((Vcc - V) * R) / V   
    #datasheet: https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/10/R163882.pdf
    Vcc = 3.30
    Vin = voltage_in
    R = 47000
    fsr = ((Vcc-voltage_in)*R)/Vin
    return fsr

def fsr_resistance_to_conductance(resistance_in):
    #ref: https://learn.adafruit.com/force-sensitive-resistor-fsr/using-an-fsr
    # The voltage = Vcc * R / (R + FSR) where R = 47K and Vcc = 3.30V
    # so FSR = ((Vcc - V) * R) / V   
    #datasheet: https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/10/R163882.pdf
    return 1/resistance_in

def fsr_voltage_to_conductance(voltage_in):
    #ref: https://learn.adafruit.com/force-sensitive-resistor-fsr/using-an-fsr
    # The voltage = Vcc * R / (R + FSR) where R = 47K and Vcc = 3.30V
    # so FSR = ((Vcc - V) * R) / V   
    #datasheet: https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/10/R163882.pdf
    return fsr_resistance_to_conductance(fsr_voltage_to_resistance(voltage_in))

def fsr_voltage_to_newtons(voltage_in, channel):
    #ref: https://learn.adafruit.com/force-sensitive-resistor-fsr/using-an-fsr
    # The voltage = Vcc * R / (R + FSR) where R = 47K and Vcc = 3.30V
    # so FSR = ((Vcc - V) * R) / V   
    #datasheet: https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/10/R163882.pdf
    v_arr = np.asarray(voltage_in, dtype=float)
    v_safe = np.where(v_arr == 0, 1e-9, v_arr) #we need to prevent divide by 0
    in_conductance = fsr_voltage_to_conductance(v_safe)
    newtons = np.where(v_arr == 0, 0.0, (np.interp(in_conductance, calibration_df_conductance[str(channel)], calibration_df_conductance["g"])/1000)*9.81) #return 0 where original was 0
    return float(newtons) if newtons.ndim == 0 else newtons #return df otherwise return original newtons value

def serial_df_to_force_df(serial_data_df):
    force_data_df = serial_data_df.copy()
    force_data_df["Channel1"] = fsr_voltage_to_newtons(force_data_df["Channel1"], 1)
    force_data_df["Channel2"] = fsr_voltage_to_newtons(force_data_df["Channel2"], 2)
    force_data_df["Channel3"] = fsr_voltage_to_newtons(force_data_df["Channel3"], 3)
    force_data_df["Channel4"] = fsr_voltage_to_newtons(force_data_df["Channel4"], 4)
    force_data_df["Channel5"] = fsr_voltage_to_newtons(force_data_df["Channel5"], 5)
    force_data_df["Channel6"] = fsr_voltage_to_newtons(force_data_df["Channel6"], 6)
    force_data_df["Channel7"] = fsr_voltage_to_newtons(force_data_df["Channel7"], 7)
    force_data_df["Channel8"] = fsr_voltage_to_newtons(force_data_df["Channel8"], 8)
    return force_data_df

def serial_df_to_resistance_df(serial_data_df):
    force_data_df = serial_data_df.copy()
    force_data_df["Channel1"] = fsr_voltage_to_resistance(force_data_df["Channel1"])
    force_data_df["Channel2"] = fsr_voltage_to_resistance(force_data_df["Channel2"])
    force_data_df["Channel3"] = fsr_voltage_to_resistance(force_data_df["Channel3"])
    force_data_df["Channel4"] = fsr_voltage_to_resistance(force_data_df["Channel4"])
    force_data_df["Channel5"] = fsr_voltage_to_resistance(force_data_df["Channel5"])
    force_data_df["Channel6"] = fsr_voltage_to_resistance(force_data_df["Channel6"])
    force_data_df["Channel7"] = fsr_voltage_to_resistance(force_data_df["Channel7"])
    force_data_df["Channel8"] = fsr_voltage_to_resistance(force_data_df["Channel8"])
    return force_data_df

def serial_df_to_conductance_df(serial_data_df):
    force_data_df = serial_data_df.copy()
    force_data_df["Channel1"] = fsr_voltage_to_conductance(force_data_df["Channel1"])
    force_data_df["Channel2"] = fsr_voltage_to_conductance(force_data_df["Channel2"])
    force_data_df["Channel3"] = fsr_voltage_to_conductance(force_data_df["Channel3"])
    force_data_df["Channel4"] = fsr_voltage_to_conductance(force_data_df["Channel4"])
    force_data_df["Channel5"] = fsr_voltage_to_conductance(force_data_df["Channel5"])
    force_data_df["Channel6"] = fsr_voltage_to_conductance(force_data_df["Channel6"])
    force_data_df["Channel7"] = fsr_voltage_to_conductance(force_data_df["Channel7"])
    force_data_df["Channel8"] = fsr_voltage_to_conductance(force_data_df["Channel8"])
    return force_data_df

def get_testset_listing():
    return [f for f in os.listdir('testsets') if not f.startswith('.')]

def get_batches_listing(testset):
    return [f for f in os.listdir(f'testsets/{testset}') if not f.startswith('.')]

calibration_df = pd.read_csv("calibrations/calibration_data_0405.csv")
tare = 38.5
calibration_df["g"] = calibration_df["g"] - tare #subtract the tare of the bottle
calibration_df["g"] = calibration_df["g"].clip(lower=0) #clip at 0, it can't be less than 0

def get_calibration_df():    
    return calibration_df

calibration_df_conductance = calibration_df.copy()
calibration_df_conductance["1"] = fsr_voltage_to_conductance(calibration_df_conductance["1"])
calibration_df_conductance["2"] = fsr_voltage_to_conductance(calibration_df_conductance["2"])
calibration_df_conductance["3"] = fsr_voltage_to_conductance(calibration_df_conductance["3"])
calibration_df_conductance["4"] = fsr_voltage_to_conductance(calibration_df_conductance["4"])
calibration_df_conductance["5"] = fsr_voltage_to_conductance(calibration_df_conductance["5"])
calibration_df_conductance["6"] = fsr_voltage_to_conductance(calibration_df_conductance["6"])
calibration_df_conductance["7"] = fsr_voltage_to_conductance(calibration_df_conductance["7"])
calibration_df_conductance["8"] = fsr_voltage_to_conductance(calibration_df_conductance["8"])

def get_calibration_df_conductance():
    return calibration_df_conductance

datasheet_df_resistance = pd.DataFrame()
datasheet_df_resistance["g"] = [1200, 1400, 1600, 1800, 2200]
datasheet_df_resistance["datasheet"] = [150e3, 140e3, 130e3, 120e3, 110e3]

def get_datasheet_df_resistance():
    return datasheet_df_resistance

calibration_df_resistance = calibration_df.copy()
calibration_df_resistance["1"] = fsr_voltage_to_resistance(calibration_df_resistance["1"])
calibration_df_resistance["2"] = fsr_voltage_to_resistance(calibration_df_resistance["2"])
calibration_df_resistance["3"] = fsr_voltage_to_resistance(calibration_df_resistance["3"])
calibration_df_resistance["4"] = fsr_voltage_to_resistance(calibration_df_resistance["4"])
calibration_df_resistance["5"] = fsr_voltage_to_resistance(calibration_df_resistance["5"])
calibration_df_resistance["6"] = fsr_voltage_to_resistance(calibration_df_resistance["6"])
calibration_df_resistance["7"] = fsr_voltage_to_resistance(calibration_df_resistance["7"])
calibration_df_resistance["8"] = fsr_voltage_to_resistance(calibration_df_resistance["8"])

def get_calibration_df_resistance():
    return calibration_df_resistance

def get_average_sensor_force_batch(testset, batch):
    with open(f'testsets/{testset}/{batch}', "r") as raw_serial_data: 
        serial_df = serial_recording_df(raw_serial_data)
        force_df = serial_df_to_force_df(serial_df)
        steps = find_step_segments(force_df)
        channel_cols = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Channel7', 'Channel8']
        peak_force_per_step_list = []
        for step in steps:
            step_df = force_df[(force_df["DateTime"] >= step[0]) & (force_df["DateTime"] <= step[1])]
            max_force_step = step_df[channel_cols].max()        
            peak_force_per_step_list.append(max_force_step.values)  
        peak_force_per_step = pd.DataFrame(peak_force_per_step_list, columns=channel_cols)
        avg_force_df = peak_force_per_step.copy()
        # avg_force_df.drop(columns=["DateTime"], axis=1, inplace=True)
        avg_force_df = avg_force_df.mean(axis=0)
        return avg_force_df
    
def get_sensor_peak_force_step(testset, batch, selected_step):
    with open(f'testsets/{testset}/{batch}', "r") as raw_serial_data: 
        serial_df = serial_recording_df(raw_serial_data)
        force_df = serial_df_to_force_df(serial_df)
        steps = find_step_segments(force_df)
        channel_cols = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Channel7', 'Channel8']
        step_df = force_df[(force_df["DateTime"] >= selected_step[0]) & (force_df["DateTime"] <= selected_step[1])]
        max_force_step = step_df[channel_cols].max()        
        return max_force_step.values
    
def get_step_segment_force_df(testset, batch, selected_step):
    with open(f'testsets/{testset}/{batch}', "r") as raw_serial_data: 
        serial_df = serial_recording_df(raw_serial_data)
        force_df = serial_df_to_force_df(serial_df)
        steps = find_step_segments(force_df)
        step_start_end = steps[selected_step]
        step_df = force_df[(force_df["DateTime"] >= step_start_end[0]) & (force_df["DateTime"] <= step_start_end[1])]
        return step_df

def get_mould_force_from_manifest(mould, manifest):
    with open(f'manifests/{manifest}', "r") as manifest_data:
        manifest_data_json = json.load(manifest_data)
        mould_dfs = []
        recording_paths = manifest_data_json["moulds"][mould]["recordings"]
        for recording_path in recording_paths:
            with open(f'testsets/{recording_path}', "r") as raw_serial_data: 
                serial_df = serial_recording_df(raw_serial_data)
                force_df = serial_df_to_force_df(serial_df)
                mould_dfs.append(force_df) 
        for i in range(1,len(mould_dfs)):
            offset = mould_dfs[i]["DateTime"].min() - mould_dfs[i-1]["DateTime"].max()
            mould_dfs[i]["DateTime"] -= offset
        combined_mould_df = pd.concat(mould_dfs)
        return combined_mould_df

    
def get_manifest_listing():
    return [f for f in os.listdir(f'manifests') if not f.startswith('.')]

def get_cop_listing():
    return [f for f in os.listdir(f'desired_cops') if not f.startswith('.')]

def get_manifest_moulds(manifest):
    with open(f'manifests/{manifest}', "r") as manifest_data:
        manifest_data_json = json.load(manifest_data) 
        return manifest_data_json["moulds"].keys()
    
def get_average_sensor_force_manifest_mould(mould, manifest):
    force_df = get_mould_force_from_manifest(mould, manifest)
    steps = find_step_segments(force_df)
    channel_cols = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Channel7', 'Channel8']
    peak_force_per_step_list = []
    for step in steps:
        step_df = force_df[(force_df["DateTime"] >= step[0]) & (force_df["DateTime"] <= step[1])]
        max_force_step = step_df[channel_cols].max()        
        peak_force_per_step_list.append(max_force_step.values)  
    peak_force_per_step = pd.DataFrame(peak_force_per_step_list, columns=channel_cols)
    avg_force_df = peak_force_per_step.copy()
    # avg_force_df.drop(columns=["DateTime"], axis=1, inplace=True)
    avg_force_df = avg_force_df.mean(axis=0)
    return avg_force_df

def get_sensor_peak_force_step_manifest(manifest, mould, selected_step, precomputed_steps = None):
        steps = precomputed_steps
        force_df = get_mould_force_from_manifest(mould, manifest)
        if(precomputed_steps is None):
            steps = find_step_segments(force_df)
        channel_cols = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Channel7', 'Channel8']
        step_df = force_df[(force_df["DateTime"] >= selected_step[0]) & (force_df["DateTime"] <= selected_step[1])]
        max_force_step = step_df[channel_cols].max()        
        return max_force_step.values


def resample_step_force(df, target_points=100):
    current_time = (df['DateTime'] - df['DateTime'].iloc[0]).dt.total_seconds()
    total_duration = current_time.iloc[-1]
    
    if total_duration == 0:
        return pd.DataFrame()

    relative_scale = current_time / total_duration
    
    new_scale = np.linspace(0, 1, target_points)
    
    return pd.DataFrame({
        'Step_Percent': new_scale * 100,
        'Channel1': np.interp(new_scale, relative_scale, df['Channel1']),
        'Channel2': np.interp(new_scale, relative_scale, df['Channel2']),
        'Channel3': np.interp(new_scale, relative_scale, df['Channel3']),
        'Channel4': np.interp(new_scale, relative_scale, df['Channel4']),
        'Channel5': np.interp(new_scale, relative_scale, df['Channel5']),
        'Channel6': np.interp(new_scale, relative_scale, df['Channel6']),
        'Channel7': np.interp(new_scale, relative_scale, df['Channel7']),
        'Channel8': np.interp(new_scale, relative_scale, df['Channel8'])
    })

def get_manifest_step_cop_pressure(manifest, mould, selected_step):
    force_df = get_mould_force_from_manifest(mould, manifest)
    step_df = force_df[(force_df["DateTime"] >= selected_step[0]) & (force_df["DateTime"] <= selected_step[1])]
    channel_cols = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Channel7', 'Channel8']
    nonzero_step_df = step_df[(step_df[channel_cols] > 1).any(axis=1)].copy()
    x_coords = np.array([sensor_coords[i][0] for i in range(1, len(channel_cols) + 1)])
    y_coords = np.array([sensor_coords[i][1] for i in range(1, len(channel_cols) + 1)])

    total_pressure = nonzero_step_df[channel_cols].sum(axis=1)

    weighted_x_sum = (nonzero_step_df[channel_cols] * x_coords).sum(axis=1)
    weighted_y_sum = (nonzero_step_df[channel_cols] * y_coords).sum(axis=1)

    nonzero_step_df['CoP_x'] = weighted_x_sum / total_pressure
    nonzero_step_df['CoP_y'] = weighted_y_sum / total_pressure
    step_cop_df = nonzero_step_df
    return step_cop_df

def resample_step_cop(df, target_points=100):
    current_time = (df['DateTime'] - df['DateTime'].iloc[0]).dt.total_seconds()
    total_duration = current_time.iloc[-1]
    
    if total_duration == 0:
        return pd.DataFrame()

    relative_scale = current_time / total_duration
    
    new_scale = np.linspace(0, 1, target_points)
    
    interp_x = np.interp(new_scale, relative_scale, df['CoP_x'])
    interp_y = np.interp(new_scale, relative_scale, df['CoP_y'])
    
    return pd.DataFrame({
        'CoP_x': interp_x,
        'CoP_y': interp_y
    })

# def get_manifest_overall_cop_pressure(manifest, mould):
#     force_df = get_mould_force_from_manifest(mould, manifest)
#     steps = find_step_segments(force_df)
    
#     all_normalized_steps = []
    
#     for i, step in enumerate(steps):
#         step_df = get_manifest_step_cop_pressure(manifest, mould, step)
        
#         normalized_df = resample_step_cop(step_df, target_points=10)
#         normalized_df['Step_ID'] = i  
        
#         all_normalized_steps.append(normalized_df)
    
#     overall_cop_df = pd.concat(all_normalized_steps, ignore_index=True)
#     return overall_cop_df

def get_manifest_overall_cop_pressure(mould, manifest):
    force_df = get_mould_force_from_manifest(mould, manifest)
    steps = find_step_segments(force_df)
    cops = []
    for step in steps:
        step_cop = get_manifest_step_cop_pressure(mould=mould, manifest=manifest, selected_step=step)
        normalized_df = resample_step_cop(step_cop, target_points=10)
        cops.append(normalized_df)
    stacked = np.stack(cops, axis=0)       
    mean_cop = np.mean(stacked, axis=0)  
    mean_df = pd.DataFrame(np.hstack([mean_cop]), columns=["CoP_x", "CoP_y"])
    return mean_df

def get_manifest_stacked_cop_pressure(mould, manifest):
    force_df = get_mould_force_from_manifest(mould, manifest)
    steps = find_step_segments(force_df)
    cops = []
    for step in steps:
        step_cop = get_manifest_step_cop_pressure(mould=mould, manifest=manifest, selected_step=step)
        normalized_df = resample_step_cop(step_cop, target_points=10)
        cops.append(normalized_df)
    stacked = np.vstack(cops)
    return pd.DataFrame(stacked, columns=["CoP_x", "CoP_y"])

def retrieve_inverse_design_cop_data(manifest):
    selected_manifest_no_extension = manifest[:-5]
    manifest_cop_data = {}
    if(os.path.isdir(f"inverse_design_cop/{selected_manifest_no_extension}")):
        moulds  = [f for f in os.listdir(f"inverse_design_cop/{selected_manifest_no_extension}") if not f.startswith('.')]
        for mould in moulds:
            manifest_cop_data[mould] = pd.read_csv(f"inverse_design_cop/{selected_manifest_no_extension}/{mould}/cop.csv")
        return manifest_cop_data
    raise Exception("No inverse design CoP data, please generate using Batch export normalized CoP for inverse design.")

    
def inverse_design_find_angles(desired_cop_df, manifest):
    vertical_linear_range = ["0", "1v"]
    vertical_linear_range_degree = [float(item.rstrip("vh")) for item in vertical_linear_range]
    horizontal_linear_range = ["0", "1h", "2h"]
    horizontal_linear_range_degree = [float(item.rstrip("vh")) for item in horizontal_linear_range]
    manifest_cop_data = retrieve_inverse_design_cop_data(manifest=manifest)
    # vertical_f = [interpolate.interp1d(x, y) for stage in manifest_cop_data]
    # horizontal_f = [interpolate.interp1d(x, y) for stage in manifest_cop_data]
    vertical_interpolation_by_stage_x = []
    horizontal_interpolation_by_stage_x = []
    vertical_interpolation_by_stage_y = []
    horizontal_interpolation_by_stage_y = []
    stage_count = manifest_cop_data[vertical_linear_range[0]].shape[0]
    for stage in range(stage_count):
        degree_value = []
        x_value = []
        y_value = []
        for i, degree in enumerate(vertical_linear_range_degree):
            degree_value.append(degree)
            manifest_mould_name = vertical_linear_range[i]
            x_value.append(manifest_cop_data[manifest_mould_name].iloc[stage]["CoP_x"])
            y_value.append(manifest_cop_data[manifest_mould_name].iloc[stage]["CoP_y"])
        vertical_interpolation_by_stage_x.append(interp1d(x_value, degree_value, axis=0, kind='linear', bounds_error=False, fill_value=np.nan))
        vertical_interpolation_by_stage_y.append(interp1d(y_value, degree_value, axis=0, kind='linear', bounds_error=False, fill_value=np.nan))
    for stage in range(stage_count):
        degree_value = []
        x_value = []
        y_value = []
        for i, degree in enumerate(horizontal_linear_range_degree):
            degree_value.append(degree)
            manifest_mould_name = horizontal_linear_range[i]
            x_value.append(manifest_cop_data[manifest_mould_name].iloc[stage]["CoP_x"])
            y_value.append(manifest_cop_data[manifest_mould_name].iloc[stage]["CoP_y"])
        horizontal_interpolation_by_stage_x.append(interp1d(x_value, degree_value, axis=0, kind='linear', bounds_error=False, fill_value=np.nan))
        horizontal_interpolation_by_stage_y.append(interp1d(y_value, degree_value, axis=0, kind='linear', bounds_error=False, fill_value=np.nan))
    estimated_degree_vertical_x = []
    estimated_degree_horizontal_x = []
    estimated_degree_vertical_y = []
    estimated_degree_horizontal_y = []
    for i, stage_df in desired_cop_df.iterrows():
        estimated_degree_vertical_x.append(vertical_interpolation_by_stage_x[i](stage_df["CoP_x"]))
        estimated_degree_horizontal_x.append(horizontal_interpolation_by_stage_x[i](stage_df["CoP_x"]))
        estimated_degree_vertical_y.append(vertical_interpolation_by_stage_y[i](stage_df["CoP_y"]))
        estimated_degree_horizontal_y.append(horizontal_interpolation_by_stage_y[i](stage_df["CoP_y"]))
    estimated_v_degree = np.nanmean(estimated_degree_vertical_x + estimated_degree_vertical_y)
    estimated_h_degree = np.nanmean(estimated_degree_horizontal_x + estimated_degree_horizontal_y)
    return {
        "estimated_v_degree":float(estimated_v_degree),
        "estimated_h_degree":float(estimated_h_degree)
    }

def get_stage_cop_xy_horizontal_vertical(manifest):
    vertical_range = ["0", "1v", "1.5v", "2v"]
    vertical_range_degree = [float(item.rstrip("vh")) for item in vertical_range]
    horizontal_range = ["0", "1h", "2h", "3h"]
    horizontal_range_degree = [float(item.rstrip("vh")) for item in horizontal_range]
    manifest_cop_data = retrieve_inverse_design_cop_data(manifest=manifest)
    stage_count = manifest_cop_data[vertical_range[0]].shape[0]
    overall_stage_cop_xy = {
        "horizontal": {
            "stage": {stage_no:{
                "x": [],
                "y": [],
                "degree": []
                } for stage_no in range(stage_count)}
        },
        "vertical": {
            "stage": {stage_no:{
                "x": [],
                "y": [],
                "degree": []
                } for stage_no in range(stage_count)}
        }
    }
    for stage in range(stage_count):
        degree_value = []
        x_value = []
        y_value = []
        for i, degree in enumerate(vertical_range_degree):
            degree_value.append(degree)
            manifest_mould_name = vertical_range[i]
            x_value.append(manifest_cop_data[manifest_mould_name].iloc[stage]["CoP_x"])
            y_value.append(manifest_cop_data[manifest_mould_name].iloc[stage]["CoP_y"])
        overall_stage_cop_xy["vertical"]["stage"][stage]["x"] = x_value
        overall_stage_cop_xy["vertical"]["stage"][stage]["y"] = y_value
        overall_stage_cop_xy["vertical"]["stage"][stage]["degree"] = degree_value
    for stage in range(stage_count):
        degree_value = []
        x_value = []
        y_value = []
        for i, degree in enumerate(horizontal_range_degree):
            degree_value.append(degree)
            manifest_mould_name = horizontal_range[i]
            x_value.append(manifest_cop_data[manifest_mould_name].iloc[stage]["CoP_x"])
            y_value.append(manifest_cop_data[manifest_mould_name].iloc[stage]["CoP_y"])
            overall_stage_cop_xy["horizontal"]["stage"][stage]["x"] = x_value
            overall_stage_cop_xy["horizontal"]["stage"][stage]["y"] = y_value
            overall_stage_cop_xy["horizontal"]["stage"][stage]["degree"] = degree_value
    return overall_stage_cop_xy

        