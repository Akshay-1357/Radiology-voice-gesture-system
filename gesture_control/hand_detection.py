# ======================================
# hand_detection.py (FINAL CLEAN VERSION)
# ======================================

import cv2
import mediapipe as mp
import threading
import time

from core_logic.command_validator import (
    START_SCAN,
    STOP_SCAN,
    SCAN_COMPLETE,
    EMERGENCY_STOP,
    validate_and_process
)

# ---------------- MEDIAPIPE SETUP ----------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils


# ---------------- FINGER COUNT ----------------
def count_fingers(hand):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    fingers.append(
        hand.landmark[tips[0]].x <
        hand.landmark[tips[0] - 1].x
    )

    # Other fingers
    for i in range(1, 5):
        fingers.append(
            hand.landmark[tips[i]].y <
            hand.landmark[tips[i] - 2].y
        )

    return fingers.count(True), fingers


# ---------------- GESTURE MAPPING ----------------
def get_gesture(count, fingers):
    if count == 5:
        return START_SCAN          # ✋ Open hand
    if count == 0:
        return STOP_SCAN           # ✊ Fist
    if count == 2 and fingers[1] and fingers[2]:
        return SCAN_COMPLETE       # ✌ Peace
    if count == 1 and fingers[0]:
        return EMERGENCY_STOP      # 👍 Thumb
    return None


# ---------------- MAIN ENTRY ----------------
def start_gesture_control(state_manager, arduino):

    def run():
        print("⏳ Warming up gesture system...")
        time.sleep(3)  # prevent false detection at startup
        print("✅ Gesture system ready")
        print("✋ Gesture control started")

        cap = cv2.VideoCapture(0)

        last_time = 0
        COOLDOWN = 2  # seconds

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            command = None

            if result.multi_hand_landmarks:
                hand = result.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(
                    frame, hand, mp_hands.HAND_CONNECTIONS
                )

                count, fingers = count_fingers(hand)
                command = get_gesture(count, fingers)

            # 🔒 STATE-BASED SAFETY CHECK
            if command:
                current_state = state_manager.get_state()

                # Emergency gesture allowed ONLY during SCANNING
                if command == EMERGENCY_STOP and current_state != "SCANNING":
                    command = None

            # ---------------- EXECUTE COMMAND ----------------
            now = time.time()
            if command and (now - last_time) > COOLDOWN:
                response = validate_and_process(
                    command,
                    state_manager.get_state()
                )

                state_manager.set_state(response["next_state"])

                if response["arduino_command"]:
                    arduino.send(response["arduino_command"])

                print(f"[GESTURE] {command} → {response['message']}")
                last_time = now

            # Preview window (optional)
            cv2.putText(
                frame,
                f"STATE: {state_manager.get_state()}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.imshow("Gesture Control", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    threading.Thread(target=run, daemon=True).start()
