#!/bin/bash
set -e

export PORT=${PORT:-8501}
export PUBLIC_BASE_URL=${PUBLIC_BASE_URL:-"https://autonomous-ai-task-worker.onrender.com"}
export MAIN_APP_URL="https://autonomous-ai-task-worker.onrender.com"
export RENDER="true"

echo "=========================================================="
echo "Starting CentrAlign Autonomous Task Worker Platform"
echo "Public Base URL: $PUBLIC_BASE_URL"
echo "Active Port: $PORT"
echo "=========================================================="

# 1. Start Mock ERP backend on internal port 8000
echo "Starting Mock Enterprise ERP on 127.0.0.1:8000..."
python run_mock_erp.py &

# Wait for ERP to initialize
sleep 2

# 2. Check if Nginx reverse proxy is available
if command -v nginx > /dev/null 2>&1; then
    echo "Nginx detected: Starting Streamlit internally on port 8501..."
    streamlit run ui/dashboard.py --server.port 8501 --server.address 127.0.0.1 --server.headless true &
    
    echo "Configuring Nginx reverse proxy to expose Streamlit & ERP unified on PORT $PORT..."
    envsubst '${PORT}' < nginx.conf.template > /etc/nginx/nginx.conf
    exec nginx -g 'daemon off;'
else
    # Direct execution without Nginx
    echo "Starting Streamlit Dashboard on public port $PORT..."
    exec streamlit run ui/dashboard.py --server.port "$PORT" --server.address 0.0.0.0 --server.headless true
fi
