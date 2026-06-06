import sys
import io
import traceback
import multiprocessing
import queue
from typing import Dict, Any, Optional, Tuple

def _execute_code_worker(code: str, globals_dict: Dict[str, Any], result_queue: multiprocessing.Queue):
    """Worker function to execute code in a separate process."""
    # Capture stdout
    stdout_capture = io.StringIO()
    sys.stdout = stdout_capture
    
    try:
        # Create a restricted builtins set
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'bool': bool, 'dict': dict,
            'enumerate': enumerate, 'filter': filter, 'float': float, 'int': int,
            'isinstance': isinstance, 'len': len, 'list': list, 'map': map,
            'max': max, 'min': min, 'pow': pow, 'print': print, 'range': range,
            'round': round, 'set': set, 'sorted': sorted, 'str': str, 'sum': sum,
            'tuple': tuple, 'type': type, 'zip': zip, 'None': None, 'True': True,
            'False': False,
        }
        
        # Execute the code
        exec(code, {'__builtins__': safe_builtins}, globals_dict)
        
        # Get result if assigned
        result = globals_dict.get('result') or globals_dict.get('fig')
        
        result_queue.put({
            'success': True,
            'result': result,
            'stdout': stdout_capture.getvalue(),
            'error': None,
            'traceback': None
        })
    except Exception as e:
        result_queue.put({
            'success': False,
            'result': None,
            'stdout': stdout_capture.getvalue(),
            'error': str(e),
            'traceback': traceback.format_exc()
        })
    finally:
        sys.stdout = sys.__stdout__

def run_safe_code(code: str, globals_dict: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """Runs python code safely in a separate process with a timeout."""
    result_queue = multiprocessing.Queue()
    
    # We need to make sure the globals_dict only contains picklable items if we use multiprocessing
    # For now, let's just pass the code and handle the rest inside the worker
    # In a real app, we'd need a more robust way to sync dataframes
    
    process = multiprocessing.Process(
        target=_execute_code_worker, 
        args=(code, globals_dict, result_queue)
    )
    
    process.start()
    
    try:
        return result_queue.get(timeout=timeout)
    except queue.Empty:
        process.terminate()
        return {
            'success': False,
            'result': None,
            'stdout': '',
            'error': f'Execution timed out after {timeout} seconds',
            'traceback': 'Timeout'
        }
    finally:
        if process.is_alive():
            process.join()

# Simplified version for cases where multiprocessing is too heavy or pickling fails
def run_in_memory_safe(code: str, globals_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Runs code in the current process but with restricted builtins and stdout capture."""
    stdout_capture = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout_capture
    
    try:
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'bool': bool, 'dict': dict,
            'enumerate': enumerate, 'filter': filter, 'float': float, 'int': int,
            'isinstance': isinstance, 'len': len, 'list': list, 'map': map,
            'max': max, 'min': min, 'pow': pow, 'print': print, 'range': range,
            'round': round, 'set': set, 'sorted': sorted, 'str': str, 'sum': sum,
            'tuple': tuple, 'type': type, 'zip': zip, 'None': None, 'True': True,
            'False': False,
        }
        
        # We allow pandas and plotly as they are needed for the system
        # These are usually already in the globals_dict
        
        exec(code, {'__builtins__': safe_builtins}, globals_dict)
        
        result = globals_dict.get('result') or globals_dict.get('fig')
        
        return {
            'success': True,
            'result': result,
            'stdout': stdout_capture.getvalue(),
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'result': None,
            'stdout': stdout_capture.getvalue(),
            'error': str(e),
            'traceback': traceback.format_exc()
        }
    finally:
        sys.stdout = old_stdout
