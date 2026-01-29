# ======================================
# voice_recognition.py
# ======================================

import speech_recognition as sr
import threading
from difflib import SequenceMatcher
from core_logic.command_validator import RESET


from core_logic.command_validator import (
    validate_and_process,
    START_SCAN,
    STOP_SCAN,
    EMERGENCY_STOP
)


def start_voice_control(state_manager, arduino):
    """
    Starts voice recognition in a background thread.
    Voice → Command Validator → State Manager → Arduino
    """

    def listen():
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("🎤 Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source)

        print("🎤 Voice control started")
        print("Say: start scan | stop scan | emergency")

        # Fuzzy matching threshold
        SIMILARITY_THRESHOLD = 0.8

        def is_similar(input_text, target_cmd):
             return SequenceMatcher(None, input_text, target_cmd).ratio() > SIMILARITY_THRESHOLD

        while True:
            try:
                print("👂 Listening...")
                with mic as source:
                    audio = recognizer.listen(
                        source, timeout=3, phrase_time_limit=3
                    )

                print("🧠 Processing audio...")
                text = recognizer.recognize_google(audio).lower()
                print(f"[VOICE HEARD]: '{text}'")

                command = None
                
                # Check commands with fuzzy matching
                if is_similar(text, "start scan") or "start scan" in text or "scanning" in text:
                    command = START_SCAN
                elif is_similar(text, "stop scan") or "stop scan" in text:
                    command = STOP_SCAN
                # 🔁 RESET SYSTEM (VOICE)
                elif "reset" in text or "clear emergency" in text:
                    command = RESET
                elif "emergency" in text or is_similar(text, "emergency stop"):
                    command = EMERGENCY_STOP

                if not command:
                    print("⚠️ No valid command detected")
                    continue

                print("STATE BEFORE:", state_manager.get_state())

                # ✅ CORRECT USAGE (DICT)
                result = validate_and_process(
                    command, state_manager.get_state()
                )

                state_manager.set_state(result["next_state"])

                print("STATE AFTER:", state_manager.get_state())

                if result["arduino_command"]:
                    arduino.send(result["arduino_command"])

                print("✅", result["message"])
                print("-" * 30)

            except Exception as e:
                print("Voice error:", e)

    threading.Thread(target=listen, daemon=True).start()
