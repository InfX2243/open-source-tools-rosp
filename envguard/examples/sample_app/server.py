import os

port = int(os.getenv("PORT", "8000"))
database_url = os.environ["DATABASE_URL"]
stripe_secret = os.getenv("STRIPE_SECRET_KEY")
redis_host = os.environ.get("REDIS_URL", "localhost")

print(f"Starting server on port {port} connecting to {database_url}")
