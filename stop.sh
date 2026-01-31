#!/bin/bash

echo "Stopping WhiteRabbit..."

# Kill Streamlit
if [ -f .streamlit.pid ]; then
    STREAMLIT_PID=$(cat .streamlit.pid)
    kill $STREAMLIT_PID 2>/dev/null && echo "Streamlit stopped (PID: $STREAMLIT_PID)" || echo "Streamlit not running"
    rm .streamlit.pid
else
    pkill -f "streamlit run Dashboard.py" && echo "Streamlit stopped" || echo "Streamlit not running"
fi

# Kill Scanner Worker
if [ -f .scanner.pid ]; then
    SCANNER_PID=$(cat .scanner.pid)
    kill $SCANNER_PID 2>/dev/null && echo "Scanner worker stopped (PID: $SCANNER_PID)" || echo "Scanner worker not running"
    rm .scanner.pid
else
    pkill -f "scanner_worker.py" && echo "Scanner worker stopped" || echo "Scanner worker not running"
fi

echo ""
echo "WhiteRabbit stopped."