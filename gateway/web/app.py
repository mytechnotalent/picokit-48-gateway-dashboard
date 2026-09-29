"""Flask dashboard serving authenticated telemetry from SQLite.

The application exposes a REST endpoint that returns recent authenticated
telemetry frames and events as JSON, plus a single page that renders the
temperature and humidity history with Chart.js. Only authenticated rows
reach the database, so the page can treat every point as trusted.

Parameters
----------
None

Returns
-------
None
"""

import argparse
import sqlite3
import sys

from flask import Flask
from flask import current_app
from flask import jsonify
from flask import render_template

DEFAULT_DB = "gateway.db"
SELECT_TELEMETRY = "SELECT * FROM telemetry ORDER BY id DESC LIMIT ?"
SELECT_EVENTS = "SELECT * FROM events ORDER BY id DESC LIMIT ?"
TELEMETRY_LIMIT = 200
EVENT_LIMIT = 100


def _rows(path, query, args=()):
    """Run a read-only query and return dictionary rows.

    Parameters
    ----------
    path : str
        SQLite database path.
    query : str
        Parameterized SELECT statement.
    args : tuple
        Query parameters.

    Returns
    -------
    list of dict
        Result rows as dictionaries.
    """
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        cursor = connection.execute(query, args)
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        return []
    finally:
        connection.close()


def index():
    """Render the Chart.js telemetry dashboard page.

    Parameters
    ----------
    None

    Returns
    -------
    str
        Rendered dashboard HTML.
    """
    return render_template("index.html")


def _fold(entry, key, value):
    """Fold one optional sample into a min and max pair.

    Parameters
    ----------
    entry : dict
        Mutable per-node summary entry.
    key : str
        Base metric name such as temp or hum.
    value : int or None
        Sample value in tenths, or None when absent.

    Returns
    -------
    None
    """
    if value is None:
        return
    low = key + "_min"
    high = key + "_max"
    if entry.get(low) is None or value < entry[low]:
        entry[low] = value
    if entry.get(high) is None or value > entry[high]:
        entry[high] = value


def _accumulate(entry, row):
    """Fold one telemetry row into a per-node summary entry.

    Parameters
    ----------
    entry : dict
        Mutable per-node summary entry.
    row : dict
        Telemetry row to fold.

    Returns
    -------
    None
    """
    entry["count"] += 1
    _fold(entry, "temp", row.get("temp_tenths"))
    _fold(entry, "hum", row.get("hum_tenths"))


def _summarize(rows):
    """Compute per-node count, temperature, and humidity extremes.

    Parameters
    ----------
    rows : list of dict
        Telemetry rows to summarize.

    Returns
    -------
    list of dict
        One summary entry per node ordered by node identifier.
    """
    stats = {}
    for row in rows:
        node = row.get("node")
        entry = stats.setdefault(node, {"node": node, "count": 0})
        _accumulate(entry, row)
    return sorted(stats.values(), key=lambda item: item["node"] or 0)


def summary():
    """Return per-node telemetry summary statistics as JSON.

    Parameters
    ----------
    None

    Returns
    -------
    flask.Response
        JSON array of per-node summary rows.
    """
    path = current_app.config["DB_PATH"]
    rows = _rows(path, SELECT_TELEMETRY, (TELEMETRY_LIMIT,))
    return jsonify(_summarize(rows))


def telemetry():
    """Return recent authenticated telemetry frames as JSON.

    Parameters
    ----------
    None

    Returns
    -------
    flask.Response
        JSON array of telemetry rows in chronological order.
    """
    path = current_app.config["DB_PATH"]
    rows = _rows(path, SELECT_TELEMETRY, (TELEMETRY_LIMIT,))
    return jsonify(list(reversed(rows)))


def events():
    """Return recent gateway events as JSON.

    Parameters
    ----------
    None

    Returns
    -------
    flask.Response
        JSON array of event rows, newest first.
    """
    path = current_app.config["DB_PATH"]
    rows = _rows(path, SELECT_EVENTS, (EVENT_LIMIT,))
    return jsonify(rows)


def create_app(db_path=DEFAULT_DB):
    """Create the Flask application bound to a SQLite database.

    Parameters
    ----------
    db_path : str
        SQLite database path.

    Returns
    -------
    flask.Flask
        Configured Flask application.
    """
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path
    app.add_url_rule("/", "index", index)
    app.add_url_rule("/api/telemetry", "telemetry", telemetry)
    app.add_url_rule("/api/events", "events", events)
    app.add_url_rule("/api/summary", "summary", summary)
    return app


def _parse_args(argv):
    """Parse web dashboard command-line arguments.

    Parameters
    ----------
    argv : list of str or None
        Argument vector without the program name.

    Returns
    -------
    argparse.Namespace
        Parsed dashboard arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=DEFAULT_DB, help="SQLite DB path")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8000, help="Bind port")
    return parser.parse_args(argv)


def main(argv=None):
    """Run the dashboard development server.

    Parameters
    ----------
    argv : list of str or None
        Argument vector without the program name.

    Returns
    -------
    int
        Zero on clean shutdown.
    """
    args = _parse_args(argv)
    app = create_app(args.db)
    app.run(host=args.host, port=args.port, debug=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
