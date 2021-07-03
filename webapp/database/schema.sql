CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email_address TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  active_subscriber BOOLEAN,
  website_path TEXT,
  stripe_customer_id TEXT,
  stripe_connect_account_id TEXT
);
