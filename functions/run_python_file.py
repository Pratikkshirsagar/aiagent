import os
import subprocess


def run_python_file(working_directory, file_path, args=[]):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    try:
        if os.path.commonpath([abs_file_path, abs_working_dir]) != abs_working_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    except Exception:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(abs_file_path):
        return f'Error: File "{file_path}" not found.'

    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'

    try:
        final_args = ["python3", file_path]
        final_args.extend(args)
        completed = subprocess.run(
            final_args,
            cwd=abs_working_dir,
            timeout=30,
            capture_output=True,
        )

        stdout = completed.stdout
        stderr = completed.stderr

        if not stdout and not stderr:
            return "No output produced."

        result = (
            f"STDOUT: {stdout}\n\n"  # Keep raw bytes representation as in prior tasks
            f"STDERR: {stderr}\n\n"
        )

        if completed.returncode != 0:
            result += f"Process exited with code {completed.returncode}"

        return result
    except Exception as e:
        return f"Error: executing Python file: {e}"
