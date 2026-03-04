# Break Timer Design

## Overview
Local break reminder for Windows. Runs in system tray.

## Two Modes
- **Warning**: Dismissible popup notification
- **Forced**: Fullscreen semi-transparent overlay blocking input, snooze-able

## Stack
Python + customtkinter + pystray + Pillow + ctypes

## Components
- settings.py: JSON config
- timer.py: background timer thread
- overlay.py: fullscreen break overlay
- settings_ui.py: settings window
- main.py: tray app entry point
