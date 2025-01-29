from dagster import asset, Output, MetadataValue
import pandas as pd


@asset
def generate_users():
    """Generate sample user data"""
    df = pd.DataFrame({
        'user_id': range(1, 101),
        'username': [f'user_{i}' for i in range(1, 101)],
        'score': range(50, 150)
    })
    return df


@asset(required_resource_keys={"postgres"})  # Declare postgres as required resource
def update_user_database(context, generate_users):  # Add context, remove postgres_db parameter
    """Update PostgreSQL database with user data"""
    with context.resources.postgres.get_connection() as conn:  # Use postgres through context
        # Create table if not exists
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username VARCHAR(50),
            score INTEGER
        )
        """

        with conn.cursor() as cur:
            cur.execute(create_table_sql)

            # Upsert data
            for _, row in generate_users.iterrows():
                upsert_sql = """
                INSERT INTO users (user_id, username, score)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) 
                DO UPDATE SET score = EXCLUDED.score
                """
                cur.execute(upsert_sql, (
                    row['user_id'],
                    row['username'],
                    row['score']
                ))

        conn.commit()

        # Verify data
        result = pd.read_sql("SELECT * FROM users LIMIT 5", conn)
        return Output(
            result,
            metadata={
                "rows": len(result),
                "preview": MetadataValue.md(result.to_markdown())
            }
        )