"""Configuration management for MIDI controller."""

import os
import json
import logging
from typing import Dict, Any

class Config:
    """Configuration manager for MIDI controller."""
    
    def __init__(self, config_file="midi_config.json", logger=None):
        """Initialize Config."""
        self.logger = logger or logging.getLogger(__name__)
        self.config_file = config_file
        self.pad_mappings = {}
        self.knob_mappings = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.pad_mappings = config.get('pad_mappings', {})
                    self.knob_mappings = config.get('knob_mappings', {})
                    self.logger.info("Configuration loaded successfully")
            else:
                self.logger.warning(f"Config file {self.config_file} not found, using defaults")
                self.create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self.create_default_config()
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            config = {
                'pad_mappings': self.pad_mappings,
                'knob_mappings': self.knob_mappings
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def create_default_config(self) -> None:
        """Create default configuration."""
        self.pad_mappings = {
            "36": "Previous Track",
            "37": "Play/Pause Spotify",
            "38": "Next Track",
            "39": "Launch/Focus Slack",
            "40": "Launch/Focus Windsurf",
            "41": "Voice Recognition",
            "42": "Toggle Audio Output",
            "43": "Move to Next Display"
        }
        
        self.knob_mappings = {
            "16": {
                "action": "System Volume",
                "min": 1,
                "max": 127
            },
            "17": {
                "action": "Spotify Volume",
                "min": 1,
                "max": 127
            },
            "18": {
                "action": "Firefox Volume",
                "min": 1,
                "max": 127
            },
            "19": {
                "action": "Screen Brightness",
                "min": 1,
                "max": 127
            }
        }
        
        self.save_config()
    
    def update_pad_mapping(self, note: str, action: str) -> None:
        """Update pad mapping and save config."""
        self.pad_mappings[str(note)] = action
        self.save_config()
    
    def update_knob_mapping(self, cc: str, action: str, min_val: int = 1, max_val: int = 127) -> None:
        """Update knob mapping and save config."""
        self.knob_mappings[str(cc)] = {
            "action": action,
            "min": min_val,
            "max": max_val
        }
        self.save_config()
    
    def get_pad_action(self, note: str) -> str:
        """Get action mapped to pad note."""
        return self.pad_mappings.get(str(note))
    
    def get_knob_action(self, cc: str) -> str:
        """Get action mapped to knob CC."""
        try:
            mapping = self.knob_mappings.get(str(cc))
            if mapping and isinstance(mapping, dict):
                return mapping.get("action")
            elif mapping and isinstance(mapping, str):
                return mapping  # Handle legacy string format
            return None
        except Exception as e:
            self.logger.error(f"Error getting knob action for CC {cc}: {e}")
            return None
