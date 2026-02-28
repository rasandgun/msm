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
    
import subprocess
import os

def compile_program_return_command(filename):
    if not os.path.exists(filename):
        raise Exception("File not found: " + filename)

    dir_name = os.path.dirname(filename)
    base = os.path.basename(filename)
    name, ext = os.path.splitext(base)
    ext = ext[1:]  # убираем точку

    if ext == "cpp":
        out = "./msm_" + name
        res = subprocess.run(["/usr/bin/g++", filename, "-o", out], capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception("C++ compilation error:\n" + (res.stderr or res.stdout))
        return [out]

    elif ext == "java":
        res = subprocess.run(["/usr/bin/javac", filename], capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception("Java compilation error:\n" + (res.stderr or res.stdout))
        return ["java", name]

    elif ext == "py":
        return ["python3", filename]

    elif ext in ("pas", "pp"):  # Free Pascal
        out = "./msm_" + name
        res = subprocess.run(["fpc", filename, "-o" + out], capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception("Pascal compilation error:\n" + (res.stderr or res.stdout))
        return [out]

    elif ext == "rs":  # Rust
        out = "./msm_" + name
        res = subprocess.run(["rustc", filename, "-o", out], capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception("Rust compilation error:\n" + (res.stderr or res.stdout))
        return [out]

    elif ext == "kt":  # Kotlin
        res = subprocess.run(["kotlinc", filename, "-d", "."], capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception("Kotlin compilation error:\n" + (res.stderr or res.stdout))
        return ["kotlin", name + "Kt"]  # соглашение: имя файла + Kt

    elif ext == "d":  # D
        out = "./msm_" + name
        res = subprocess.run(["dmd", filename, "-of" + out], capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception("D compilation error:\n" + (res.stderr or res.stdout))
        return [out]

    else:
        raise Exception("Unknown extension: " + ext)