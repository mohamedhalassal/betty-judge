from dataclasses import dataclass
import subprocess
import threading
import signal
import os

@dataclass
class ExecutionResult:
    returncode: int
    stdout: str
    stderr: str
    cpu_time_ms: int
    memory_mb: int
    wall_timed_out: bool


def max_rss_to_mb(max_rss: int) -> float:
    return max_rss / 1024
    
def run_testcase(exe_file, input_data, limit_resources, wall_limit_seconds) -> ExecutionResult:
    process = subprocess.Popen(
        [str(exe_file)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        preexec_fn=limit_resources,
        start_new_session=True,
    )

    # set a wall clock time limit
    wall_timed_out = False

    def kill_process():
        nonlocal wall_timed_out
        wall_timed_out = True
        try:
            os.killpg(process.pid, signal.SIGKILL)
        # if the process has already exited before killing it
        except ProcessLookupError:
            pass

    timer = threading.Timer(wall_limit_seconds, kill_process)
    timer.start()

    try:
        process.stdin.write(input_data)
    # if the process has already exited before writing to stdin, ignore the error
    except (BrokenPipeError, OSError):
        pass
    finally:
        try:
            process.stdin.close()
        # if the process has already exited before closing stdin, ignore the error
        except (BrokenPipeError, OSError):
            pass

    try:
        pid, status, usage = os.wait4(process.pid, 0)
    finally:
        timer.cancel()

    process.returncode = os.waitstatus_to_exitcode(status)
    # CPU time in milliseconds
    cpu_time = int((usage.ru_utime + usage.ru_stime) * 1000)
    # Memory usage in MB
    memory_mb = int(max_rss_to_mb(usage.ru_maxrss))

    return ExecutionResult(
        returncode=process.returncode,
        stdout=process.stdout.read(),
        stderr=process.stderr.read(),
        cpu_time_ms=cpu_time,
        memory_mb=memory_mb,
        wall_timed_out=wall_timed_out,
    )
  