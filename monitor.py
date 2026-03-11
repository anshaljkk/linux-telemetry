# linux system monitor
# reads /proc files and prints cpu/memory info
# ansh - written quickly, needs cleanup
#
# usage: python3 monitor.py
#        python3 monitor.py --port /dev/ttyUSB0

import time
import sys
import json

# optional serial
try:
    import serial
    HAS_SERIAL = True
except:
    HAS_SERIAL = False

# globals for cpu calculation (needs previous reading to calculate delta)
prev_idle = 0
prev_total = 0

def get_cpu():
    global prev_idle, prev_total
    
    with open('/proc/stat') as f:
        line = f.readline() # first line is total cpu
    
    # line looks like: cpu  1234 56 789 ...
    parts = line.split()
    # parts[1:] are: user nice system idle iowait irq softirq steal
    vals = [int(x) for x in parts[1:]]
    
    idle = vals[3] # idle time
    total = sum(vals)
    
    # delta from last reading
    d_idle = idle - prev_idle
    d_total = total - prev_total
    
    prev_idle = idle
    prev_total = total
    
    if d_total == 0:
        return 0.0
    
    # cpu % = 1 - (idle_delta / total_delta)
    percent = (1.0 - d_idle/d_total) * 100
    return round(percent, 1)

def get_mem():
    info = {}
    with open('/proc/meminfo') as f:
        for line in f:
            k, v = line.split(':', 1)
            info[k.strip()] = int(v.split()[0]) # in kb
    
    total = info['MemTotal']
    free = info['MemFree']
    # "available" memory accounts for cache, more useful than free
    # but not all kernels have it so fall back to free
    available = info.get('MemAvailable', free)
    used = total - available
    
    return {
        'total_mb': total // 1024,
        'used_mb': used // 1024,
        'free_mb': free // 1024
    }

# setup serial if port given
ser = None
if '--port' in sys.argv:
    idx = sys.argv.index('--port')
    port = sys.argv[idx+1]
    if not HAS_SERIAL:
        print("pyserial not installed, run: pip install pyserial")
        sys.exit(1)
    ser = serial.Serial(port, 9600, timeout=1)
    print(f"connected to {port}")

print("starting monitor, ctrl+c to stop")
print()

# first reading is always 0 so skip it
get_cpu()
time.sleep(0.5)

while True:
    try:
        cpu = get_cpu()
        mem = get_mem()
        
        data = {
            'cpu': cpu,
            'mem_used': mem['used_mb'],
            'mem_total': mem['total_mb']
        }
        
        # print locally
        print(f"cpu: {cpu}%  |  ram: {mem['used_mb']}mb / {mem['total_mb']}mb", end='\r')
        
        # send to arduino if connected
        if ser:
            packet = json.dumps(data) + '\n'
            ser.write(packet.encode())
        
        time.sleep(1)
        
    except KeyboardInterrupt:
        print("\nstopped")
        if ser:
            ser.close()
        break
    except Exception as e:
        # TODO: handle errors better
        print(f"error: {e}")
        time.sleep(1)
