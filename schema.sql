-- WaiterJobs schema (MySQL 8)
-- One-time SQL to create database, tables, indexes, and an example stored procedure

-- Database and charset
CREATE DATABASE IF NOT EXISTS waiter_jobs DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE waiter_jobs;

-- Users (base auth)
CREATE TABLE IF NOT EXISTS user_account (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  display_name VARCHAR(255) NOT NULL,
  user_type ENUM('waiter','business_manager') NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Token table (checked via Depends on each request)
CREATE TABLE IF NOT EXISTS token_table (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  token VARCHAR(512) NOT NULL,
  modification_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_token_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_token_user (user_id),
  KEY idx_token (token(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Waiter profile
CREATE TABLE IF NOT EXISTS waiter_profile (
  user_id BIGINT UNSIGNED PRIMARY KEY,
  status ENUM('pre_army','post_army','student','other') NOT NULL,
  about_me TEXT NULL,
  distance_km INT NULL,
  min_hourly_wage DECIMAL(10,2) NULL,
  shifts_per_week INT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_waiter_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Multi-selects for waiter
CREATE TABLE IF NOT EXISTS waiter_hours (
  user_id BIGINT UNSIGNED NOT NULL,
  hour_tag ENUM('part_time','full_time','morning','evening','weekends') NOT NULL,
  PRIMARY KEY (user_id, hour_tag),
  CONSTRAINT fk_waiter_hours_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS waiter_experience (
  user_id BIGINT UNSIGNED NOT NULL,
  exp_tag ENUM('waiter','barman','barista','shift_manager','host') NOT NULL,
  PRIMARY KEY (user_id, exp_tag),
  CONSTRAINT fk_waiter_exp_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS waiter_people_say (
  user_id BIGINT UNSIGNED NOT NULL,
  say_tag ENUM('best_coffee_maker','good_vibe','best_cocktails','customers_love_me') NOT NULL,
  PRIMARY KEY (user_id, say_tag),
  CONSTRAINT fk_waiter_say_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS waiter_skills (
  user_id BIGINT UNSIGNED NOT NULL,
  skill_tag ENUM('customer_service','basic_computer','coffee_making','teamwork','food_service','working_under_pressure','table_management') NOT NULL,
  PRIMARY KEY (user_id, skill_tag),
  CONSTRAINT fk_waiter_skill_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Looking-for (multi-select)
CREATE TABLE IF NOT EXISTS waiter_looking_for (
  user_id BIGINT UNSIGNED NOT NULL,
  looking_for ENUM('waiter','bartender','barista','hostess','shift_manager','manager') NOT NULL,
  PRIMARY KEY (user_id, looking_for),
  CONSTRAINT fk_waiter_looking_for_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Businesses
CREATE TABLE IF NOT EXISTS business (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  manager_user_id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(255) NOT NULL,
  location VARCHAR(255) NOT NULL,
  menu_url VARCHAR(500) NULL,
  business_type ENUM('bar','restaurant','cafe','hotel') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_business_manager FOREIGN KEY (manager_user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Roles (job postings)
CREATE TABLE IF NOT EXISTS role (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  business_id BIGINT UNSIGNED NOT NULL,
  position ENUM('waiter','bartender','barista','hostess','shift_manager') NOT NULL,
  payment_per_hour DECIMAL(10,2) NOT NULL,
  location VARCHAR(255) NOT NULL,
  when_need ENUM('this_week','always_looking') NOT NULL,
  experience_required ENUM('no_experience','some_experience','experience_only') NOT NULL,
  shift_morning TINYINT(1) NOT NULL DEFAULT 0,
  shift_evening TINYINT(1) NOT NULL DEFAULT 0,
  shift_weekends TINYINT(1) NOT NULL DEFAULT 0,
  shift_full_time TINYINT(1) NOT NULL DEFAULT 0,
  shift_part_time TINYINT(1) NOT NULL DEFAULT 0,
  about_job TEXT NULL,
  min_hourly_wage DECIMAL(10,2) NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_role_business FOREIGN KEY (business_id) REFERENCES business(id) ON DELETE CASCADE,
  KEY idx_role_active (is_active, position)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Likes: user likes a role
CREATE TABLE IF NOT EXISTS role_like (
  role_id BIGINT UNSIGNED NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (role_id, user_id),
  CONSTRAINT fk_role_like_role FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE,
  CONSTRAINT fk_role_like_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_role_like_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Likes: manager likes waiter
CREATE TABLE IF NOT EXISTS manager_like_waiter (
  manager_user_id BIGINT UNSIGNED NOT NULL,
  waiter_user_id BIGINT UNSIGNED NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (manager_user_id, waiter_user_id),
  CONSTRAINT fk_ml_manager FOREIGN KEY (manager_user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  CONSTRAINT fk_ml_waiter FOREIGN KEY (waiter_user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_ml_waiter (waiter_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notifications
CREATE TABLE IF NOT EXISTS notification (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  type ENUM(
    'upcoming_interview',
    'new_match',
    'business_liked_you',
    'interview_succeeded',
    'arriving_for_shift',
    'new_message'
  ) NOT NULL,
  payload JSON NULL,
  scheduled_at DATETIME NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  read_at DATETIME NULL,
  CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_notification_user (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reports config
CREATE TABLE IF NOT EXISTS report_configuration (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  report_name VARCHAR(255) NOT NULL UNIQUE,
  parameters JSON NOT NULL, -- [{ "parameter_name": "...", "is_mandatory": true/false, "default_value": ... }]
  procedure_name VARCHAR(255) NOT NULL, -- e.g., "sp_roles_by_position"
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  modification_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- In-app Messaging (Conversations & Messages)
CREATE TABLE IF NOT EXISTS conversation (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS conversation_participant (
  conversation_id BIGINT UNSIGNED NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (conversation_id, user_id),
  CONSTRAINT fk_conv_participant_conv FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE,
  CONSTRAINT fk_conv_participant_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_conv_part_user (user_id, conversation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS message (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  conversation_id BIGINT UNSIGNED NOT NULL,
  sender_user_id BIGINT UNSIGNED NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  read_at DATETIME NULL,
  CONSTRAINT fk_msg_conv FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE,
  CONSTRAINT fk_msg_sender FOREIGN KEY (sender_user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_msg_conv_created (conversation_id, created_at),
  KEY idx_msg_unread (conversation_id, read_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Example stored procedure (report)
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_roles_by_position(IN p_position VARCHAR(32))
BEGIN
  SELECT r.*, b.name AS business_name
  FROM role r
  JOIN business b ON b.id = r.business_id
  WHERE r.position = p_position AND r.is_active = 1
  ORDER BY r.created_at DESC
  LIMIT 200;
END$$
DELIMITER ;


