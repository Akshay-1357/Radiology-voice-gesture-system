# ===============================
# state_manager.py
# ===============================

# -------- SYSTEM STATES --------
IDLE = "IDLE"
SCANNING = "SCANNING"
COMPLETED = "COMPLETED"
EMERGENCY = "EMERGENCY"


class StateManager:
    """
    Central authority for managing system state.
    All modules must read/update state ONLY through this class.
    """

    def __init__(self):
        self._state = IDLE

    def get_state(self):
        """Return current system state"""
        return self._state

    def set_state(self, new_state):
        """Update system state safely"""
        if new_state in [IDLE, SCANNING, COMPLETED, EMERGENCY]:
            self._state = new_state
            return True
        return False

    def reset(self):
        """Reset system to IDLE"""
        self._state = IDLE

    def is_idle(self):
        return self._state == IDLE

    def is_scanning(self):
        return self._state == SCANNING

    def is_completed(self):
        return self._state == COMPLETED

    def is_emergency(self):
        return self._state == EMERGENCY
