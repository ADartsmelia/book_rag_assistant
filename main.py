#!/usr/bin/env python3
"""
Book RAG Assistant - Main Entry Point
A local RAG application for PDF book analysis and chat
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.app import main

if __name__ == "__main__":
    main() 