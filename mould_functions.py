from math import tan, pi
from visualisation import img_height, img_width

mould_size_x = img_width 
mould_size_y = img_height

def deg2rad(deg):
    return pi*(deg/180)

def mould_0_z_magnitude(x, y):
    x = img_width-x
    y = img_height-y
    return 5

def mould_1v_z_magnitude(x, y):
    rad = deg2rad(1)
    x = img_width-x
    y = img_height-y
    return 5 + x*tan(rad)

def mould_1h_z_magnitude(x, y):
    x = img_width-x
    y = img_height-y
    rad = deg2rad(1)
    return 5 + y*tan(rad)

def mould_1dot5v_z_magnitude(x, y):
    x = img_width-x
    y = img_height-y
    rad = deg2rad(1.5)
    return 5 + x*tan(rad)

def mould_2v_z_magnitude(x, y):
    x = img_width-x
    y = img_height-y
    rad = deg2rad(2)
    return 5 + x*tan(rad)

def mould_2h_z_magnitude(x, y):
    x = img_width-x
    y = img_height-y
    rad = deg2rad(2)
    return 5 + y*tan(rad)

def mould_3h_z_magnitude(x, y):
    x = img_width-x
    y = img_height-y
    rad = deg2rad(3)
    return 5 + y*tan(rad)

mould_function_mapping = {
    "0": mould_0_z_magnitude,
    "1v": mould_1v_z_magnitude,
    "1h": mould_1h_z_magnitude,
    "1.5v": mould_1dot5v_z_magnitude,
    "2v": mould_2v_z_magnitude,
    "2h": mould_2h_z_magnitude,
    "3h": mould_3h_z_magnitude
}