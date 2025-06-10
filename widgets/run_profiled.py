# run_profiled.py
import subprocess
import time
import sys
import os
import signal

def run_with_pyspy(target_script, output_svg="pyspy_output.svg", delay=3):
    print(f"⏳ Launching: {target_script}")
    
    # Launch your app
    process = subprocess.Popen([sys.executable, target_script])
    print(f"📌 App PID: {process.pid}")

    # Wait a bit to let the GUI show up
    time.sleep(delay)

    print("📈 Starting py-spy profiling...")
    subprocess.run([
        "py-spy", "record",
        "-o", output_svg,
        "--pid", str(process.pid),
        "--duration", "10",  # profile for 10 seconds (change as needed)
        "--rate", "1000"     # high sampling rate for better resolution
    ])

    print(f"✅ Profiling done. Output saved to: {output_svg}")

    # Ask user if they want to kill the app
    kill = input("Kill app now? (y/N): ").strip().lower()
    if kill == 'y':
        process.send_signal(signal.SIGINT)

if __name__ == "__main__":
    run_with_pyspy("searchworker.py")  # replace with your actual script name
