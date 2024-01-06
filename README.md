# 1. Install Dependencies
```bash
pip install -r requirements.txt
```

# 2. Run the app
```bash
uvicorn main:app --reload
```
The default port is set to 8000. To run the server on a different port, use the --port option. For example:
```bash
uvicorn main:app --reload --port 8080
```

# 3. Access the API documentation
1. After starting the server, visit http://127.0.0.1:8000/docs in your browser to access the Swagger-based interactive API documentation.

2. Alternatively, you can use the http://127.0.0.1:8000/redoc endpoint for the ReDoc documentation.
