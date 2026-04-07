import asyncio
import time
import struct
import numpy as np
from bleak import BleakScanner

# --- Configuration (Must match ESP32-C6 code) ---
HALO_COMPANY_ID = 0xFFFF
HALO_TAG_ID     = 1

# Timing
BURST_TIMEOUT_SEC = 2.0  # If no packet for this long, burst is over

# Range Threshold
RSSI_THRESHOLD = -90     # dBm - above this = in range

# --- State ---
rssi_buffer = []
last_packet_time = None
current_tag_id = None
current_battery = None

def filter_outliers_iqr(samples):
    """Remove outliers using IQR method. Returns filtered list."""
    if len(samples) < 4:
        return samples  # Not enough data for IQR

    sorted_samples = sorted(samples)
    q1 = np.percentile(sorted_samples, 25)
    q3 = np.percentile(sorted_samples, 75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return [s for s in samples if lower_bound <= s <= upper_bound]

def process_burst():
    """Process buffered RSSI samples and report range status."""
    global rssi_buffer, current_tag_id, current_battery

    if not rssi_buffer:
        return

    original_count = len(rssi_buffer)
    filtered = filter_outliers_iqr(rssi_buffer)
    filtered_count = len(filtered)

    if filtered_count == 0:
        print("No samples after filtering")
        rssi_buffer.clear()
        return

    mean_rssi = np.mean(filtered)
    status = "IN RANGE" if mean_rssi >= RSSI_THRESHOLD else "OUT OF RANGE"

    print(f"\n--- [HALO BURST PROCESSED] ---")
    print(f"Tag ID:     {hex(current_tag_id)}")
    print(f"Battery:    {current_battery}%")
    print(f"Samples:    {original_count} collected, {filtered_count} after IQR")
    print(f"Mean RSSI:  {mean_rssi:.1f} dBm")
    print(f"Status:     {status}")
    print("-" * 30)

    rssi_buffer.clear()

def callback(device, advertisement_data):
    """Called on every BLE advertisement detection."""
    global rssi_buffer, last_packet_time, current_tag_id, current_battery

    if HALO_COMPANY_ID in advertisement_data.manufacturer_data:
        raw_data = advertisement_data.manufacturer_data[HALO_COMPANY_ID]

        if len(raw_data) == 3:
            tag_id, battery = struct.unpack("<HB", raw_data)

            if tag_id == HALO_TAG_ID:
                rssi = advertisement_data.rssi
                rssi_buffer.append(rssi)
                last_packet_time = time.time()
                current_tag_id = tag_id
                current_battery = battery
                print(f"Packet: RSSI={rssi} dBm (buffer: {len(rssi_buffer)})")

async def main():
    global last_packet_time

    print(f"Halo Anchor started. Scanning for tags...")
    print("Press Ctrl+C to stop.\n")

    scanner = BleakScanner(detection_callback=callback)

    async with scanner:
        while True:
            await asyncio.sleep(0.5)

            # Check for burst timeout
            if last_packet_time and rssi_buffer:
                elapsed = time.time() - last_packet_time
                if elapsed >= BURST_TIMEOUT_SEC:
                    process_burst()
                    last_packet_time = None

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAnchor stopped by user.")