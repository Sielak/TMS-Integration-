import gunicorn

def test_config():
    assert gunicorn.name == "gunicorn config for FastAPI TMS"
    assert gunicorn.accesslog == "/home/ubuntu/logs/tms/access.log"
    assert gunicorn.errorlog == "/home/ubuntu/logs/tms/error.log"
    assert gunicorn.bind == "0.0.0.0:8400"
    assert gunicorn.worker_class == "uvicorn.workers.UvicornWorker"
    assert gunicorn.timeout == 120
