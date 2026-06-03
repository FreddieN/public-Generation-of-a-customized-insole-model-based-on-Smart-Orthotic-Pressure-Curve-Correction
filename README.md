# Freddie Nicholson MEng Orthotic Insole Master's Project

This repository contains the Command Line Interface used for data analysis within the Master's project and the original raw testset data recorded from the dynamic walker.

The CLI allows you run the following operations on the master's dataset: 

0. Record a serial recording from ADS1256
1. Display an individual batch's raw serial recordings
2. Display an individual batch's resistance recordings
3. Display an individual batch's conductance recordings
4. Display an individual batch's force recordings
5. Display an individual batch's step segmentation
6. Display an individual step's force recordings
7. Display calibration plot
8. Display calibration conductance plot
9. Display calibration resistance plot
10. Test interpolation based on voltage -> g plot
11. Display batch average force peak plot
12. Display step force peak plot
13. Animated step force replay
14. Diplay manifest mould force recordings
15. Display manifest individual step force recordings
16. Display manifest mould force map
17. Display manifest mould step peak force
18. Batch export manifest
19. Display manifest mould step CoP
20. Display manifest mould CoP
21. Display mould z pattern
22. Create desired CoP
23. Display desired CoP
24. Batch export normalized CoP for inverse design
25. Inverse Design based on desired CoP
26. Display manifest mould CoP with steps
27. Display stage cop xy horizontal vertical
28. Display manifest mould RMSE step vs mean
29. Display manifest moulds RMSE step vs mean
30. Display repeatability plot for manifest

# Installation
1. Clone the repo to your local device
2. Create a virtual environment with `python -m venv venv` and activate the environment based on your operating system.
3. Navigate to the project directory, install requirements with `pip install -r requirements.txt`
4. Run the CLI with `python cli.py`

# Project Structure
* cli.py - Contains the main user interface for using the application
* dataprocessing.py - Used for all data processing including manifest handling, CoP calculations and repeatability calculations.
* constants.py - Contains constants such as the sensor coordinates
* mould_functions.py - Stores the mould functions for visualising the geometry of the moulds.
* record_serial.py - Used for recording readings from the ADS1256 fitted to the dynamic walker.
* stepsegmentation.py - Used for segmenting steps within each recording.
* visualisation.py - Visualises the processed data using Matplotlib

* ESP32-Firmware - The firmware adapted from CuriousScientist used as a datalogger for the ADS1256 on the ESP32
* assets - Insole image
* calibrations - Stores calibration data of the FSRs
* desired_cops - Stores the desired CoPs entered into the program for inverse design
* manifests - Stores the JSON manifest files that are used for sorting the testset batches into individual insole trials.