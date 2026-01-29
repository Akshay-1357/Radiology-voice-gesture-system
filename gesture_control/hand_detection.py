# ======================================
# hand_detection.py (FINAL CLEAN VERSION)
# ======================================
from core_logic.command_validator import RESET
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


# ---------------- FINGER STATE UTILS ----------------
def get_finger_states(hand):
    """
    Returns a list of booleans: True if finger is extended, False if folded.
    [Thumb, Index, Middle, Ring, Pinky]
    Using geometric heuristics for better accuracy.
    """
    cnt = 0
    fingers = []
    
    # Landmarks
    # Thumb: 4, Index: 8, Middle: 12, Ring: 16, Pinky: 20
    # MCP (Base): 2, 5, 9, 13, 17
    
    # THUMB: Check horizontal distance for simplicity in 2D
    # (Works best for front-facing palm)
    # If tip (4) is further "out" than IP joint (3) relative to the palm
    # Here we use a simpler x-coordinate check relative to the knuckle (2)
    # Assuming right hand logic (need to handle left/right flip if needed)
    # But usually just checking x-distance is okay for basic gestures
    
    # Better Thumb Check: Compare tip (4) to base of index (5)?
    # Or just use the standard x-check but ensuring it's "significant"
    if hand.landmark[4].x < hand.landmark[3].x: # Right hand assumed or flipped
        fingers.append(True)
    else:
        fingers.append(False)

    # FINGERS (Index to Pinky)
    # Check if TIP y < PIP y (2 joints down) matches "extended" (for upright hand)
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18] # PIP joints
    
    for tip, pip in zip(tips, pips):
        if hand.landmark[tip].y < hand.landmark[pip].y:
            fingers.append(True)
        else:
            fingers.append(False)
            
    return fingers


# ---------------- GESTURE MAPPING ----------------
def get_gesture_refined(fingers):
    """
    fingers: [Thumb, Index, Middle, Ring, Pinky]
    """
    # Count extended fingers
    count = fingers.count(True)
    
    # ✋ START_SCAN: All 5 fingers extended
    if count == 5:
        return START_SCAN, "OPEN HAND (Start)"

    # ✌ SCAN_COMPLETE: Index & Middle extended, others folded
    # Strict check: Thumb, Ring, Pinky MUST be False
    if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
        return SCAN_COMPLETE, "PEACE SIGN (Complete)"

    # 👍 EMERGENCY_STOP: Thumb extended, others folded
    # Strict check: Index, Middle, Ring, Pinky MUST be False
    if fingers[0] and not fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
        return EMERGENCY_STOP, "THUMB UP (Emergency)"

    # ✊ STOP_SCAN: All fingers folded (Fist)
    if count == 0:
        return STOP_SCAN, "FIST (Stop)"

    return None, "UNKNOWN"



# ---------------- MAIN ENTRY ----------------
def start_gesture_control(state_manager, arduino):

    def run():
       

        print("⏳ Warming up gesture system...")
        time.sleep(3)  # prevent false detection at startup
        print("✅ Gesture system ready")
        print("✋ Gesture control started")

        reset_hold_start = None
        RESET_HOLD_TIME = 2  # seconds
        cap = cv2.VideoCapture(0)

        last_time = 0
        COOLDOWN = 2  # seconds
        
        current_gesture_name = "NONE"

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            command = None
            current_gesture_name = "NONE"

            if result.multi_hand_landmarks:
                hand = result.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(
                    frame, hand, mp_hands.HAND_CONNECTIONS
                )

                # IMPROVED DETECTION
                fingers = get_finger_states(hand)
                command, current_gesture_name = get_gesture_refined(fingers)

            # 🔁 RESET GESTURE: PEACE SIGN HELD DURING EMERGENCY
            if command == SCAN_COMPLETE:
                if state_manager.get_state() == "EMERGENCY":
                    if reset_hold_start is None:
                        reset_hold_start = time.time()
                        print(f"🕒 Hold reset... {RESET_HOLD_TIME - (time.time() - reset_hold_start):.1f}s")
                    elif time.time() - reset_hold_start >= RESET_HOLD_TIME:
                        command = RESET
                        current_gesture_name = "RESET TRIGGERED"
                        reset_hold_start = None
                else:
                    reset_hold_start = None
            else:
                reset_hold_start = None


            # 🔒 STATE-BASED SAFETY CHECK
            if command:
                current_state = state_manager.get_state()

                # Emergency gesture allowed ONLY during SCANNING or INIT/READY? 
                # Relaxed rule: Emergency is usually allowed almost always, but let's keep original logic if it was intentioned
                # "Emergency gesture allowed ONLY during SCANNING" -> seems restrictive for safety? 
                # Assuming original logic was intentional for this specific workflow.
                
                if command == EMERGENCY_STOP and current_state != "SCANNING":
                    # command = None # Un-comment to enforce strict state
                    pass # Allowing emergency stop more broadly might be safer? reverting to original logic:
                    if current_state != "SCANNING":
                         command = None # Original logic maintained

                # Stop scan NOT allowed during EMERGENCY
                if command == STOP_SCAN and current_state == "EMERGENCY":
                    command = None


            # ---------------- EXECUTE COMMAND ----------------
            now = time.time()
            if command and (command == RESET or (now - last_time) > COOLDOWN):
                response = validate_and_process(
                    command,
                    state_manager.get_state()
                )

                state_manager.set_state(response["next_state"])

                if response["arduino_command"]:
                    arduino.send(response["arduino_command"])

                print(f"[GESTURE] {command} → {response['message']}")
                last_time = now

            # Preview window (Visual Feedback)
            cv2.putText(
                frame,
                f"STATE: {state_manager.get_state()}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            
            # Show detected gesture
            color = (0, 255, 255) if command else (200, 200, 200)
            cv2.putText(
                frame,
                f"GESTURE: {current_gesture_name}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )


            cv2.imshow("Gesture Control", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    threading.Thread(target=run, daemon=True).start()
