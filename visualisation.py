import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from dataprocessing import get_calibration_df, get_calibration_df_conductance, get_calibration_df_resistance, get_datasheet_df_resistance, get_step_segment_force_df
import matplotlib.animation as animation
from constants import sensor_coords
import seaborn as sns
import matplotlib.pyplot as plt

def plot_readings(data_df, title=None, ylabel=None):
    fig, axs = plt.subplots(8)
    data_time = data_df['DateTime']
    axs[0].plot(data_time, data_df["Channel1"])
    axs[1].plot(data_time, data_df["Channel2"])
    axs[2].plot(data_time, data_df["Channel3"])
    axs[3].plot(data_time, data_df["Channel4"])
    axs[4].plot(data_time, data_df["Channel5"])
    axs[5].plot(data_time, data_df["Channel6"])
    axs[6].plot(data_time, data_df["Channel7"])
    axs[7].plot(data_time, data_df["Channel8"])

    if(title):
        fig.suptitle(title)
    else:
        fig.suptitle("Channel Data Readings")
    axs[-1].set_xlabel("Time")
    if ylabel:
        fig.supylabel(ylabel) 
    fig.set_size_inches(14, 9)
    fig.tight_layout() 
    return fig

def plot_readings_with_step_indication(data_df, steps, title=None, ylabel=None):
    fig, axs = plt.subplots(9)
    data_time = data_df['DateTime']
    axs[0].plot(data_time, data_df["Channel1"])
    axs[1].plot(data_time, data_df["Channel2"])
    axs[2].plot(data_time, data_df["Channel3"])
    axs[3].plot(data_time, data_df["Channel4"])
    axs[4].plot(data_time, data_df["Channel5"])
    axs[5].plot(data_time, data_df["Channel6"])
    axs[6].plot(data_time, data_df["Channel7"])
    axs[7].plot(data_time, data_df["Channel8"])
    axs[8].plot(data_time, data_df["Channel8"])
    for step in steps:
        plt.axvline(x = step[0], color = 'g')
        plt.axvline(x = step[1], color = 'r')

    if(title):
        fig.suptitle(title)
    else:
        fig.suptitle("Channel Data Readings with Step Indication")
    axs[-1].set_xlabel("Time")
    if ylabel:
        fig.supylabel(ylabel) 
    fig.set_size_inches(14, 9)
    fig.tight_layout() 
    return fig

def plot_calibration():
    calibration_df = get_calibration_df()
    channel_cols = [1,2,3,4,5,6,7,8]
    for col in channel_cols:
        plt.plot(list(calibration_df["g"]), list(calibration_df[str(col)]), label=f"Channel {col}")
    plt.legend()
    plt.title("Calibration Curve")
    plt.xlabel("Weight (g)")
    plt.ylabel("Voltage (V)")

def plot_calibration_conductance():
    calibration_df = get_calibration_df_conductance()
    channel_cols = [1,2,3,4,5,6,7,8]
    for col in channel_cols:
        plt.plot(list(calibration_df["g"]), list(calibration_df[str(col)]), label=f"Channel {col}")
    plt.legend()
    plt.title("Calibration Curve Conductance")
    plt.xlabel("Weight (g)")
    plt.ylabel("Conductance (S)")

def plot_calibration_resistance():
    calibration_df = get_calibration_df_resistance()
    datasheet_df = get_datasheet_df_resistance()
    channel_cols = [1,2,3,4,5,6,7,8]
    for col in channel_cols:
        plt.plot(list(calibration_df["g"]), list(calibration_df[str(col)]), label=f"Channel {col}")
    plt.plot(list(datasheet_df["g"]), list(datasheet_df["datasheet"]), label=f"Datasheet", color='black', linestyle='dashed')
    plt.legend()
    plt.title("Calibration Curve Resistance")
    plt.xlabel("Weight (g)")
    plt.ylabel("Resistance (ohms)")

insole_background = plt.imread("assets/insole_perspective_transform.png")

def plot_insole_image():
    fig, ax = plt.subplots()        
    ax.imshow(insole_background, extent=[0, 220, 70, 0])
    for sensor, coords in sensor_coords.items():
        plt.plot([coords[0]], [coords[1]], marker='x', markersize=3, label=f"Channel {sensor}")
        plt.text(coords[0]-5, coords[1]+8, str(sensor), fontsize=14, color="white")

    # plt.legend()
    return fig, ax

img_width = 220
img_height = 70

def plot_force_map(force_sensor_readings, title=None):
    fig, ax = plot_insole_image()
    X = [coord[0] for coord in sensor_coords.values()]
    Y = [coord[1] for coord in sensor_coords.values()]
    Z = list(force_sensor_readings)
    X.extend([0, img_width, 0, img_width])
    Y.extend([0, 0, img_height, img_height])
    Z.extend([0, 0, 0, 0]) #make it cover whole image

    fixed_levels = np.linspace(0, 12, 16)

    CS = ax.tricontourf(X, Y, Z, levels=fixed_levels, alpha=0.7, vmin=0, vmax=12, cmap='inferno')
    CS.set_clim(0, 12)
    cbar = plt.colorbar(CS, ax=ax, shrink=0.8)
    cbar.ax.set_ylabel('Force (N)', rotation=270)

    for i in range(8):
        ax.annotate(f'Ch{i+1}\n{Z[i]:.4f}',
                    (sensor_coords[i+1][0], sensor_coords[i+1][1]),
                    textcoords="offset points",
                    xytext=(0, 15),
                    ha='center',
                    color='white',
                    fontweight='bold',
                    bbox=dict(facecolor='black', alpha=0.5, boxstyle='round,pad=0.2'))
    if(title):
        fig.suptitle(title)
    else:
        fig.suptitle("Channel Force Map")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    fig.set_size_inches(14, 9)
    fig.tight_layout() 
    return fig

def plot_animated_step_force_map(testset, batch, selected_step, title, frame_interval=50):
    fig, ax = plot_insole_image()
    if(title):
        fig.suptitle(title)
    else:
        fig.suptitle("Step Force Replay")
    X = [coord[0] for coord in sensor_coords.values()]
    Y = [coord[1] for coord in sensor_coords.values()]
    Z = [0] * 8  

    X.extend([0, img_width, 0, img_width])
    Y.extend([0, 0, img_height, img_height])
    Z.extend([0, 0, 0, 0])

    fixed_levels = np.linspace(0, 12, 16)

    CS = ax.tricontourf(X, Y, Z, levels=fixed_levels, alpha=0.7, vmin=0, vmax=12, cmap='inferno')
    CS.set_clim(0, 12)
    cbar = plt.colorbar(CS, ax=ax, shrink=0.8)
    cbar.ax.set_ylabel('Force (N)', rotation=270)
        
    annotations = []
    for i in range(8):
        ann = ax.annotate(f'Ch{i+1}\n{Z[i]:.4f}',
                    (sensor_coords[i+1][0], sensor_coords[i+1][1]),
                    textcoords="offset points", xytext=(0, 15), ha='center', color='white',
                    fontweight='bold', bbox=dict(facecolor='black', alpha=0.5, boxstyle='round,pad=0.2'))
        annotations.append(ann)

    step_force_df = get_step_segment_force_df(testset, batch, selected_step)

    def update(frame):        
        nonlocal CS
        current_row = step_force_df.iloc[frame]
        new_Z = [current_row[f'Channel{i}'] for i in range(1, 9)]
        new_Z.extend([0, 0, 0, 0]) # Keep corners at 0
        
        CS.remove()

        CS = ax.tricontourf(X, Y, new_Z, levels=fixed_levels, alpha=0.7, vmin=0, vmax=12, cmap='inferno')

        for i in range(8):
            annotations[i].set_text(f'Ch{i+1}\n{new_Z[i]:.2f}')
            
        return [CS] + annotations

    ani = animation.FuncAnimation(fig=fig, func=update, frames=len(step_force_df), interval=frame_interval, blit=True)
    return ani

def plot_probability_grid():
    fig, ax = plot_insole_image()

    y_bottom, y_top = ax.get_ylim()
    y_spacing = img_height / 3

    grid_start = [45, min(y_bottom, y_top) + y_spacing]
    x_spacing = 35
    grid_cols = 4
    grid_rows = 2

    for col in range(grid_cols + 2):
        plt.axvline(x=grid_start[0] + x_spacing*col, color='b')
        if(col < grid_cols):
            plt.text(grid_start[0] + (x_spacing)*col + x_spacing/2, grid_start[1]-25, chr(65+col), fontsize=14, color="red")
    for row in range(grid_rows+1):
        plt.axhline(y=grid_start[1] + y_spacing*row, color='b')
        plt.text(grid_start[0]-20, grid_start[1] + (y_spacing)*row - (y_spacing/2), str(row+1), fontsize=14, color="red")

    return fig, ax

def plot_cop(cop_df, color="green", alpha=1):
    plt.plot(cop_df["CoP_x"], cop_df["CoP_y"], label=f"Center of Pressure", color=color, alpha=alpha)

def plot_mould_function(mould_function, title = None):
    fig, ax = plot_insole_image()
    if(title):
        fig.suptitle(title)
    else:
        fig.suptitle("Mould Function Display")
    resolution = 10
    grid = [[x for x in range(0, img_width+resolution, resolution)] for y in range(0, img_height+resolution, resolution)]
    
    z_height_x = []
    z_height_y = []
    z_height_z = []

    for i, row in enumerate(grid):
        y_coord = i * resolution 
        for x_coord in row:
            # plt.plot(x_coord, y_coord, 'go', markersize=2)
            z_height_x.append(x_coord)
            z_height_y.append(y_coord)
            z_height_z.append(mould_function(x_coord,y_coord))
    fixed_levels = np.linspace(0, 15, 30)

    CS = ax.tricontourf(z_height_x, z_height_y, z_height_z, levels=fixed_levels, alpha=0.7, vmin=0, vmax=12, cmap='inferno')
    CS.set_clim(0, 12)
    cbar = plt.colorbar(CS, ax=ax, shrink=0.8)
    cbar.ax.set_ylabel('Height Z (mm)', rotation=270)

def plot_stage_cop_xy_horizontal_vertical(stage_cop_xy_horizontal_vertical_obj, orientation, coordinate):
    for stage in stage_cop_xy_horizontal_vertical_obj[orientation]['stage'].keys():
        stage_obj = stage_cop_xy_horizontal_vertical_obj[orientation]['stage'][stage]
        plt.plot(stage_obj["degree"], stage_obj[coordinate], label=f"Stage {stage}")
    plt.xlabel("Degree")
    plt.ylabel(f"{coordinate} (mm)")
    plt.title(f"{orientation} orientation / {coordinate} coordinate")
    plt.legend()
