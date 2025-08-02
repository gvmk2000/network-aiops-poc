DEVICES = ["router01", "router02", "base01", "base02", "switch01"]

def dict_factory(cursor, row):
    """Helper to return sqlite rows as dicts."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
