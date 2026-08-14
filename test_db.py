import pandas as pd

from app.database import check_connection, engine


if __name__ == "__main__":
    check_connection()
    df = pd.read_sql("SELECT id, name, buckilStatus, privacySetting FROM buckils LIMIT 10", engine)
    print(df)
