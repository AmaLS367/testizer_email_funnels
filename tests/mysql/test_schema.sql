-- Test schema for integration tests
-- This schema must be kept in sync with production schema for overlapping tables
-- (funnel_entries and brevo_sync_outbox) to ensure test accuracy.

-- Simple test tables for MODX database simulation
DROP TABLE IF EXISTS simpletest_users;

CREATE TABLE simpletest_users (
  Id INT NOT NULL AUTO_INCREMENT,
  Email VARCHAR(255) NULL,
  TestId INT NULL,
  Datep DATETIME NULL,
  Status INT NULL,
  PRIMARY KEY (Id),
  KEY idx_testid (TestId),
  KEY idx_datep (Datep)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- newid is a technical surrogate key used for the test schema.
-- Tests intentionally insert only Id and LangId, so newid must be AUTO_INCREMENT.
DROP TABLE IF EXISTS simpletest_test;

CREATE TABLE simpletest_test (
  newid INT NOT NULL AUTO_INCREMENT,
  Id INT NOT NULL,
  LangId INT NOT NULL,
  PRIMARY KEY (newid),
  KEY idx_langid (LangId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS simpletest_lang;

CREATE TABLE simpletest_lang (
  Id INT NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Analytics tables (must match production schema)
-- Drop brevo_sync_outbox first (it may reference funnel_entries)
DROP TABLE IF EXISTS brevo_sync_outbox;

DROP TABLE IF EXISTS funnel_entries;

CREATE TABLE funnel_entries (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  email VARCHAR(255) NOT NULL,
  funnel_type VARCHAR(50) NOT NULL,
  user_id INT NULL,
  test_id INT NULL,
  entered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  certificate_purchased TINYINT(1) NOT NULL DEFAULT 0,
  certificate_purchased_at DATETIME NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_funnel_entry_email_type_test (email, funnel_type, test_id),
  KEY idx_email_funnel (email, funnel_type),
  KEY idx_user_test (user_id, test_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE brevo_sync_outbox (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  funnel_entry_id INT UNSIGNED NOT NULL,
  operation_type VARCHAR(50) NOT NULL,
  payload TEXT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  retry_count INT UNSIGNED NOT NULL DEFAULT 0,
  last_error TEXT NULL,
  next_attempt_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_status_next_attempt (status, next_attempt_at),
  KEY idx_funnel_entry (funnel_entry_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

