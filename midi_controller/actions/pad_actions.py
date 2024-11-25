"""Pad actions for MIDI controller."""

import os
import time
import subprocess
import pyautogui
import win32gui
import win32api
import win32con
import logging
from ..utils.window_utils import WindowUtils
from ..utils.process_utils import ProcessUtils

class PadActions:
    """Handles all pad-related actions."""
    
    def __init__(self, logger=None):
        """Initialize PadActions."""
        self.logger = logger or logging.getLogger(__name__)
        self.window_utils = WindowUtils(logger)
        self.process_utils = ProcessUtils(logger)
    
    def previous_track(self):
        """Handle Previous Track action."""
        pyautogui.press('prevtrack')
        self.logger.info("Previous track command sent")
    
    def play_pause_spotify(self):
        """Handle Play/Pause Spotify action."""
        if not self.process_utils.is_spotify_running():
            self.logger.info("Spotify not found, launching...")
            if not self.process_utils.launch_spotify():
                return
        
        pyautogui.press('playpause')
        self.logger.info("Play/Pause command sent to Spotify")
    
    def next_track(self):
        """Handle Next Track action."""
        pyautogui.press('nexttrack')
        self.logger.info("Next track command sent")
    
    def launch_focus_slack(self):
        """Handle Launch/Focus Slack action."""
        slack_window = self.window_utils.find_window_by_title("Slack")
        if slack_window:
            if self.window_utils.focus_window(slack_window):
                self.logger.info("Focused Slack window")
            else:
                self.logger.warning("Failed to focus Slack window")
        else:
            self.logger.info("Slack not found, launching...")
            try:
                subprocess.Popen([os.path.expandvars("%LOCALAPPDATA%\\slack\\slack.exe")])
            except Exception as e:
                self.logger.error(f"Failed to launch Slack: {e}")
    
    def launch_focus_windsurf(self):
        """Handle Launch/Focus Windsurf action."""
        windsurf_window = self.window_utils.find_window_by_title("Windsurf")
        if windsurf_window:
            if self.window_utils.focus_window(windsurf_window):
                self.logger.info("Focused Windsurf window")
            else:
                self.logger.warning("Failed to focus Windsurf window")
        else:
            self.logger.info("Windsurf not found, launching...")
            try:
                # Update this path to match your Windsurf installation
                windsurf_path = "C:\\Program Files\\Windsurf\\Windsurf.exe"  # Example path
                if os.path.exists(windsurf_path):
                    subprocess.Popen([windsurf_path])
                else:
                    self.logger.error(f"Windsurf not found at: {windsurf_path}")
            except Exception as e:
                self.logger.error(f"Failed to launch Windsurf: {e}")
    
    def voice_recognition(self):
        """Handle Voice Recognition action."""
        pyautogui.hotkey('win', 'h')
        self.logger.info("Triggered voice recognition")
    
    def toggle_audio_output(self):
        """Handle Toggle Audio Output action."""
        pyautogui.hotkey('win', 'ctrl', 'v')
        self.logger.info("Opened audio output selection")
    
    def move_to_next_display(self):
        """Handle Move to Next Display action."""
        active_window = win32gui.GetForegroundWindow()
        if active_window:
            try:
                # Get window position and size
                rect = win32gui.GetWindowRect(active_window)
                x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
                
                # Get display information
                monitors = win32api.EnumDisplayMonitors(None, None)
                
                # Find current monitor
                current_monitor = None
                for i, monitor in enumerate(monitors):
                    monitor_rect = win32gui.GetMonitorInfo(monitor[0])['Monitor']
                    if (x >= monitor_rect[0] and x < monitor_rect[2] and
                        y >= monitor_rect[1] and y < monitor_rect[3]):
                        current_monitor = i
                        break
                
                if current_monitor is not None:
                    # Move to next monitor
                    next_monitor = (current_monitor + 1) % len(monitors)
                    next_rect = win32gui.GetMonitorInfo(monitors[next_monitor][0])['Monitor']
                    
                    # Calculate new position
                    new_x = next_rect[0] + (x - monitors[current_monitor][1][0])
                    new_y = next_rect[1] + (y - monitors[current_monitor][1][1])
                    
                    # Move window
                    win32gui.MoveWindow(active_window, new_x, new_y, w, h, True)
                    self.logger.info("Moved window to next display")
                else:
                    self.logger.warning("Could not determine current monitor")
            except Exception as e:
                self.logger.error(f"Failed to move window: {e}")
        else:
            self.logger.warning("No active window found")
    
    def minimize_window(self):
        """Handle Minimize Window action."""
        active_window = win32gui.GetForegroundWindow()
        if active_window:
            window_title = win32gui.GetWindowText(active_window)
            self.logger.info(f"Attempting to minimize window: {window_title}")
            if self.window_utils.minimize_window(active_window):
                self.logger.info(f"Successfully minimized window: {window_title}")
            else:
                self.logger.warning(f"Failed to minimize window: {window_title}")
        else:
            self.logger.warning("No active window found to minimize")
    
    def maximize_window(self):
        """Handle Maximize Window action."""
        active_window = win32gui.GetForegroundWindow()
        if active_window:
            window_title = win32gui.GetWindowText(active_window)
            self.logger.info(f"Attempting to maximize window: {window_title}")
            if self.window_utils.maximize_window(active_window):
                self.logger.info(f"Successfully maximized window: {window_title}")
            else:
                self.logger.warning(f"Failed to maximize window: {window_title}")
        else:
            self.logger.warning("No active window found to maximize")
    
    def switch_window(self):
        """Handle Switch Window (Alt+Tab) action."""
        try:
            self.logger.info("Switching to next window using Alt+Tab")
            pyautogui.hotkey('alt', 'tab')
            self.logger.info("Successfully switched to next window")
        except Exception as e:
            self.logger.error(f"Failed to switch window: {e}")
    
    def open_file_explorer(self):
        """Handle Open File Explorer action."""
        try:
            self.logger.info("Opening File Explorer")
            subprocess.Popen('explorer')
            self.logger.info("Successfully opened File Explorer")
        except Exception as e:
            self.logger.error(f"Failed to open File Explorer: {e}")
    
    def show_desktop(self):
        """Handle Show Desktop action."""
        try:
            self.logger.info("Showing desktop using Win+D")
            pyautogui.hotkey('win', 'd')
            self.logger.info("Successfully showed desktop")
        except Exception as e:
            self.logger.error(f"Failed to show desktop: {e}")
