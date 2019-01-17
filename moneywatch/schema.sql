DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS ruleset;


CREATE TABLE categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  type TEXT CHECK( type IN ('in', 'out') ) NOT NULL,
  parent INTEGER NULL REFERENCES categories,
  budget_monthly INTEGER NOT NULL DEFAULT 0);


CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  days INTEGER NOT NULL,
  valuta NUMERIC NOT NULL,
  full_text TEXT NOT NULL,
  description TEXT NULL,
  rule_id INTEGER NULL REFERENCES ruleset,
  category_id INTEGER REFERENCES categories,
  trend NUMERIC NULL,
  trend_calculated INTEGER CHECK( trend_calculated IN(0, 1) ) NOT NULL DEFAULT 0
  );

 
CREATE TABLE ruleset (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  group_name TEXT NULL,
  pattern TEXT NOT NULL,
  type TEXT CHECK( type IN ('in', 'out') ) NOT NULL,
  description TEXT NOT NULL,
  category_id INTEGER REFERENCES categories,
  regular INTEGER NULL DEFAULT 0,
  next_days INTEGER NULL ,
  next_valuta INTEGER NULL
  );


CREATE INDEX idx_days ON transactions (days);
CREATE INDEX idx_rule_id ON transactions (rule_id);
CREATE INDEX idx_category_id ON transactions (category_id);

INSERT INTO categories (name, type) VALUES ('Earnings', 'in');
INSERT INTO categories (name, type) VALUES ('Spendings', 'out');
