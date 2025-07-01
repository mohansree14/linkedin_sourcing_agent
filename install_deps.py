#!/usr/bin/env python3
"""
Dependency Installation Script for LinkedIn Sourcing Agent
This script ensures all required dependencies are properly installed.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🔧 Installing LinkedIn Sourcing Agent Dependencies...")
    print("=" * 50)
    
    # Essential dependencies
    essential_deps = [
        "retrying",
        "tenacity", 
        "streamlit",
        "pandas",
        "plotly",
        "requests",
        "beautifulsoup4",
        "lxml",
        "openpyxl",
        "xlsxwriter"
    ]
    
    failed_installs = []
    
    for dep in essential_deps:
        print(f"Installing {dep}...")
        if not install_package(dep):
            failed_installs.append(dep)
    
    print("\n" + "=" * 50)
    
    if failed_installs:
        print(f"❌ Failed to install: {', '.join(failed_installs)}")
        print("Please install these manually:")
        for dep in failed_installs:
            print(f"  pip install {dep}")
    else:
        print("✅ All dependencies installed successfully!")
    
    # Try to install the main package
    print("\n🚀 Installing LinkedIn Sourcing Agent package...")
    try:
        os.chdir('/workspaces/linkedin_sourcing_agent')
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ LinkedIn Sourcing Agent package installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install main package: {e}")
    
    print("\n🎯 Setup complete! You can now run the Streamlit app:")
    print("  streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
