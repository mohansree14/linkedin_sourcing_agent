#!/bin/bash
# Start Streamlit Web Application
# LinkedIn Sourcing Agent - Professional Web Interface

echo "🎯 Starting LinkedIn Sourcing Agent Web Application..."
echo "======================================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider activating your virtual environment first:"
    echo "   source venv/bin/activate"
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python -c "import streamlit, plotly, pandas" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Core dependencies found"
else
    echo "❌ Missing dependencies. Installing..."
    pip install streamlit plotly pandas
fi

# Set environment variables for demo mode
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

echo ""
echo "🚀 Launching Streamlit application..."
echo "   URL: http://localhost:8501"
echo "   Docs: Check the sidebar for help"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================================="

# Start Streamlit
streamlit run streamlit_app.py
