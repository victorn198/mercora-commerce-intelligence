from __future__ import annotations

import os

from application import app, server


if __name__ == "__main__":
    debug = os.getenv("APP_ENV", "production").lower() == "development"
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "8050")),
        debug=debug,
        use_reloader=False,
    )
