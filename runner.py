import subprocess
import os
def run_program(command, input_data="", timeout=1.0):
    try:
        result = subprocess.run(
            command, 
            input=input_data, 
            text=True, 
            capture_output=True, 
            check=True, 
            timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        raise Exception("Timeout expired")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else e.stdout if e.stdout else str(e)
        raise Exception(f"Process exited with error {e.returncode}: {error_msg}")
    except Exception as e:
        raise Exception(f"Error running program: {str(e)}")
    
def compile_program_return_command(filename):
    if not os.path.exists(filename):
        raise Exception(f"File not found: {filename}")
    
    # Extract file parts properly
    file_dir = os.path.dirname(filename)  # Directory path
    file_fullname = os.path.basename(filename)  # Filename with extension
    file_name = os.path.splitext(file_fullname)[0]  # Filename without extension
    
    extension = os.path.splitext(filename)[1][1:]  # Get extension without dot
    
    if extension == 'cpp':
        executable_name = f"msm_{file_name}"
        result = subprocess.run(
            ["/usr/bin/g++", filename, "-o", executable_name], 
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else result.stdout
            raise Exception(f"C++ compilation failed:\n{error_msg}")
        return [f"./{executable_name}"]
    
    elif extension == "java":
        result = subprocess.run(["/usr/bin/javac", filename], capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else result.stdout
            raise Exception(f"Java compilation failed:\n{error_msg}")
        return ["java", file_name]  # Just the class name
    
    elif extension == "py":
        return ["python3", filename]
    
    else:
        raise Exception(f'Unknown extension: {extension}')