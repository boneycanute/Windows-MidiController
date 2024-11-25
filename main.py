"""Main entry point for MIDI Controller application."""

import sys
import logging
from midi_controller import AkaiMPKMiniAutomation

def main():
    """Run the MIDI controller application."""
    try:
        controller = AkaiMPKMiniAutomation(log_level=logging.INFO)
        print("MIDI Controller started. Press Ctrl+C to exit.")
        controller.start_monitoring()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.cleanup()

if __name__ == "__main__":
    main()
