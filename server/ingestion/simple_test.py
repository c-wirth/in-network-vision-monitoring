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

FLAG_HANDSHAKE      = 0x0001
FLAG_HANDSHAKE_ACK  = 0x0002
FLAG_STOP_STREAM    = 0x0003
FLAG_START_STREAM   = 0x0004
FLAG_PACKET_LOSS    = 0x0005
FLAG_ALIVE          = 0x0006

HEADER_SIZE = 8

print("exiting")

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
sock.settimeout(1.0)

# --- handshake ---
print("Waiting for handshake from device...")
while True:
    try:
        data, addr = sock.recvfrom(1400)
        if len(data) >= HEADER_SIZE:
            print(f"Message received from {addr}")
            flags = struct.unpack('>H', data[6:8])[0]
            if flags == FLAG_HANDSHAKE:
                print(f"Handshake received from {addr} — sending ACK")
                print(f"Sending ACK to {DEVICE_IP}:{DEVICE_CONTROL_PORT}")
                ack = make_packet(FLAG_HANDSHAKE_ACK)
                sock.sendto(ack, (DEVICE_IP, DEVICE_CONTROL_PORT))
                break
    except socket.timeout:
        continue

# --- start stream ---
time.sleep(0.1)
print("Sending START_STREAM")
send_control(sock, FLAG_START_STREAM)

# --- receive loop ---
fragments     = defaultdict(dict)   # frame_id -> {frag_id: payload}
frame_totals  = {}                  # frame_id -> total_frags expected
frames_saved  = 0
frame_times   = {}                  # arrival time of first fragment per frame
last_alive    = time.time()
stream_start  = time.time()

sock.settimeout(0.05)  # 50ms poll so alive signal stays on time

print(f"Streaming for {STREAM_DURATION_SEC} seconds...")

while True:
    now = time.time()
    elapsed = now - stream_start

    # --- send alive ---
    if now - last_alive >= ALIVE_INTERVAL_SEC:
        send_control(sock, FLAG_ALIVE)
        last_alive = now

    # --- stop after duration ---
    if elapsed >= STREAM_DURATION_SEC:
        print("Sending STOP_STREAM")
        send_control(sock, FLAG_STOP_STREAM)
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
    print(f"Packet: frame_id={frame_id} frag={frag_id}/{total_frags} flags=0x{flags:04X} len={len(payload)}")

    # ignore control packets on this port
    if flags != 0:
        continue

    recv_time = time.time()

    # record arrival time of first fragment for latency reference
    if frame_id not in frame_times:
        frame_times[frame_id] = recv_time

    fragments[frame_id][frag_id]  = payload
    frame_totals[frame_id]        = total_frags

    # check if frame is complete
    if len(fragments[frame_id]) == total_frags:
        jpeg = b''.join(fragments[frame_id][i] for i in range(total_frags))
        filename = os.path.join(out_dir, f"frame_{frame_id:05d}.jpg")
        with open(filename, 'wb') as f:
            f.write(jpeg)
        frames_saved += 1
        del fragments[frame_id]
        del frame_totals[frame_id]

# --- stats ---
total_time = time.time() - stream_start
fps = frames_saved / total_time if total_time > 0 else 0

# inter-frame latency — average gap between consecutive frame arrivals
sorted_times = [frame_times[k] for k in sorted(frame_times)]
if len(sorted_times) > 1:
    gaps = [sorted_times[i+1] - sorted_times[i] for i in range(len(sorted_times)-1)]
    avg_latency_ms = (sum(gaps) / len(gaps)) * 1000
else:
    avg_latency_ms = 0

print(f"\n--- Results ---")
print(f"Duration:        {total_time:.2f}s")
print(f"Frames saved:    {frames_saved}")
print(f"FPS:             {fps:.2f}")
print(f"Avg inter-frame: {avg_latency_ms:.1f}ms")
print(f"Incomplete frames dropped: {len(fragments)}")
print(f"Output:          {out_dir}")

sock.close()
