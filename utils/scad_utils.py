import subprocess
import os

def set_variables(variables):
    return [f"-D {var}={value}" for var, value in variables.items()]

def set_parameters(parameter_file, parameter_set):
    return [f"-p {parameter_file}", f"-P {parameter_set}"]

def convert_scad_to_stl(scad_path, output_path, variables=None, parameters=None, parameter_set=None):
    args = ["openscad", scad_path, "-o", output_path]
    
    if variables:
        args.extend(set_variables(variables))

    if parameters and parameter_set:
        args.extend(set_parameters(parameters, parameter_set))

    process = subprocess.run(args, capture_output=True, text=True)

    if process.returncode != 0:
        raise RuntimeError(f"OpenSCAD conversion failed: {process.stderr}")

    return output_path
