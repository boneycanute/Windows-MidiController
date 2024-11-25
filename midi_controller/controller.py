"""Main MIDI controller module."""

import os
import time
import pygame.midi
import logging
from datetime import datetime
from .config import Config
from .actions.pad_actions import PadActions
from .actions.knob_actions import KnobActions

class AkaiMPKMiniAutomation:
    """Main class for MIDI controller automation."""
    
    def __init__(self, log_level=logging.INFO):
        """Initialize the MIDI controller automation."""
        # Set up logging
        self.setup_logging(log_level)
        
        # Initialize components
        self.config = Config(logger=self.logger)
        self.pad_actions = PadActions(logger=self.logger)
        self.knob_actions = KnobActions(logger=self.logger)
        
        # Initialize MIDI
        self.midi_input = None
        self.initialize_midi()
    
    def setup_logging(self, log_level):
        """Set up logging configuration."""
        self.logger = logging.getLogger("MPKMini")
        self.logger.setLevel(log_level)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        # Create file handler
        log_file = f"logs/midi_controller_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def initialize_midi(self):
        """Initialize MIDI input device."""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Cleanup any existing MIDI resources
                if self.midi_input:
                    self.midi_input.close()
                pygame.midi.quit()
                pygame.midi.init()
                
                # List all MIDI devices for debugging
                self.logger.info(f"Found {pygame.midi.get_count()} MIDI devices:")
                for i in range(pygame.midi.get_count()):
                    info = pygame.midi.get_device_info(i)
                    device_name = info[1].decode('utf-8')
                    is_input = info[2] == 1
                    is_output = info[3] == 1
                    self.logger.info(f"Device {i}: {device_name} (Input: {is_input}, Output: {is_output})")
                
                # Find Akai MPK Mini device
                for i in range(pygame.midi.get_count()):
                    info = pygame.midi.get_device_info(i)
                    device_name = info[1].decode('utf-8').lower()
                    if 'mpk mini' in device_name and info[2] == 1:  # Input device
                        self.midi_input = pygame.midi.Input(i)
                        self.logger.info(f"Connected to MIDI device: {info[1].decode('utf-8')}")
                        return
                
                self.logger.error("Akai MPK Mini not found")
                return
                
            except Exception as e:
                retry_count += 1
                self.logger.warning(f"Failed to initialize MIDI (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    self.logger.info("Retrying in 1 second...")
                    time.sleep(1)
                else:
                    self.logger.error("Failed to initialize MIDI after multiple attempts")
    
    def handle_pad_action(self, note):
        """Handle pad press action."""
        action = self.config.get_pad_action(str(note))
        if action:
            try:
                if hasattr(self.pad_actions, action.lower().replace('/', '_').replace(' ', '_')):
                    method = getattr(self.pad_actions, action.lower().replace('/', '_').replace(' ', '_'))
                    method()
                else:
                    self.logger.warning(f"No handler found for pad action: {action}")
            except Exception as e:
                self.logger.error(f"Error executing pad action {action}: {e}")
    
    def handle_knob_action(self, cc, value):
        """Handle knob turn action."""
        action = self.config.get_knob_action(str(cc))
        if action:
            try:
                # Log raw MIDI values
                self.logger.info(f"Received knob CC: {cc}, value: {value}")
                
                # Normalize MIDI value (0-127) to 0-1 range
                normalized_value = value / 127.0
                self.logger.info(f"Normalized value: {normalized_value:.2f}")
                
                # Execute action
                self.knob_actions.handle_action(action, normalized_value)
            except Exception as e:
                self.logger.error(f"Error executing knob action {action}: {e}")
    
    def start_monitoring(self):
        """Start monitoring MIDI input."""
        if not self.midi_input:
            self.logger.error("No MIDI input device available")
            return
        
        self.logger.info("Started monitoring MIDI input")
        try:
            while True:
                if self.midi_input.poll():
                    events = self.midi_input.read(10)
                    for event in events:
                        status = event[0][0]
                        data1 = event[0][1]
                        data2 = event[0][2]
                        
                        if status == 144 and data2 > 0:  # Note On (Pad press)
                            self.handle_pad_action(data1)
                        elif status == 176:  # Control Change (Knob turn)
                            self.handle_knob_action(data1, data2)
                
                time.sleep(0.001)  # Prevent CPU overload
                
        except KeyboardInterrupt:
            self.logger.info("Stopping MIDI monitoring")
        except Exception as e:
            self.logger.error(f"Error in MIDI monitoring: {e}")
        finally:
            if self.midi_input:
                self.midi_input.close()
            pygame.midi.quit()
    
    def cleanup(self):
        """Clean up resources."""
        if self.midi_input:
            self.midi_input.close()
        pygame.midi.quit()
        self.logger.info("Cleaned up resources")

def main():
    """Main entry point."""
    try:
        mpk = AkaiMPKMiniAutomation(log_level=logging.INFO)
        mpk.start_monitoring()
    except Exception as e:
        logging.error(f"Application error: {e}")
    finally:
        mpk.cleanup()

if __name__ == "__main__":
    main()
