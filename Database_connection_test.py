import oracledb

DB_USER = "Gawk"
DB_PASS = "Gawk"
DB_HOST = "Gawk.Gawk.Gawk.Gawk"
DB_PORT = Gawk
DB_SERVICE = "Gawk"

tables = [
    "FACOA",
    "STGS_COLORM",
    "ARTICLE_SIZE_TYPE",
    "STGS_ARTICLEM",
    "ARTICLE_SIZEM",
    "STGS_ARTICLE_CSM"
]

try:
    dsn = oracledb.makedsn(
        DB_HOST,
        DB_PORT,
        service_name=DB_SERVICE
    )

    connection = oracledb.connect(
        user=DB_USER,
        password=DB_PASS,
        dsn=dsn
    )

    cursor = connection.cursor()

    for table in tables:
        print("\n" + "=" * 60)
        print(f"Table: {table}")
        print("=" * 60)

        cursor.execute(f"SELECT * FROM {table} FETCH FIRST 5 ROWS ONLY")

        # Column names
        columns = [col[0] for col in cursor.description]
        print("Columns:", columns)

        rows = cursor.fetchall()
        for row in rows:
            print(row)

    cursor.close()
    connection.close()

except Exception as e:
    print("Error:", e)
