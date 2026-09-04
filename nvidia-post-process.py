#!/usr/bin/env python3
# -*- mode: python; indent-tabs-mode: nil; python-indent-level: 4 -*-
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python

import sys
import os
import lzma
import re
import math
from datetime import datetime, timezone
from pathlib import Path

TOOLBOX_HOME = os.environ.get('TOOLBOX_HOME')
if TOOLBOX_HOME is None:
    print("This script requires libraries that are provided by the toolbox project.")
    print("Toolbox can be acquired from https://github.com/perftool-incubator/toolbox and")
    print("then use 'export TOOLBOX_HOME=/path/to/toolbox' so that it can be located.")
    exit(1)
else:
    p = Path(TOOLBOX_HOME) / 'python'
    if not p.exists() or not p.is_dir():
        print("ERROR: <TOOLBOX_HOME>/python ('%s') does not exist!" % (p))
        exit(2)
    sys.path.append(str(p))
from toolbox.cdm_metrics import CDMMetrics

def main():
    print('nvidia-post-process')
    metrics = CDMMetrics()

    # timestamp, device_id, device_name, gpu_util(%), mem_util(%), temp(C), used_mem(MiB), total_mem(MiB), free_mem(MiB), power(W), fan(%)
    # 2025-05-16 14:51:59, 0, NVIDIA A100-SXM4-80GB,   0,   0,  31,    882.4,  81920.0,  81037.6,  65.3,   0
    # 2025-05-16 14:51:59, 1, NVIDIA A100-SXM4-80GB,   0,   0,  29,    882.4,  81920.0,  81037.6,  63.7,   0

    f = 'nvidia-output.txt.xz'
    if not os.path.exists(f):
        print("ERROR: %s not found" % f)
        return 1

    with lzma.open(f, 'rt') as file:
        file_id = '0'
        for line in file:
            print(line)
            if reggy := re.search(r'^(\d{,4}-\d{,2}-\d{,2}\s+\d{,2}:\d{,2}:\d{,2}),\s+(\d+),\s+([^,]+),\s+(\d+),\s+(\d+),\s+(\d+),\s+((\d+(\.\d*)?)|(\.\d+)),\s+((\d+(\.\d*)?)|(\.\d+)),\s+((\d+(\.\d*)?)|(\.\d+)),\s+((\d+(\.\d*)?)|(\.\d+)),\s+(\d+)$', line):
                print("matched")
                end_dt = reggy.group(1)
                names = {'id': reggy.group(2), 'desc' : reggy.group(3)}
                values = {
                    'util': reggy.group(4),
                    'temp': reggy.group(6),
                    'mem': reggy.group(7),
                    'pwr': reggy.group(19)
                    }
                dt = datetime.strptime(end_dt, '%Y-%m-%d %X').replace(tzinfo=timezone.utc)
                end_ts = int(math.floor(dt.timestamp() * 1000))
                for this_type in ('pwr', 'util', 'mem', 'temp'):
                    sample = {'end': end_ts, 'value': values[this_type]}
                    if this_type in ('temp', 'mem'):
                        this_class = 'count'
                    else:
                        this_class = 'throughput'
                    this_desc = {'source': 'nvidia', 'type': this_type, 'class': this_class}
                    metrics.log_sample(file_id, this_desc, names, sample)
            else:
                print("NO MATCH")
    metrics.finish_samples()
    return(0)

if __name__ == "__main__":
    exit(main())
