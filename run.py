"""
Main execution entry point for MoRTH Indian Road Accident Analytics Platform.
"""
import sys
import os

# Ensure current workspace directory is on python sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.server import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"================================================================")
    print(f" MoRTH Road Accident Analytics & AI Risk Prediction Platform")
    print(f" Running at: http://127.0.0.1:{port}")
    print(f"================================================================")
    app.run(host='0.0.0.0', port=port, debug=False)
