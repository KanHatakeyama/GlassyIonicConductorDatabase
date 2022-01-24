import numpy as np
import copy
import re


def make_electrolyte_name(target_str):
    array = target_str[1:].split(":")

    array[0] = array[0].replace('nan', "")
    array[1] = array[1].replace('nan', "")

    array[0] = array[0].replace('136.03', "S")
    array[0] = array[0].replace('120.15', "O")

    array[1] = array[1].replace('245.86', "L")  # chloranil
    array[1] = array[1].replace('108.1', "Q")  # BQ
    array[1] = array[1].replace('423.68', "R")  # bromanil
    array[1] = array[1].replace('227.0', "D")  # DDQ

    array[2] = array[2].replace('287.08', "D")  # TFSI
    array[2] = array[2].replace('237.07', "M")  # F-TFSI
    array[2] = array[2].replace('187.06', "N")  # FSI
    array[2] = array[2].replace('93.74', "B")  # bf4

    """
    array[3]="{:.2f}".format(float(array[3]))
    array[4]="{:.2f}".format(float(array[4]))
    """

    if float(array[3]) == 0:
        array[3] = ""
    else:
        array[3] = "{:.0f}".format(float(array[3])*100)+"-"

    array[4] = "{:.0f}".format(float(array[4])*100)

    # anneal
    array[5] = str(array[5]).replace("1.0", "H")
    array[5] = str(array[5]).replace("0.0", "L")

    # sealer
    array[6] = str(array[6]).replace("1.0", "O")
    array[6] = str(array[6]).replace("0.0", "G")
    name = "".join(array)
    return name


def shorten_column_name(s):
    remove_list = [
        "label: ",
        "procedure, ",
        "protocol: ",
        "type: ",
        "(oC)",
        "($^\mathrm{o}$C)",
        "(mg)",
        "(um)",
        "(ppm)",
        "($\mu$m)",
        "temperature: ",
        "time: ",
        "hot plate",
        "machine: ",
        " (min)",
        "(J/g)"
    ]
    for r in remove_list:
        s = s.replace(r, "")
    s = s.replace("DSC (salt_melting_heat_energy)", "Melting enthaply")
    s = s.replace("DSC (salt_melting_temperature)", "Melting temperature")
    s = s.replace("Measurement temperature for conductivity",
                  "Measurement temperature")
    s = s.replace("Seal, vacuum pack using KitchenBoss G210",
                  "Seal with vacuum pack")
    pos = s.find(", <-->")
    if pos > 0:
        s = s[:pos]
    return s


def shorten_column_name2(s):
    s = shorten_column_name(s)
    s = s.replace("cell_id_cell_id", "Cell ID")
    s = s.replace("O2", "Oxygen concentration")
    s = s.replace("Particle_size", "Particle size")
    s = s.replace("Ion ", "")
    return s


def shorten_plotting_name(x_name):
    x_name = x_name.replace("label: ", "")
    x_name = x_name.replace("procedure,", "")
    x_name = x_name.replace(", type:", "")
    x_name = x_name.replace("protocol: ", "")
    x_name = x_name.replace("sample,", "")
    x_name = x_name.replace("|", "\n")
    return x_name

def remove_json_characters(s):
    
    s=s.replace(":","")
    s=s.replace("(","")
    s=s.replace(")","")
    s=s.replace("","")
    s=s.replace("$","")
    s=s.replace("^","")
    s=s.replace("\\","")
    s=s.replace("{","")
    s=s.replace("}","")
    s=s.replace("/","")
    return s