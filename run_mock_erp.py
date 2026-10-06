import uvicorn
from worker.config import settings

if __name__ == "__main__":
    print(f"Starting CentrAlign Mock ERP on {settings.MOCK_ERP_HOST}:{settings.MOCK_ERP_PORT}...")
    print(f"Portal URL: {settings.MOCK_ERP_BASE_URL}/login")
    print("Credentials: admin / company_secure_pass")
    uvicorn.run("mock_erp.app:app", host=settings.MOCK_ERP_HOST, port=settings.MOCK_ERP_PORT, reload=False)
