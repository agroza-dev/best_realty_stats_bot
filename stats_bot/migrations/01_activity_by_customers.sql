CREATE TABLE IF NOT EXISTS activity_by_customers (
    date_time TIMESTAMP DEFAULT NULL,
    deal_id INTEGER DEFAULT NULL,
    status STRING NOT NULL,
    event_manager STRING NOT NULL
);