import time

try:
    from picamera2 import Picamera2
    import cv2
except ImportError as e:
    print(f"❌ Required module missing: {e}")
    exit(1)

print("📷 Starting Picamera2 preview test...")

try:
    picam2 = Picamera2()

    # Configure for preview (640x480 is good default)
    picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))

    picam2.start()
    time.sleep(2)  # Give camera time to warm up

    print("✅ Camera started. Press 'q' in the window to quit.")

    while True:
        frame = picam2.capture_array()
        cv2.imshow("Picamera2 Preview", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("👋 Exiting preview.")
            break

    picam2.stop()
    cv2.destroyAllWindows()

except Exception as e:
    print(f"❌ Error running Picamera2 preview: {e}")
