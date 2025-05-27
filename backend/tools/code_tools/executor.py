from typing import Dict, Any
import subprocess
import tempfile
import os
import sys
import shlex

class CodeExecutor:
    """
    Tool for executing code in a controlled environment.
    """
    
    name = "code_executor"
    description = "Executes code and returns the result"

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def run(self, args: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        code = args.get("code")
        language = args.get("language", "python").lower()

        if not code:
            return {"error": "No code provided", "success": False}

        if language == "python":
            return self._execute_python(code)
        elif language in ["c", "cpp"]:
            return self._execute_compiled_code(code, language)
        else:
            return {"error": f"Unsupported language: {language}", "success": False}

    def _execute_python(self, code: str) -> Dict[str, Any]:
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file.write(code.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            process = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return {
                "output": process.stdout,
                "error": process.stderr,
                "success": process.returncode == 0,
                "tool_name": self.name,
                "language": "python"
            }
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "error": f"Execution timed out after {self.timeout} seconds",
                "success": False,
                "tool_name": self.name,
                "language": "python"
            }
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def _execute_compiled_code(self, code: str, language: str) -> Dict[str, Any]:
        suffix = ".c" if language == "c" else ".cpp"
        compiler = "gcc" if language == "c" else "g++"
        
        # Create temporary directory for compilation artifacts
        temp_dir = tempfile.mkdtemp()
        src_file_path = os.path.join(temp_dir, f"code{suffix}")
        binary_path = os.path.join(temp_dir, "code.out")
        
        try:
            # Write source file
            with open(src_file_path, "w") as src_file:
                src_file.write(code)
            
            # Add compiler flags for better error checking and warnings
            compiler_flags = ["-Wall", "-Wextra", "-pedantic"]
            if language == "c":
                compiler_flags.append("-std=c11")  # Use C11 standard
            else:  # C++
                compiler_flags.append("-std=c++17")  # Use C++17 standard
            
            # Compile command with proper flags
            compile_cmd = [compiler, src_file_path, "-o", binary_path] + compiler_flags
            
            # Compile the code
            compile_proc = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if compile_proc.returncode != 0:
                return {
                    "output": "",
                    "error": f"Compilation error:\n{compile_proc.stderr}",
                    "success": False,
                    "tool_name": self.name,
                    "language": language
                }

            # Run the compiled binary with input redirection if needed
            run_proc = subprocess.run(
                [binary_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return {
                "output": run_proc.stdout,
                "error": run_proc.stderr,
                "success": run_proc.returncode == 0,
                "tool_name": self.name,
                "language": language,
                "compilation": "successful"
            }
        except subprocess.TimeoutExpired as e:
            stage = "compilation" if "compile_proc" not in locals() else "execution"
            return {
                "output": "",
                "error": f"{stage.capitalize()} timed out after {self.timeout} seconds",
                "success": False,
                "tool_name": self.name,
                "language": language
            }
        except Exception as e:
            return {
                "output": "",
                "error": f"Error: {str(e)}",
                "success": False,
                "tool_name": self.name,
                "language": language
            }
        finally:
            # Clean up all temp files
            if os.path.exists(src_file_path):
                os.unlink(src_file_path)
            if os.path.exists(binary_path):
                os.unlink(binary_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)