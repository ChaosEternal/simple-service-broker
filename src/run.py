#!/usr/bin/env python
import os
from app import app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("VCAP_APP_PORT", "8080")), debug=True)
