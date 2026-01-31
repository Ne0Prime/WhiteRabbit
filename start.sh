#!/bin/bash

echo "Starting WhiteRabbit..."

# Start Streamlit in background
streamlit run Dashboard.py > streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "Streamlit started (PID: $STREAMLIT_PID)"

# Start Scanner Worker in background
python scanner_worker.py > scanner.log 2>&1 &
SCANNER_PID=$!
echo "Scanner worker started (PID: $SCANNER_PID)"

# Save PIDs
echo $STREAMLIT_PID > .streamlit.pid
echo $SCANNER_PID > .scanner.pid

echo ""
echo "WhiteRabbit is running!"
echo "Dashboard: http://localhost:8501"
echo "Logs: tail -f streamlit.log scanner.log"
echo "Stop: ./stop.sh"