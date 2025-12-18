#!/bin/bash

echo "🧴 Setting up Skincare Advisor..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the app:"
echo "  source venv/bin/activate"
echo "  streamlit run src/ui/app.py"
echo ""
echo "The app will open at http://localhost:8501"
