from dataprocessing import serial_recording_df, serial_df_to_force_df, get_testset_listing, get_batches_listing, serial_df_to_resistance_df, serial_df_to_conductance_df, fsr_voltage_to_newtons, get_average_sensor_force_batch, get_sensor_peak_force_step, get_manifest_listing, get_mould_force_from_manifest, get_manifest_moulds, get_average_sensor_force_manifest_mould, get_sensor_peak_force_step_manifest, get_manifest_step_cop_pressure, get_manifest_overall_cop_pressure, get_cop_listing, inverse_design_find_angles, get_manifest_stacked_cop_pressure, get_stage_cop_xy_horizontal_vertical
from visualisation import plot_readings, plot_readings_with_step_indication, plot_calibration, plot_calibration_conductance, plot_calibration_resistance, plot_force_map, plot_animated_step_force_map, plot_cop, plot_mould_function, plot_insole_image, plot_stage_cop_xy_horizontal_vertical
import matplotlib.pyplot as plt
from stepsegmentation import find_step_segments
import os
import shutil
from mould_functions import mould_function_mapping
import pandas as pd
from record_serial import start_recording

def print_options(operations):
    display_options = operations.keys()
    print("------------------")
    for i, option in enumerate(display_options):
        print(f"{i}. {option}")
    print("------------------")

def user_input_option_and_execute(operations):
    operation_results = list(operations.values())
    # try: 
    user_input = input("Enter an option and press Enter: ")
    operation_results[int(user_input)]()
    # except Exception as e:
    #     print(f"Try again, error {e}")
    #     user_input_option_and_execute(operations)

def user_input_option_and_return(operations):
    operation_results = list(operations.values())
    # try: 
    user_input = input("Enter an option and press Enter: ")
    return operation_results[int(user_input)], int(user_input)
    # except Exception as e:
    #     print(f"Try again, error {e}")
    #     user_input_option_and_execute(operations)

def display_operations_and_prompt_for_user_input_and_execute(operations):
    print_options(operations)
    user_input_option_and_execute(operations)

def display_operations_and_prompt_for_user_input_and_return(operations):
    print_options(operations)
    return user_input_option_and_return(operations)

def display_individual_batch_force_recordings():
    available_testsets = {item: item for item in get_testset_listing()}
    print("Select Testset")
    (selected_testset, selected_test_user_input) = display_operations_and_prompt_for_user_input_and_return(available_testsets)
    print(f"User selected {selected_testset}")
    available_batches = {item: item for item in get_batches_listing(selected_testset)}
    print("Select Batch")
    (selected_batch, selected_batch_user_input) = display_operations_and_prompt_for_user_input_and_return(available_batches)
    print(f"User selected {selected_batch}")
    with open(f'testsets/{selected_testset}/{selected_batch}', "r") as raw_serial_data: #TODO: This should move to data processing
        serial_df = serial_recording_df(raw_serial_data)
        force_df = serial_df_to_force_df(serial_df)
        plot_readings(force_df, title=f"Batch Force Recordings \ {selected_testset} \ {selected_batch}", ylabel="N")
        plt.show()

def display_individual_batch_serial_recordings():
    available_testsets = {item: item for item in get_testset_listing()}
    print("Select Testset")
    (selected_testset, selected_testset_user_input) = display_operations_and_prompt_for_user_input_and_return(available_testsets)
    print(f"User selected {selected_testset}")
    available_batches = {item: item for item in get_batches_listing(selected_testset)}
    print("Select Batch")
    (selected_batch, selected_batch_user_input) = display_operations_and_prompt_for_user_input_and_return(available_batches)
    print(f"User selected {selected_batch}")
    with open(f'testsets/{selected_testset}/{selected_batch}', "r") as raw_serial_data: #TODO: This should move to data processing
        serial_df = serial_recording_df(raw_serial_data)
        plot_readings(serial_df, title=f"Batch Serial Recordings \ {selected_testset} \ {selected_batch}", ylabel="V")
        plt.show()

def display_individual_batch_force_recordings_step_segmentation(): 
    available_testsets = {item: item for item in get_testset_listing()}
    print("Select Testset")
    selected_testset = display_operations_and_prompt_for_user_input_and_return(available_testsets)
    print(f"User selected {selected_testset}")
    available_batches = {item: item for item in get_batches_listing(selected_testset)}
    print("Select Batch")
    selected_batch = display_operations_and_prompt_for_user_input_and_return(available_batches)
    print(f"User selected {selected_batch}")
    with open(f'testsets/{selected_testset}/{selected_batch}', "r") as raw_serial_data: #TODO: This should move to data processing
        serial_df = serial_recording_df(raw_serial_data)
        force_df = serial_df_to_force_df(serial_df)
        steps = find_step_segments(force_df)
        plot_readings_with_step_indication(force_df, steps, title=f"Batch Force Recordings \ {selected_testset} \ {selected_batch}", ylabel="N")
        plt.show()

def display_individual_step_force_recordings():
    available_testsets = {item: item for item in get_testset_listing()}
    print("Select Testset")
    (selected_testset, selected_testset_user_input) = display_operations_and_prompt_for_user_input_and_return(available_testsets)
    print(f"User selected {selected_testset}")
    available_batches = {item: item for item in get_batches_listing(selected_testset)}
    print("Select Batch")
    (selected_batch, selected_batch_user_input) = display_operations_and_prompt_for_user_input_and_return(available_batches)
    print(f"User selected {selected_batch}")
    with open(f'testsets/{selected_testset}/{selected_batch}', "r") as raw_serial_data: #TODO: This should move to data processing
        serial_df = serial_recording_df(raw_serial_data)
        force_df = serial_df_to_force_df(serial_df)
        steps = find_step_segments(force_df)
        available_steps = {f"Step {i}": item for i, item in enumerate(steps)}
        print("Select Step")
        (selected_step, selected_step_user_input) = display_operations_and_prompt_for_user_input_and_return(available_steps)
        print(f"User selected {selected_step}")
        step_df = force_df[(force_df["DateTime"] >= selected_step[0]) & (force_df["DateTime"] <= selected_step[1])]
        plot_readings(step_df, title=f"Step Force Recordings \ {selected_testset} \ {selected_batch} \ Step {selected_step_user_input}", ylabel="N")
        plt.show()


def display_individual_batch_resistance_recordings():
    available_testsets = {item: item for item in get_testset_listing()}
    print("Select Testset")
    (selected_testset, selected_testset_user_input) = display_operations_and_prompt_for_user_input_and_return(available_testsets)
    print(f"User selected {selected_testset}")
    available_batches = {item: item for item in get_batches_listing(selected_testset)}
    print("Select Batch")
    (selected_batch, selected_batch_user_input) = display_operations_and_prompt_for_user_input_and_return(available_batches)
    print(f"User selected {selected_batch}")
    with open(f'testsets/{selected_testset}/{selected_batch}', "r") as raw_serial_data: #TODO: This should move to data processing
        serial_df = serial_recording_df(raw_serial_data)
        resistance_df = serial_df_to_resistance_df(serial_df)
        plot_readings(resistance_df, title=f"Batch Resistance Recordings \ {selected_testset} \ {selected_batch}", ylabel="ohms")
        plt.show()

def display_individual_batch_conductance_recordings():
    available_testsets = {item: item for item in get_testset_listing()}
    print("Select Testset")
    (selected_testset, selected_testset_user_input) = display_operations_and_prompt_for_user_input_and_return(available_testsets)
    print(f"User selected {selected_testset}")
    available_batches = {item: item for item in get_batches_listing(selected_testset)}
    print("Select Batch")
    (selected_batch, selected_batch_user_input) = display_operations_and_prompt_for_user_input_and_return(available_batches) #TODO: Need to implement DRY
    print(f"User selected {selected_batch}")
    with open(f'testsets/{selected_testset}/{selected_batch}', "r") as raw_serial_data: #TODO: This should move to data processing
        serial_df = serial_recording_df(raw_serial_data)
        conductance_df = serial_df_to_conductance_df(serial_df)
        plot_readings(conductance_df)
        plt.show()

def display_calibration_plot():
    plot_calibration()
    plt.show()

def display_calibration_conductance_plot():
    plot_calibration_conductance()
    plt.show()

def display_calibration_resistance_plot():
    plot_calibration_resistance()
    plt.show()


def test_interpolation_based_on_voltage():
    available_channels = {f"Channel {item}": item for item in [1,2,3,4,5,6,7,8]}
    print("Select Channel")
    (selected_channel, selected_channel_user_input) = display_operations_and_prompt_for_user_input_and_return(available_channels)
    input_voltage = float(input("Enter voltage: "))
    interpolated_newtons = fsr_voltage_to_newtons(input_voltage, selected_channel)
    print(f"Interpolated newtons: {interpolated_newtons}")
    interpolated_grams = (interpolated_newtons*1000)/9.81
    print(f"Interpolated grams: {interpolated_grams}")
    plt.vlines(x=[interpolated_grams], ymin=0, ymax=[input_voltage], color='red', linewidth=1.5)
    plt.hlines(y=[input_voltage], xmin=0, xmax=[interpolated_grams], color='red', linewidth=1.5) #TODO: should be in vis
    plot_calibration()
    plt.show()

def display_individual_batch_avg_force():
    available_testsets = {item: item for item in get_testset_listing()}
    print("Select Testset")
    (selected_testset, selected_testset_user_input) = display_operations_and_prompt_for_user_input_and_return(available_testsets)
    print(f"User selected {selected_testset}")
    available_batches = {item: item for item in get_batches_listing(selected_testset)}
    print("Select Batch")
    (selected_batch, selected_batch_user_input) = display_operations_and_prompt_for_user_input_and_return(available_batches)
    print(f"User selected {selected_batch}")
    average_sensor_force_batch = get_average_sensor_force_batch(selected_testset, selected_batch)
    plot_force_map(average_sensor_force_batch, title=f"Batch Average Peak Force \ {selected_testset} \ {selected_batch}")
    plt.show()

def display_individual_step_peak_force():
    available_testsets = {item: item for item in get_testset_listing()}
    print("Select Testset")
    (selected_testset, selected_testset_user_input) = display_operations_and_prompt_for_user_input_and_return(available_testsets)
    print(f"User selected {selected_testset}")
    available_batches = {item: item for item in get_batches_listing(selected_testset)}
    print("Select Batch")
    (selected_batch, selected_batch_user_input) = display_operations_and_prompt_for_user_input_and_return(available_batches)
    print(f"User selected {selected_batch}")
    with open(f'testsets/{selected_testset}/{selected_batch}', "r") as raw_serial_data: #TODO: This should move to data processing
        serial_df = serial_recording_df(raw_serial_data)
        force_df = serial_df_to_force_df(serial_df)
        steps = find_step_segments(force_df)
        available_steps = {f"Step {i}": item for i, item in enumerate(steps)}
        print("Select Step")
        (selected_step, selected_step_user_input) = display_operations_and_prompt_for_user_input_and_return(available_steps)
        print(f"User selected {selected_step}")
        peak_sensor_force_step = get_sensor_peak_force_step(selected_testset, selected_batch, selected_step)
        plot_force_map(peak_sensor_force_step, title=f"Batch Step Peak Force \ {selected_testset} \ {selected_batch} \ Step {selected_step_user_input}")
        plt.show()

def display_animated_step_force_replay():
    available_testsets = {item: item for item in get_testset_listing()}
    print("Select Testset")
    (selected_testset, selected_testset_user_input) = display_operations_and_prompt_for_user_input_and_return(available_testsets)
    print(f"User selected {selected_testset}")
    available_batches = {item: item for item in get_batches_listing(selected_testset)}
    print("Select Batch")
    (selected_batch, selected_batch_user_input) = display_operations_and_prompt_for_user_input_and_return(available_batches)
    print(f"User selected {selected_batch}")
    with open(f'testsets/{selected_testset}/{selected_batch}', "r") as raw_serial_data: #TODO: This should move to data processing
        serial_df = serial_recording_df(raw_serial_data)
        force_df = serial_df_to_force_df(serial_df)
        steps = find_step_segments(force_df)
        available_steps = {f"Step {i}": item for i, item in enumerate(steps)}
        print("Select Step")
        (selected_step, selected_step_user_input) = display_operations_and_prompt_for_user_input_and_return(available_steps)
        print(f"User selected {selected_step}")
        frame_intervals = {
            "10 (Very fast)": 10,
            "75 (Fast)": 75,
            "50 (Normal)": 50,
            "100 (Slow)": 100,
            "200 (Very Slow)": 200
        }
        selected_frame_interval, selected_frame_interval_user_input = display_operations_and_prompt_for_user_input_and_return(frame_intervals)
        ani = plot_animated_step_force_map(selected_testset, selected_batch, selected_step_user_input, frame_interval=selected_frame_interval, title=f"Step Force Replay \ {selected_testset} \ {selected_batch} \ Step {selected_step_user_input}")
        plt.show()

def display_manifest_mould_force_recordings(selected_manifest=None, selected_mould = None, display=True, precomputed_steps=None):
    if(selected_manifest == None):
        available_manifests = {item: item for item in get_manifest_listing()}
        print("Select Manifest")
        (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
        print(f"User selected {selected_manifest}")
    if(selected_mould == None):
        available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
        (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
        print(f"User selected {selected_mould}")
    force_df = get_mould_force_from_manifest(selected_mould, selected_manifest)
    steps = precomputed_steps
    if(not precomputed_steps):
        steps = find_step_segments(force_df)
    readings = plot_readings_with_step_indication(force_df, steps, title=f"Manifest Mould Force Recordings \ {selected_manifest} \ {selected_mould}", ylabel="N")
    if(display):
        plt.show()
    return readings

def display_manifest_individual_step_force_recordings(selected_manifest=None, selected_mould = None, step_df = None, display=True):
    if(selected_manifest == None):
        available_manifests = {item: item for item in get_manifest_listing()}
        print("Select Manifest")
        (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
        print(f"User selected {selected_manifest}")
    if(selected_mould == None):
        available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
        (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
        print(f"User selected {selected_mould}")
    if(step_df is None):
        force_df = get_mould_force_from_manifest(selected_mould, selected_manifest)
        steps = find_step_segments(force_df)
        available_steps = {f"Step {i}": item for i, item in enumerate(steps)}
        print("Select Step")
        (selected_step, selected_step_user_input) = display_operations_and_prompt_for_user_input_and_return(available_steps)
        print(f"User selected {selected_step}")
        step_df = force_df[(force_df["DateTime"] >= selected_step[0]) & (force_df["DateTime"] <= selected_step[1])]
    readings = plot_readings(step_df, title=f"Manifest Step Force Recordings \ {selected_manifest} \ {selected_mould} \ Step", ylabel="N")
    if(display):
        plt.show()
    return readings

def display_individual_manifest_mould_avg_force(selected_manifest=None, selected_mould = None, display=True, precomputed_steps=None):
    # available_testsets = {item: item for item in get_testset_listing()}
    # print("Select Testset")
    # (selected_testset, selected_testset_user_input) = display_operations_and_prompt_for_user_input_and_return(available_testsets)
    # print(f"User selected {selected_testset}")
    # available_batches = {item: item for item in get_batches_listing(selected_testset)}
    # print("Select Batch")
    # (selected_batch, selected_batch_user_input) = display_operations_and_prompt_for_user_input_and_return(available_batches)
    # print(f"User selected {selected_batch}")
    available_manifests = {item: item for item in get_manifest_listing()}
    if(selected_manifest == None):
        print("Select Manifest")
        (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
        print(f"User selected {selected_manifest}")
    if(selected_mould == None):
        available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
        (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
        print(f"User selected {selected_mould}")
    average_sensor_force_batch = get_average_sensor_force_manifest_mould(selected_mould, selected_manifest)
    force_map = plot_force_map(average_sensor_force_batch, title=f"Manifest Mould Average Peak Force \ {selected_manifest} \ {selected_mould}")
    if(display):
        plt.show()
    return force_map

def display_individual_manifest_mould_step_peak_force(selected_manifest=None, selected_mould = None, selected_step = None, display=True, precomputed_steps=None):
    available_manifests = {item: item for item in get_manifest_listing()}
    if(selected_manifest == None):
        print("Select Manifest")
        (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
        print(f"User selected {selected_manifest}")
    if(selected_mould == None):
        available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
        (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
        print(f"User selected {selected_mould}")
    if(selected_step == None):
        force_df = get_mould_force_from_manifest(selected_mould, selected_manifest)
        steps = find_step_segments(force_df)
        available_steps = {f"Step {i}": item for i, item in enumerate(steps)}
        print("Select Step")
        (selected_step, selected_step_user_input) = display_operations_and_prompt_for_user_input_and_return(available_steps)
        print(f"User selected {selected_step}")
    peak_sensor_force_step = get_sensor_peak_force_step_manifest(selected_manifest, selected_mould, selected_step, precomputed_steps)
    force_map = plot_force_map(peak_sensor_force_step, title=f"Manifest Step Peak Force \ {selected_manifest} \ {selected_mould}")
    if(display):
        plt.show()
    return force_map

def batch_export_manifest():
    available_manifests = {item: item for item in get_manifest_listing()}
    print("Select Manifest")
    (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
    print(f"User selected {selected_manifest}")
    manifest_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
    print(f"Batch Export for {selected_manifest} Manifest")
    print("Setting up directories...")
    selected_manifest_no_extension = selected_manifest[:-5]
    os.makedirs("export", exist_ok=True)
    if(os.path.isdir(f"export/{selected_manifest_no_extension}")):
        shutil.rmtree(f"export/{selected_manifest_no_extension}", ignore_errors=True)
    os.mkdir(f"export/{selected_manifest_no_extension}")
    for mould in manifest_moulds:
        force_df = get_mould_force_from_manifest(mould, selected_manifest)
        steps = find_step_segments(force_df)
        os.mkdir(f"export/{selected_manifest_no_extension}/{mould}")
        os.mkdir(f"export/{selected_manifest_no_extension}/{mould}/steps")
        for i, step in enumerate(steps):
            os.mkdir(f"export/{selected_manifest_no_extension}/{mould}/steps/Step{i}")
    print("Saving csvs...")
    for mould in manifest_moulds:
        print(mould)
        force_df = get_mould_force_from_manifest(mould, selected_manifest)
        force_df.to_csv(f"export/{selected_manifest_no_extension}/{mould}/raw_force_readings.csv")
        overall_cop_df = get_manifest_overall_cop_pressure(manifest=selected_manifest, mould=mould)
        overall_cop_df.to_csv(f"export/{selected_manifest_no_extension}/{mould}/cop.csv")
        steps = find_step_segments(force_df)
        for i, step in enumerate(steps):
            step_df = force_df[(force_df["DateTime"] >= step[0]) & (force_df["DateTime"] <= step[1])]
            step_df.to_csv(f"export/{selected_manifest_no_extension}/{mould}/steps/Step{i}/raw_force_readings.csv")
    print("Generating overall plots...")
    for mould in manifest_moulds:
        print(mould)
        force_df = get_mould_force_from_manifest(mould, selected_manifest)
        steps = find_step_segments(force_df)
        fig = display_manifest_mould_force_recordings(selected_manifest=selected_manifest, selected_mould = mould, display=False, precomputed_steps=steps)
        fig.savefig(f"export/{selected_manifest_no_extension}/{mould}/{selected_manifest_no_extension}_{mould}_force_recordings.png")
        plt.close(fig)
        fig = display_individual_manifest_mould_avg_force(selected_manifest=selected_manifest, selected_mould = mould, display=False)
        fig.savefig(f"export/{selected_manifest_no_extension}/{mould}/{selected_manifest_no_extension}_{mould}_peak_force.png")
        plt.close(fig)
        fig = display_individual_manifest_mould_overall_cop(selected_manifest=selected_manifest, selected_mould = mould, display=False)
        fig.savefig(f"export/{selected_manifest_no_extension}/{mould}/{selected_manifest_no_extension}_{mould}_cop.png")
        plt.close(fig)
    print("Generating step plots... (takes a while)")
    for mould in manifest_moulds:
        print(mould)
        force_df = get_mould_force_from_manifest(mould, selected_manifest)
        steps = find_step_segments(force_df)
        for i, step in enumerate(steps):
            step_df = force_df[(force_df["DateTime"] >= step[0]) & (force_df["DateTime"] <= step[1])]
            fig = display_manifest_individual_step_force_recordings(selected_manifest=selected_manifest, selected_mould = mould, step_df=step_df, display=False)
            fig.savefig(f"export/{selected_manifest_no_extension}/{mould}/steps/Step{i}/{selected_manifest_no_extension}_{mould}_step{i}_force_recordings.png")
            plt.close(fig)
            fig = display_individual_manifest_mould_step_peak_force(selected_manifest=selected_manifest, selected_mould = mould, selected_step = step, display=False, precomputed_steps=steps)
            fig.savefig(f"export/{selected_manifest_no_extension}/{mould}/steps/Step{i}/{selected_manifest_no_extension}_{mould}_step{i}_peak_force.png")
            plt.close(fig)

def display_probability_matrix():
    available_manifests = {item: item for item in get_manifest_listing()}
    print("Select Manifest")
    (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
    print(f"User selected {selected_manifest}")
    available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
    (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
    print(f"User selected {selected_mould}")
    force_df = get_mould_force_from_manifest(selected_mould, selected_manifest)
    steps = find_step_segments(force_df)
    available_steps = {f"Step {i}": item for i, item in enumerate(steps)}
    # print("Select Step")
    # (selected_step, selected_step_user_input) = display_operations_and_prompt_for_user_input_and_return(available_steps)
    # print(f"User selected {selected_step}")
    transition_matrix = get_manifest_mould_transition_matrix(selected_manifest, selected_mould)
    initial_matrix = get_manifest_step_probability_initial(selected_manifest, selected_mould)
    print("transition matrix")
    print(transition_matrix)
    print("initial matrix")
    print(initial_matrix)

def plot_probability_cop():
    available_manifests = {item: item for item in get_manifest_listing()}
    print("Select Manifest")
    (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
    print(f"User selected {selected_manifest}")
    available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
    (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
    print(f"User selected {selected_mould}")
    peak_sensor_force_step = get_average_sensor_force_manifest_mould(manifest=selected_manifest, mould=selected_mould)
    cop_path = get_overall_cop_manifest_mould_probability(manifest=selected_manifest, mould=selected_mould)
    force_map = plot_force_map(peak_sensor_force_step, title=f"Manifest Step CoP Probability \ {selected_manifest} \ {selected_mould}")
    plot_cop(cop_path)
    plt.show()


def display_individual_manifest_mould_step_cop(selected_manifest=None, selected_mould = None, selected_step = None, display=True, precomputed_steps=None):
    available_manifests = {item: item for item in get_manifest_listing()}
    if(selected_manifest == None):
        print("Select Manifest")
        (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
        print(f"User selected {selected_manifest}")
    if(selected_mould == None):
        available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
        (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
        print(f"User selected {selected_mould}")
    if(selected_step == None):
        force_df = get_mould_force_from_manifest(selected_mould, selected_manifest)
        steps = find_step_segments(force_df)
        available_steps = {f"Step {i}": item for i, item in enumerate(steps)}
        print("Select Step")
        (selected_step, selected_step_user_input) = display_operations_and_prompt_for_user_input_and_return(available_steps)
        print(f"User selected {selected_step}")
    peak_sensor_force_step = get_sensor_peak_force_step_manifest(selected_manifest, selected_mould, selected_step, precomputed_steps)
    force_map = plot_force_map(peak_sensor_force_step, title=f"Manifest Step CoP \ {selected_manifest} \ {selected_mould}")
    cop_df = get_manifest_step_cop_pressure(selected_manifest, selected_mould, selected_step)
    plot_cop(cop_df=cop_df)
    if(display):
        plt.show()
    return force_map

def display_individual_manifest_mould_stacked_cop(selected_manifest=None, selected_mould = None, display=True):
    available_manifests = {item: item for item in get_manifest_listing()}
    if(selected_manifest == None):
        print("Select Manifest")
        (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
        print(f"User selected {selected_manifest}")
    if(selected_mould == None):
        available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
        (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
        print(f"User selected {selected_mould}")
    peak_sensor_force_step = get_average_sensor_force_manifest_mould(manifest=selected_manifest, mould=selected_mould)
    force_map = plot_force_map(peak_sensor_force_step, title=f"Manifest Overall CoP \ {selected_manifest} \ {selected_mould}")
    overall_cop_df = get_manifest_overall_cop_pressure(mould=selected_mould, manifest=selected_manifest)
    stacked_cop_df = get_manifest_stacked_cop_pressure(mould=selected_mould, manifest=selected_manifest)
    print(overall_cop_df)
    plot_cop(overall_cop_df)
    for i in range(0, len(stacked_cop_df), 10):
        step_cop = stacked_cop_df.iloc[i : i + 10]
        plot_cop(step_cop, color="yellow", alpha=0.2)
    if(display):
        plt.show()
    return force_map

def display_individual_manifest_mould_overall_cop(selected_manifest=None, selected_mould = None, display=True):
    available_manifests = {item: item for item in get_manifest_listing()}
    if(selected_manifest == None):
        print("Select Manifest")
        (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
        print(f"User selected {selected_manifest}")
    if(selected_mould == None):
        available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
        (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
        print(f"User selected {selected_mould}")
    peak_sensor_force_step = get_average_sensor_force_manifest_mould(manifest=selected_manifest, mould=selected_mould)
    force_map = plot_force_map(peak_sensor_force_step, title=f"Manifest Overall CoP \ {selected_manifest} \ {selected_mould}")
    overall_cop_df = get_manifest_overall_cop_pressure(mould=selected_mould, manifest=selected_manifest)
    print(overall_cop_df)
    plot_cop(overall_cop_df)
    if(display):
        plt.show()
    return force_map

def display_mould_z_pattern(selected_manifest = None, selected_mould_function = None):
    available_manifests = {item: item for item in get_manifest_listing()}
    if(selected_manifest == None):
        print("Select Manifest")
        (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
        print(f"User selected {selected_manifest}")
    if(selected_mould_function == None):
        available_moulds = {item: item for item in get_manifest_moulds(selected_manifest) if item in mould_function_mapping.keys()}
        (selected_mould_function, selected_mould_function_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
        print(f"User selected {selected_mould_function}")
    plot_mould_function(mould_function_mapping[selected_mould_function], title = f"Mould Function Display {selected_mould_function}")
    plt.show()

def display_manifest_mould_joint_probability_distribution():
    available_manifests = {item: item for item in get_manifest_listing()}
    print("Select Manifest")
    (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
    print(f"User selected {selected_manifest}")
    available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
    (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
    print(f"User selected {selected_mould}")
    jd = get_overall_joint_probability_distribution(selected_manifest, selected_mould)
    plot_mould_joint_distribution_probability(jd)
    plt.show()

def create_desired_cop():
    desired_cop = []
    for i in range(10):
        stage_xy = input(f"Please enter x, y ({i+1}): ")
        stage_xy_split_by_comma = stage_xy.split(",")
        desired_cop.append([int(stage_xy_split_by_comma[0]), int(stage_xy_split_by_comma[1])])
    print("Entered CoP: ")
    print(desired_cop)
    filename_to_save = input("Please enter filename to save: ")
    with open(f"desired_cops/{filename_to_save}.csv", "w") as desired_cop_file:
        desired_cop_file.write("stage,x,y\n")
        for i, coord in enumerate(desired_cop):
            desired_cop_file.write(f"{i},{coord[0]},{coord[1]}\n")

def display_desired_cop():
    available_cops = {item: item for item in get_cop_listing()}
    print("Select CoP")
    (selected_cop, selected_cop_user_input) = display_operations_and_prompt_for_user_input_and_return(available_cops)
    print(f"User selected {selected_cop}")
    desired_cop = []
    with open(f"desired_cops/{selected_cop}", "r") as desired_cop_file:
        for i, line in enumerate(desired_cop_file.readlines()):
            if(i == 0):
                continue
            coords = line.split(",")
            desired_cop.append([int(coords[1]), int(coords[2])])
    print("Plotting...")
    print(desired_cop)
    desired_cop_df = pd.DataFrame(desired_cop, columns=["CoP_x", "CoP_y"])
    plot_insole_image()
    plot_cop(desired_cop_df)
    plt.show()

def display_step_probability_cop():
    available_manifests = {item: item for item in get_manifest_listing()}
    print("Select Manifest")
    (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
    print(f"User selected {selected_manifest}")
    available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
    (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
    print(f"User selected {selected_mould}")
    force_df = get_mould_force_from_manifest(selected_mould, selected_manifest)
    steps = find_step_segments(force_df)
    available_steps = {f"Step {i}": item for i, item in enumerate(steps)}
    print("Select Step")
    (selected_step, selected_step_user_input) = display_operations_and_prompt_for_user_input_and_return(available_steps)
    print(f"User selected {selected_step}")
    prob_cop = get_probability_based_cop_step(selected_mould, selected_manifest, selected_step)
    plot_insole_image()
    print(prob_cop)
    plot_cop(prob_cop)
    plt.title(f"Prob CoP Step - {selected_manifest} - {selected_mould} - {selected_step}")
    plt.show()

def display_probability_cop():
    available_manifests = {item: item for item in get_manifest_listing()}
    print("Select Manifest")
    (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
    print(f"User selected {selected_manifest}")
    available_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
    (selected_mould, selected_mould_user_input) = display_operations_and_prompt_for_user_input_and_return(available_moulds)
    print(f"User selected {selected_mould}")
    prob_cop = get_probability_based_cop(selected_mould, selected_manifest)
    print(prob_cop)
    plot_insole_image()
    plot_cop(prob_cop)
    plt.title(f"Prob CoP - {selected_manifest} - {selected_mould}")
    plt.show()

def batch_export_normalised_cop_for_inverse_design():
    available_manifests = {item: item for item in get_manifest_listing()}
    print("Select Manifest")
    (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
    print(f"User selected {selected_manifest}")
    manifest_moulds = {item: item for item in get_manifest_moulds(selected_manifest)}
    print(f"Batch Export for {selected_manifest} Manifest")
    print("Setting up directories...")
    selected_manifest_no_extension = selected_manifest[:-5]
    os.makedirs("inverse_design_cop", exist_ok=True)
    if(os.path.isdir(f"inverse_design_cop/{selected_manifest_no_extension}")):
        shutil.rmtree(f"inverse_design_cop/{selected_manifest_no_extension}", ignore_errors=True)
    os.mkdir(f"inverse_design_cop/{selected_manifest_no_extension}")
    for mould in manifest_moulds:
        force_df = get_mould_force_from_manifest(mould, selected_manifest)
        steps = find_step_segments(force_df)
        os.mkdir(f"inverse_design_cop/{selected_manifest_no_extension}/{mould}")
    print("Saving csvs...")
    for mould in manifest_moulds:
        print(mould)
        force_df = get_mould_force_from_manifest(mould, selected_manifest)
        overall_cop_df = get_manifest_overall_cop_pressure(mould=mould, manifest=selected_manifest)
        overall_cop_df.to_csv(f"inverse_design_cop/{selected_manifest_no_extension}/{mould}/cop.csv", columns=["CoP_x", "CoP_y"], index_label="stage")

def calculate_angles_inverse_design_linear_interpolation_for_desired_cop():
    available_manifests = {item: item for item in get_manifest_listing()}
    print("Select Manifest")
    (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
    print(f"User selected {selected_manifest}")
    available_cops = {item: item for item in get_cop_listing()}
    print("Select CoP")
    (selected_cop, selected_cop_user_input) = display_operations_and_prompt_for_user_input_and_return(available_cops)
    print(f"User selected {selected_cop}")
    desired_cop = []
    with open(f"desired_cops/{selected_cop}", "r") as desired_cop_file:
        for i, line in enumerate(desired_cop_file.readlines()):
            if(i == 0):
                continue
            coords = line.split(",")
            desired_cop.append([int(coords[1]), int(coords[2])])
    print("Producing inverse design for desired CoP: ")
    print(desired_cop)
    desired_cop_df = pd.DataFrame(desired_cop, columns=["CoP_x", "CoP_y"])
    estimated = inverse_design_find_angles(desired_cop_df, manifest=selected_manifest)
    print("Estimated Vertical Degree: ")
    print(estimated["estimated_v_degree"])
    print("Estimated Horizontal Degree: ")
    print(estimated["estimated_h_degree"])

def display_stage_cop_xy_horizontal_vertical():
    available_manifests = {item: item for item in get_manifest_listing()}
    print("Select Manifest")
    (selected_manifest, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_manifests)
    print(f"User selected {selected_manifest}")
    available_orientations = {item: item for item in ["vertical", "horizontal"]}
    print("Select Orientation")
    (selected_orientation, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_orientations)
    print(f"User selected {selected_orientation}")
    available_coordinates = {item: item for item in ["x", "y"]}
    print("Select Coordinate")
    (selected_coordinate, selected_manifest_user_input) = display_operations_and_prompt_for_user_input_and_return(available_coordinates)
    print(f"User selected {selected_coordinate}")
    stage_cop_xy_horizontal_vertical_obj = get_stage_cop_xy_horizontal_vertical(selected_manifest)
    plot_stage_cop_xy_horizontal_vertical(stage_cop_xy_horizontal_vertical_obj, selected_orientation, selected_coordinate)
    plt.show()

INITIAL_MENU_OPERATIONS = {
    "Record a serial recording from ADS1256": start_recording,
    "Display an individual batch's raw serial recordings": display_individual_batch_serial_recordings,
    "Display an individual batch's resistance recordings": display_individual_batch_resistance_recordings,
    "Display an individual batch's conductance recordings": display_individual_batch_conductance_recordings,
    "Display an individual batch's force recordings": display_individual_batch_force_recordings,
    "Display an individual batch's step segmentation": display_individual_batch_force_recordings_step_segmentation,
    "Display an individual step's force recordings": display_individual_step_force_recordings,
    "Display calibration plot": display_calibration_plot,
    "Display calibration conductance plot": display_calibration_conductance_plot,
    "Display calibration resistance plot": display_calibration_resistance_plot,
    "Test interpolation based on voltage -> g plot": test_interpolation_based_on_voltage,
    "Display batch average force peak plot": display_individual_batch_avg_force,
    "Display step force peak plot": display_individual_step_peak_force,
    "Animated step force replay": display_animated_step_force_replay,
    "Diplay manifest mould force recordings": display_manifest_mould_force_recordings,
    "Display manifest individual step force recordings": display_manifest_individual_step_force_recordings,
    "Display manifest mould force map": display_individual_manifest_mould_avg_force,
    "Display manifest mould step peak force": display_individual_manifest_mould_step_peak_force,
    "Batch export manifest": batch_export_manifest,
    # "Generate step probability matrix": display_probability_matrix,
    "Display manifest mould step CoP": display_individual_manifest_mould_step_cop,
    "Display manifest mould CoP": display_individual_manifest_mould_overall_cop,
    "Display mould z pattern": display_mould_z_pattern,
    # "Display manifest mould CoP probability": plot_probability_cop,
    # "Display manifest mould joint distribution probability": display_manifest_mould_joint_probability_distribution,
    "Create desired CoP": create_desired_cop,
    "Display desired CoP": display_desired_cop,
    # "Display step prob CoP": display_step_probability_cop,
    # "Display prob CoP": display_probability_cop,
    "Batch export normalized CoP for inverse design": batch_export_normalised_cop_for_inverse_design,
    "Inverse Design based on desired CoP": calculate_angles_inverse_design_linear_interpolation_for_desired_cop,
    "Display manifest mould CoP with steps": display_individual_manifest_mould_stacked_cop,
    "Display stage cop xy horizontal vertical": display_stage_cop_xy_horizontal_vertical,
}

if __name__ == '__main__':
    print("Freddie Nicholson MEng Insole CAD Generation Master's Project")
    print("What would you like to do?")
    display_operations_and_prompt_for_user_input_and_execute(INITIAL_MENU_OPERATIONS)
