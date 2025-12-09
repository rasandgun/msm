import subprocess
import os
def run_program(command, input_data, timeout = 1.0):
    result = ""
    try:
        result = subprocess.run(command, input=input_data, text=True, capture_output=True, check=True)
    except:
        print("ERROR: command is invalid")
    return result

def compile_program_return_command(filename):
    extension = filename.split('.')[-1]
    base_name = filename.split('.')[0]
    if filename.split('.')[-1] == 'cpp':
        subprocess.run(["/usr/bin/g++", filename, "-o", "msm" + base_name])  
        return ["./" + "msm" + base_name]
    elif extension == "java":
        subprocess.run(["/usr/bin/javac", filename])
        return ["java", base_name]
    elif extension == "py":
        return ["python3", filename]
    else:
        raise Exception('Unknown extension ' + extension)

