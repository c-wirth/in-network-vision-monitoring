import socket
import struct
import time
import os
from collections import defaultdict
from datetime import datetime

DEVICE_IP           = "192.168.40.12"
DEVICE_CONTROL_PORT = 5006
SERVER_FRAME_PORT   = 5005
STREAM_DURATION_SEC = 5
ALIVE_INTERVAL_SEC  = 1.0

FLAG_STOP_STREAM    = 0x0003
FLAG_START_STREAM   = 0x0004
FLAG_ALIVE          = 0x0006

HEADER_SIZE = 8

def make_packet(flags, payload=b''):
    header = struct.pack('>HHHH', 0, 0, 0, flags)
    return header + payload

def send_control(sock, flags, payload=b''):
    sock.sendto(make_packet(flags, payload), (DEVICE_IP, DEVICE_CONTROL_PORT))

# --- output directory ---
capture_name = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = os.path.expanduser(f"~/Desktop/stream_test/{capture_name}")
os.makedirs(out_dir, exist_ok=True)
print(f"Saving frames to {out_dir}")

# --- socket setup ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", SERVER_FRAME_PORT))

# --- flush stale packets ---
print("Flushing stale packets...")
sock.settimeout(0.2)
stale_pre = 0
while True:
    try:
        sock.recvfrom(1400)
        stale_pre += 1
    except socket.timeout:
        break

# --- start stream ---
print("Sending START_STREAM")
send_control(sock, FLAG_START_STREAM)

# --- receive loop ---
fragments    = defaultdict(dict)
frame_totals = {}
frames_saved = 0
frame_times  = {}
last_alive   = time.time()
stream_start = time.time()
stale_post   = 0

sock.settimeout(0.05)

print(f"Streaming for {STREAM_DURATION_SEC} seconds...")

while True:
    now     = time.time()
    elapsed = now - stream_start

    # --- send alive ---
    if now - last_alive >= ALIVE_INTERVAL_SEC:
        send_control(sock, FLAG_ALIVE)
        last_alive = now

    # --- stop after duration ---
    if elapsed >= STREAM_DURATION_SEC:
        print("Sending STOP_STREAM")
        send_control(sock, FLAG_STOP_STREAM)

        sock.settimeout(0.2)
        while True:
            try:
                sock.recvfrom(1400)
                stale_post += 1
            except socket.timeout:
                break
        break

    # --- receive packet ---
    try:
        data, addr = sock.recvfrom(1400)
    except socket.timeout:
        continue

    if len(data) < HEADER_SIZE:
        continue

    frame_id, frag_id, total_frags, flags = struct.unpack('>HHHH', data[:8])
    payload = data[HEADER_SIZE:]

    if flags != 0:
        continue

    recv_time = time.time()

    if frame_id not in frame_times:
        frame_times[frame_id] = recv_time

    fragments[frame_id][frag_id] = payload
    frame_totals[frame_id]       = total_frags

    if len(fragments[frame_id]) == total_frags:
        if all(i in fragments[frame_id] for i in range(total_frags)):
            jpeg = b''.join(fragments[frame_id][i] for i in range(total_frags))
            filename = os.path.join(out_dir, f"frame_{frame_id:05d}.jpg")
            with open(filename, 'wb') as f:
                f.write(jpeg)
            frames_saved += 1
        else:
            print(f"Frame {frame_id} missing fragments — dropping")
        del fragments[frame_id]
        del frame_totals[frame_id]

# --- stats ---
total_time = time.time() - stream_start
fps        = frames_saved / total_time if total_time > 0 else 0

sorted_times = [frame_times[k] for k in sorted(frame_times)]
if len(sorted_times) > 1:
    gaps           = [sorted_times[i+1] - sorted_times[i] for i in range(len(sorted_times) - 1)]
    avg_latency_ms = (sum(gaps) / len(gaps)) * 1000
else:
    avg_latency_ms = 0

print(f"\n--- Results ---")
print(f"Duration:            {total_time:.2f}s")
print(f"Frames saved:        {frames_saved}")
print(f"FPS:                 {fps:.2f}")
print(f"Avg inter-frame:     {avg_latency_ms:.1f}ms")
print(f"Incomplete dropped:  {len(fragments)}")
print(f"Stale pre-session:   {stale_pre}")
print(f"Stale post-session:  {stale_post}")
print(f"Total stale:         {stale_pre + stale_post}")
print(f"Output:              {out_dir}")

sock.close()
