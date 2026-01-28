# ===============================
# main.py
# ===============================

import time

from core_logic.state_manager import state_manager_instance
from dashboard.app import start_dashboard
from Voice_control.voice_recognition import start_voice_control
from gesture_control.hand_detection import start_gesture_control


# ---------------- DUMMY ARDUINO ----------------
# (Replace later with real Arduino class)
class DummyArduino:
    def send(self, command):
        print(f"[DUMMY ARDUINO] {command}")


arduino = DummyArduino()


# ---------------- MAIN ----------------
def main():
    print("🚀 System starting...")

    # ✅ VERY IMPORTANT: EXIT INIT → READY
    state_manager_instance.set_state("IDLE")

    # ---------------- START DASHBOARD ----------------
    # Flask runs in its own thread
    import threading
    threading.Thread(
        target=start_dashboard,
        daemon=True
    ).start()

    # ---------------- START VOICE ----------------
    start_voice_control(state_manager_instance, arduino)

    # ---------------- START GESTURE ----------------
    start_gesture_control(state_manager_instance, arduino)

    print("✅ System READY")
    print("🎤 Say: start scan | stop scan | emergency")
    print("✋ Use gestures to control the system")

    # ---------------- KEEP MAIN ALIVE ----------------
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    main()
