# ===============================
# command_validator.py
# ===============================

from core_logic.state_manager import (
    IDLE,
    SCANNING,
    COMPLETED,
    EMERGENCY
)

# -------- COMMANDS --------
START_SCAN = "START_SCAN"
STOP_SCAN = "STOP_SCAN"
EMERGENCY_STOP = "EMERGENCY_STOP"
SCAN_COMPLETE = "SCAN_COMPLETE"

VALID_COMMANDS = [
    START_SCAN,
    STOP_SCAN,
    EMERGENCY_STOP,
    SCAN_COMPLETE
]


def validate_and_process(command, current_state):
    """
    Core decision-making function.

    Parameters:
        command (str): Command from voice / gesture
        current_state (str): Current system state

    Returns:
        dict:
            {
                "next_state": str,
                "arduino_command": str or None,
                "message": str
            }
    """

    # -------- INVALID COMMAND --------
    if command not in VALID_COMMANDS:
        return {
            "next_state": current_state,
            "arduino_command": None,
            "message": "Invalid command"
        }

    # -------- EMERGENCY (HIGHEST PRIORITY) --------
    if command == EMERGENCY_STOP:
        return {
            "next_state": EMERGENCY,
            "arduino_command": "EMERGENCY_STOP",
            "message": "Emergency stop activated"
        }

    # -------- START SCAN --------
    if command == START_SCAN:
        if current_state == IDLE:
            return {
                "next_state": SCANNING,
                "arduino_command": "START_SCAN",
                "message": "Scan started"
            }
        else:
            return {
                "next_state": current_state,
                "arduino_command": None,
                "message": "Scan already running or not allowed"
            }

    # -------- STOP SCAN --------
    if command == STOP_SCAN:
        if current_state == SCANNING:
            return {
                "next_state": IDLE,
                "arduino_command": "STOP_SCAN",
                "message": "Scan stopped"
            }
        else:
            return {
                "next_state": current_state,
                "arduino_command": None,
                "message": "No scan to stop"
            }

    # -------- SCAN COMPLETED --------
    if command == SCAN_COMPLETE:
        if current_state == SCANNING:
            return {
                "next_state": COMPLETED,
                "arduino_command": "STOP_SCAN",
                "message": "Scan completed successfully"
            }
        else:
            return {
                "next_state": current_state,
                "arduino_command": None,
                "message": "Scan not in progress"
            }

    # -------- FALLBACK --------
    return {
        "next_state": current_state,
        "arduino_command": None,
        "message": "Unhandled case"
    }
