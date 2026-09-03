#!/usr/bin/env python3
# -*- mode: python; indent-tabs-mode: nil; python-indent-level: 4 -*-
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python

import os
import sys
import time
import argparse
from datetime import datetime
import pynvml

def initialize_nvml():
    """Initialize NVIDIA Management Library."""
    try:
        pynvml.nvmlInit()
        return True
    except pynvml.NVMLError as err:
        print(f"Failed to initialize NVML: {err}")
        return False

def get_device_count():
    """Get the number of NVIDIA devices on the system."""
    try:
        return pynvml.nvmlDeviceGetCount()
    except pynvml.NVMLError as err:
        print(f"Failed to get device count: {err}")
        return 0

def get_device_stats(device_index):
    """Get statistics for a specific GPU device."""
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(device_index)
        name = pynvml.nvmlDeviceGetName(handle)

        # Get utilization rates
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
        gpu_util = utilization.gpu
        mem_util = utilization.memory

        # Get temperature
        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

        # Get memory info
        memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
        total_mem = memory.total / (1024 * 1024)  # MiB
        used_mem = memory.used / (1024 * 1024)    # MiB
        free_mem = memory.free / (1024 * 1024)    # MiB

        # Get power usage
        try:
            power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert from mW to W
        except pynvml.NVMLError:
            power_usage = 0

        # Get fan speed if available
        try:
            fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
        except pynvml.NVMLError:
            fan_speed = 0

        return {
            "name": name,
            "gpu_util": gpu_util,
            "mem_util": mem_util,
            "temp": temp,
            "total_mem": total_mem,
            "used_mem": used_mem,
            "free_mem": free_mem,
            "power_usage": power_usage,
            "fan_speed": fan_speed
        }
    except pynvml.NVMLError as err:
        print(f"Failed to get stats for device {device_index}: {err}")
        return None

def print_header(device_count):
    """Print CSV header with aligned columns."""
    header = "timestamp, device_id, device_name, gpu_util(%), mem_util(%), temp(C), used_mem(MiB), total_mem(MiB), free_mem(MiB), power(W), fan(%)"
    print(header)

def print_stats(timestamp, device_index, stats):
    """Print device statistics in CSV format with aligned columns."""
    if stats:
        row = (f"{timestamp}, {device_index}, {stats['name']}, "
               f"{stats['gpu_util']:3d}, {stats['mem_util']:3d}, "
               f"{stats['temp']:3d}, {stats['used_mem']:8.1f}, "
               f"{stats['total_mem']:8.1f}, {stats['free_mem']:8.1f}, "
               f"{stats['power_usage']:5.1f}, {stats['fan_speed']:3d}")
        print(row)

def monitor_gpus(interval, duration=None):
    """Monitor all available GPUs at specified intervals."""
    if not initialize_nvml():
        return

    device_count = get_device_count()
    if device_count == 0:
        print("No NVIDIA GPUs found.")
        pynvml.nvmlShutdown()
        return

    print(f"Found {device_count} NVIDIA GPU(s).")
    print_header(device_count)

    try:
        start_time = time.time()
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for i in range(device_count):
                stats = get_device_stats(i)
                print_stats(timestamp, i, stats)

            if duration and (time.time() - start_time) >= duration:
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    finally:
        pynvml.nvmlShutdown()

def main():
    parser = argparse.ArgumentParser(description="Monitor NVIDIA GPU statistics")
    parser.add_argument("-i", "--interval", type=float, default=1.0,
                        help="Sampling interval in seconds (default: 1.0)")
    parser.add_argument("-d", "--duration", type=float,
                        help="Total monitoring duration in seconds (optional)")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    if args.output:
        sys.stdout = open(args.output, 'w')

    monitor_gpus(args.interval, args.duration)

    if args.output:
        sys.stdout.close()

if __name__ == "__main__":
    main()
