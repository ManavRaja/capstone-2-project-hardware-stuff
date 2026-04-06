import asyncio
import struct
from bleak import BleakScanner

# --- Configuration (Must match ESP32-C6 code) ---
HALO_COMPANY_ID = 0xFFFF
HALO_TAG_ID     = 1

def callback(device, advertisement_data):
    """
    This function is called every time a BLE advertisement is detected.
    """
    if HALO_COMPANY_ID in advertisement_data.manufacturer_data:
        raw_data = advertisement_data.manufacturer_data[HALO_COMPANY_ID]

        if len(raw_data) == 3:
            tag_id, battery = struct.unpack("<HB", raw_data)

            if tag_id == HALO_TAG_ID:
                rssi = advertisement_data.rssi

                print(f"--- [HALO SIGNAL DETECTED] ---")
                print(f"Device MAC: {device.address}")
                print(f"Tag ID:     {hex(tag_id)}")
                print(f"Battery:    {battery}%")
                print(f"Signal:     {rssi} dBm")

                # Simple MoZo Logic
                if rssi < -90:
                    print("Status:     WARNING - Weak Signal (Edge of MoZo)")
                else:
                    print("Status:     SAFE - Inside MoZo")
                print("-" * 30)

async def main():
    print(f"Halo Anchor started. Scanning for tags...")
    print("Press Ctrl+C to stop.\n")
    
    # Initialize the scanner with our detection callback
    scanner = BleakScanner(detection_callback=callback)
    
    # Start scanning and keep the script running
    async with scanner:
        # The script will stay in this loop until interrupted
        while True:
            await asyncio.sleep(1.0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAnchor stopped by user.")