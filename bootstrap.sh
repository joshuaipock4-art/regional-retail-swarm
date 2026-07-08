#!/bin/bash
# Use exec to ensure Supervisor tracks the Python PID, not the bash script PID
exec python3 core_engine.py
