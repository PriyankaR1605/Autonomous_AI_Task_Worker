#!/bin/bash
set -e

echo "Starting CentrAlign Mock ERP backend on port 8000..."
python run_mock_erp.py &

echo "Waiting for Mock ERP to become ready..."
sleep 3

echo "Starting Streamlit Dashboard on port 8501..."
exec streamlit run ui/dashboard.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
