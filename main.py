from fastapi import FastAPI
import os
from sentry_asgi import SentryMiddleware
import sentry_sdk
import socket
from lib.exporter import Exporter


# Main config
if socket.gethostname() == 'bma-app-101':  # pragma: no cover
    environment = 'Prod'
else:  # pragma: no cover
    environment = 'DEV'
sentry_sdk.init(dsn="https://a1f1ef7bb02a450692ec3f7fbd328978@o229295.ingest.sentry.io/6261843", environment=environment)

app = FastAPI(
    title="Transportation management system API",
    description="This project is used to connect Jeeves to carriers API",
    version="1.0.0",
)

@app.get("/get_order_data")
def get_order_data(shipment_id):
    exporter_object = Exporter(shipment_id)
    return exporter_object.get_shipment_data()

@app.post("/addShipment")
def addShipment(shipment_id):
    exporter_object = Exporter(shipment_id)
    return exporter_object.add_new_shipment()
    
# Sentry config
app = SentryMiddleware(app)
# Uvicorn config
if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if dir_path == "/home/ubuntu/dev/tms":
        port = 8401
    else:
        port = 8400
    log_config = uvicorn.config.LOGGING_CONFIG  # type: ignore
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    log_config["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, debug=True, log_config=log_config)
