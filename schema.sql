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
  profile_image_url VARCHAR(500) NULL,
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
  name VARCHAR(255) NOT NULL,
  location VARCHAR(255) NOT NULL,
  menu_url VARCHAR(500) NULL,
  images JSON NULL,
  business_type ENUM('bar','restaurant','cafe','hotel') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Business managers (many-to-many: multiple managers per business)
CREATE TABLE IF NOT EXISTS business_manager (
  business_id BIGINT UNSIGNED NOT NULL,
  manager_user_id BIGINT UNSIGNED NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (business_id, manager_user_id),
  CONSTRAINT fk_bm_business FOREIGN KEY (business_id) REFERENCES business(id) ON DELETE CASCADE,
  CONSTRAINT fk_bm_manager FOREIGN KEY (manager_user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_bm_manager (manager_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Roles (job postings)
CREATE TABLE IF NOT EXISTS role (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  business_id BIGINT UNSIGNED NOT NULL,
  position ENUM('waiter','bartender','barista','hostess','shift_manager') NOT NULL,
  payment_per_hour DECIMAL(10,2) NOT NULL,
  location VARCHAR(255) NOT NULL,
  latitude DOUBLE NULL,
  longitude DOUBLE NULL,
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

-- Swipes: user swipes a role with decision (like or pass)
CREATE TABLE IF NOT EXISTS role_swipe (
  role_id BIGINT UNSIGNED NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  decision ENUM('like','pass') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (role_id, user_id),
  CONSTRAINT fk_role_swipe_role FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE,
  CONSTRAINT fk_role_swipe_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_role_swipe_user (user_id)
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
  authorized_required TINYINT(1) NOT NULL DEFAULT 1,
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


-- Unswiped roles near a user's location (or all if distance is null/<=0)
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_unswiped_roles_nearby(
  IN p_user_id BIGINT,
  IN p_lat DOUBLE,
  IN p_lng DOUBLE,
  IN p_distance_km DOUBLE
)
BEGIN
  /*
    Returns up to 200 active roles that the user hasn't liked yet.
    If p_distance_km is NULL or <= 0, returns roles without distance filtering.
    Distance is computed using ST_Distance_Sphere on (lng, lat) in meters.
  */
  SELECT
    r.*,
    b.name AS business_name,
    CASE
      WHEN r.latitude IS NOT NULL AND r.longitude IS NOT NULL THEN ST_Distance_Sphere(POINT(p_lng, p_lat), POINT(r.longitude, r.latitude)) / 1000
      ELSE NULL
    END AS distance_km
  FROM role r
  JOIN business b ON b.id = r.business_id
  LEFT JOIN role_swipe rs ON rs.role_id = r.id AND rs.user_id = p_user_id
  WHERE r.is_active = 1
    AND rs.role_id IS NULL
    AND (
      p_distance_km IS NULL OR p_distance_km <= 0
      OR (
        r.latitude IS NOT NULL AND r.longitude IS NOT NULL
        AND ST_Distance_Sphere(POINT(p_lng, p_lat), POINT(r.longitude, r.latitude)) <= p_distance_km * 1000
      )
    )
  ORDER BY (distance_km IS NULL), distance_km ASC, r.created_at DESC
  LIMIT 200;
END$$
DELIMITER ;

-- ============== Dynamic CRUD Procedures ==============
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_user_get_by_email(IN p_email VARCHAR(255))
BEGIN
  SELECT id, email, password_hash, display_name, user_type, is_active
  FROM user_account
  WHERE email = p_email
  LIMIT 1;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_user_login(
  IN p_email VARCHAR(255),
  IN p_password VARCHAR(255)
)
BEGIN
  SELECT id, email, display_name, user_type, is_active
  FROM user_account
  WHERE email = p_email AND password_hash = SHA2(p_password, 256)
  LIMIT 1;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_waiter_get(IN p_user_id BIGINT)
BEGIN
  SELECT
    u.id AS user_id,
    u.display_name,
    u.email,
    wp.status,
    wp.about_me,
    wp.distance_km,
    wp.min_hourly_wage,
    wp.shifts_per_week,
    (SELECT JSON_ARRAYAGG(wh.hour_tag) FROM waiter_hours wh WHERE wh.user_id = p_user_id) AS hours,
    (SELECT JSON_ARRAYAGG(we.exp_tag) FROM waiter_experience we WHERE we.user_id = p_user_id) AS experience,
    (SELECT JSON_ARRAYAGG(wps.say_tag) FROM waiter_people_say wps WHERE wps.user_id = p_user_id) AS people_say,
    (SELECT JSON_ARRAYAGG(ws.skill_tag) FROM waiter_skills ws WHERE ws.user_id = p_user_id) AS skills,
    (SELECT JSON_ARRAYAGG(wl.looking_for) FROM waiter_looking_for wl WHERE wl.user_id = p_user_id) AS looking_for
  FROM user_account u
  LEFT JOIN waiter_profile wp ON wp.user_id = u.id
  WHERE u.id = p_user_id AND u.user_type = 'waiter'
  LIMIT 1;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_user_register_manager_basic(
  IN p_display_name VARCHAR(255),
  IN p_email VARCHAR(255),
  IN p_password VARCHAR(255)
)
BEGIN
  INSERT INTO user_account(email, password_hash, display_name, user_type)
  VALUES(p_email, SHA2(p_password, 256), p_display_name, 'business_manager');
  SELECT id, email, display_name, user_type, is_active FROM user_account WHERE email = p_email;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_waiter_register_full(
  IN p_display_name VARCHAR(255),
  IN p_email VARCHAR(255),
  IN p_password VARCHAR(255),
  IN p_status VARCHAR(32),
  IN p_about_me TEXT,
  IN p_distance_km INT,
  IN p_min_hourly_wage DECIMAL(10,2),
  IN p_shifts_per_week INT,
  IN p_hours JSON,
  IN p_experience JSON,
  IN p_people_say JSON,
  IN p_skills JSON,
  IN p_looking_for JSON
)
BEGIN
  DECLARE v_user_id BIGINT UNSIGNED;
  INSERT INTO user_account(email, password_hash, display_name, user_type)
  VALUES(p_email, SHA2(p_password, 256), p_display_name, 'waiter');
  SET v_user_id = LAST_INSERT_ID();

  INSERT INTO waiter_profile(user_id, status, about_me, distance_km, min_hourly_wage, shifts_per_week)
  VALUES(v_user_id, p_status, p_about_me, p_distance_km, p_min_hourly_wage, p_shifts_per_week);

  IF p_hours IS NOT NULL THEN
    INSERT INTO waiter_hours(user_id, hour_tag)
    SELECT v_user_id, jt.tag FROM JSON_TABLE(p_hours, '$[*]' COLUMNS(tag VARCHAR(32) PATH '$')) jt;
  END IF;
  IF p_experience IS NOT NULL THEN
    INSERT INTO waiter_experience(user_id, exp_tag)
    SELECT v_user_id, jt.tag FROM JSON_TABLE(p_experience, '$[*]' COLUMNS(tag VARCHAR(32) PATH '$')) jt;
  END IF;
  IF p_people_say IS NOT NULL THEN
    INSERT INTO waiter_people_say(user_id, say_tag)
    SELECT v_user_id, jt.tag FROM JSON_TABLE(p_people_say, '$[*]' COLUMNS(tag VARCHAR(64) PATH '$')) jt;
  END IF;
  IF p_skills IS NOT NULL THEN
    INSERT INTO waiter_skills(user_id, skill_tag)
    SELECT v_user_id, jt.tag FROM JSON_TABLE(p_skills, '$[*]' COLUMNS(tag VARCHAR(64) PATH '$')) jt;
  END IF;
  IF p_looking_for IS NOT NULL THEN
    INSERT INTO waiter_looking_for(user_id, looking_for)
    SELECT v_user_id, jt.tag FROM JSON_TABLE(p_looking_for, '$[*]' COLUMNS(tag VARCHAR(32) PATH '$')) jt;
  END IF;

  SELECT v_user_id AS user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_waiter_upsert_profile(
  IN p_user_id BIGINT,
  IN p_status VARCHAR(32),
  IN p_about_me TEXT,
  IN p_distance_km INT,
  IN p_min_hourly_wage DECIMAL(10,2),
  IN p_shifts_per_week INT,
  IN p_hours JSON,
  IN p_experience JSON,
  IN p_people_say JSON,
  IN p_skills JSON,
  IN p_looking_for JSON
)
BEGIN
  INSERT INTO waiter_profile(user_id, status, about_me, distance_km, min_hourly_wage, shifts_per_week)
  VALUES(p_user_id, IFNULL(p_status, 'other'), p_about_me, p_distance_km, p_min_hourly_wage, p_shifts_per_week)
  ON DUPLICATE KEY UPDATE
    status = IFNULL(p_status, status),
    about_me = IFNULL(p_about_me, about_me),
    distance_km = IFNULL(p_distance_km, distance_km),
    min_hourly_wage = IFNULL(p_min_hourly_wage, min_hourly_wage),
    shifts_per_week = IFNULL(p_shifts_per_week, shifts_per_week);

  IF p_hours IS NOT NULL THEN
    DELETE FROM waiter_hours WHERE user_id = p_user_id;
    INSERT INTO waiter_hours(user_id, hour_tag)
    SELECT p_user_id, jt.tag FROM JSON_TABLE(p_hours, '$[*]' COLUMNS(tag VARCHAR(32) PATH '$')) jt;
  END IF;
  IF p_experience IS NOT NULL THEN
    DELETE FROM waiter_experience WHERE user_id = p_user_id;
    INSERT INTO waiter_experience(user_id, exp_tag)
    SELECT p_user_id, jt.tag FROM JSON_TABLE(p_experience, '$[*]' COLUMNS(tag VARCHAR(32) PATH '$')) jt;
  END IF;
  IF p_people_say IS NOT NULL THEN
    DELETE FROM waiter_people_say WHERE user_id = p_user_id;
    INSERT INTO waiter_people_say(user_id, say_tag)
    SELECT p_user_id, jt.tag FROM JSON_TABLE(p_people_say, '$[*]' COLUMNS(tag VARCHAR(64) PATH '$')) jt;
  END IF;
  IF p_skills IS NOT NULL THEN
    DELETE FROM waiter_skills WHERE user_id = p_user_id;
    INSERT INTO waiter_skills(user_id, skill_tag)
    SELECT p_user_id, jt.tag FROM JSON_TABLE(p_skills, '$[*]' COLUMNS(tag VARCHAR(64) PATH '$')) jt;
  END IF;
  IF p_looking_for IS NOT NULL THEN
    DELETE FROM waiter_looking_for WHERE user_id = p_user_id;
    INSERT INTO waiter_looking_for(user_id, looking_for)
    SELECT p_user_id, jt.tag FROM JSON_TABLE(p_looking_for, '$[*]' COLUMNS(tag VARCHAR(32) PATH '$')) jt;
  END IF;

  SELECT p_user_id AS user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_business_create(
  IN p_name VARCHAR(255),
  IN p_location VARCHAR(255),
  IN p_business_type VARCHAR(32),
  IN p_menu_url VARCHAR(500),
  IN p_images JSON,
  IN p_manager_user_ids JSON,
  IN p_requester_id BIGINT
)
BEGIN
  DECLARE v_business_id BIGINT UNSIGNED;
  INSERT INTO business(name, location, business_type, menu_url, images)
  VALUES(p_name, p_location, p_business_type, p_menu_url, p_images);
  SET v_business_id = LAST_INSERT_ID();
  -- Always add the requester as a manager
  IF p_requester_id IS NOT NULL THEN
    INSERT IGNORE INTO business_manager(business_id, manager_user_id) VALUES(v_business_id, p_requester_id);
  END IF;
  IF p_manager_user_ids IS NOT NULL THEN
    INSERT INTO business_manager(business_id, manager_user_id)
    SELECT v_business_id, jt.manager_id
    FROM JSON_TABLE(p_manager_user_ids, '$[*]' COLUMNS(manager_id BIGINT PATH '$')) jt
    ON DUPLICATE KEY UPDATE manager_user_id = manager_user_id;
  END IF;
  SELECT v_business_id AS id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_business_list_by_manager(IN p_manager_user_id BIGINT)
BEGIN
  SELECT b.*
  FROM business b
  JOIN business_manager bm ON bm.business_id = b.id
  WHERE bm.manager_user_id = p_manager_user_id
  ORDER BY b.created_at DESC
  LIMIT 500;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_business_get(IN p_business_id BIGINT, IN p_manager_user_id BIGINT)
BEGIN
  SELECT b.*
  FROM business b
  JOIN business_manager bm ON bm.business_id = b.id
  WHERE b.id = p_business_id AND bm.manager_user_id = p_manager_user_id
  LIMIT 1;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_business_update(
  IN p_business_id BIGINT,
  IN p_manager_user_id BIGINT,
  IN p_updates JSON
)
BEGIN
  -- Only managers can update
  IF EXISTS(SELECT 1 FROM business_manager WHERE business_id = p_business_id AND manager_user_id = p_manager_user_id) THEN
    UPDATE business
    SET name = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(p_updates, '$.name')), name),
        location = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(p_updates, '$.location')), location),
        business_type = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(p_updates, '$.business_type')), business_type),
        menu_url = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(p_updates, '$.menu_url')), menu_url),
        images = COALESCE(JSON_EXTRACT(p_updates, '$.images'), images)
    WHERE id = p_business_id;
  END IF;
  SELECT * FROM business WHERE id = p_business_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_business_delete(IN p_business_id BIGINT, IN p_manager_user_id BIGINT)
BEGIN
  IF EXISTS(SELECT 1 FROM business_manager WHERE business_id = p_business_id AND manager_user_id = p_manager_user_id) THEN
    DELETE FROM business WHERE id = p_business_id;
  END IF;
  SELECT 1 AS ok;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_business_add_manager_by_email(IN p_business_id BIGINT, IN p_requester_id BIGINT, IN p_email VARCHAR(255))
BEGIN
  DECLARE v_user_id BIGINT;
  IF EXISTS(SELECT 1 FROM business_manager WHERE business_id = p_business_id AND manager_user_id = p_requester_id) THEN
    SELECT id INTO v_user_id FROM user_account WHERE email = p_email AND user_type = 'business_manager' LIMIT 1;
    IF v_user_id IS NOT NULL THEN
      INSERT IGNORE INTO business_manager(business_id, manager_user_id) VALUES(p_business_id, v_user_id);
    END IF;
  END IF;
  SELECT * FROM business WHERE id = p_business_id;
END$$
DELIMITER ;

-- Seed report configurations for CRUD
INSERT IGNORE INTO report_configuration (report_name, parameters, procedure_name, is_active, authorized_required)
VALUES
('user_get_by_email', JSON_ARRAY(JSON_OBJECT('parameter_name','p_email','is_mandatory',true,'default_value',NULL)), 'sp_user_get_by_email', 1, 0),
('user_login', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_email','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_password_hash','is_mandatory',true,'default_value',NULL)
), 'sp_user_login', 1, 0),
('user_register_manager_basic', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_display_name','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_email','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_password_hash','is_mandatory',true,'default_value',NULL)
), 'sp_user_register_manager_basic', 1, 0),
('waiter_register_full', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_display_name','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_email','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_password_hash','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_status','is_mandatory',true,'default_value','other'),
  JSON_OBJECT('parameter_name','p_about_me','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_distance_km','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_min_hourly_wage','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_shifts_per_week','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_hours','is_mandatory',false,'default_value',JSON_ARRAY()),
  JSON_OBJECT('parameter_name','p_experience','is_mandatory',false,'default_value',JSON_ARRAY()),
  JSON_OBJECT('parameter_name','p_people_say','is_mandatory',false,'default_value',JSON_ARRAY()),
  JSON_OBJECT('parameter_name','p_skills','is_mandatory',false,'default_value',JSON_ARRAY()),
  JSON_OBJECT('parameter_name','p_looking_for','is_mandatory',false,'default_value',JSON_ARRAY())
), 'sp_waiter_register_full', 1, 0),
('waiter_upsert_profile', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_user_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_status','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_about_me','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_distance_km','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_min_hourly_wage','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_shifts_per_week','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_hours','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_experience','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_people_say','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_skills','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_looking_for','is_mandatory',false,'default_value',NULL)
), 'sp_waiter_upsert_profile', 1, 1),
('waiter_get', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_waiter_get', 1, 1),
('business_create', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_name','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_location','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_business_type','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_menu_url','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_images','is_mandatory',false,'default_value',JSON_ARRAY()),
  JSON_OBJECT('parameter_name','p_manager_user_ids','is_mandatory',false,'default_value',JSON_ARRAY()),
  JSON_OBJECT('parameter_name','p_requester_id','is_mandatory',true,'default_value',NULL)
), 'sp_business_create', 1, 1),
('business_list_by_manager', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_manager_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_business_list_by_manager', 1, 1),
('business_get', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_business_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_manager_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_business_get', 1, 1),
('business_update', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_business_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_manager_user_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_updates','is_mandatory',true,'default_value',JSON_OBJECT())
), 'sp_business_update', 1, 1),
('business_delete', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_business_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_manager_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_business_delete', 1, 1),
('business_add_manager_by_email', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_business_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_requester_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_email','is_mandatory',true,'default_value',NULL)
), 'sp_business_add_manager_by_email', 1, 1);
-- Seed report configuration for unswiped roles nearby
INSERT IGNORE INTO report_configuration (report_name, parameters, procedure_name, is_active, authorized_required)
VALUES (
  'unswiped_roles_nearby',
  JSON_ARRAY(
    JSON_OBJECT('parameter_name','p_user_id','is_mandatory',true,'default_value',NULL),
    JSON_OBJECT('parameter_name','p_lat','is_mandatory',true,'default_value',NULL),
    JSON_OBJECT('parameter_name','p_lng','is_mandatory',true,'default_value',NULL),
    JSON_OBJECT('parameter_name','p_distance_km','is_mandatory',false,'default_value',NULL)
  ),
  'sp_unswiped_roles_nearby',
  1,
  1
);

-- ================= Roles (reports) =================
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_role_create(
  IN p_business_id BIGINT,
  IN p_position VARCHAR(32),
  IN p_payment_per_hour DECIMAL(10,2),
  IN p_location VARCHAR(255),
  IN p_latitude DOUBLE,
  IN p_longitude DOUBLE,
  IN p_when_need VARCHAR(32),
  IN p_experience_required VARCHAR(32),
  IN p_shift_morning TINYINT,
  IN p_shift_evening TINYINT,
  IN p_shift_weekends TINYINT,
  IN p_shift_full_time TINYINT,
  IN p_shift_part_time TINYINT,
  IN p_about_job TEXT,
  IN p_min_hourly_wage DECIMAL(10,2),
  IN p_is_active TINYINT,
  IN p_manager_user_id BIGINT
)
BEGIN
  IF NOT EXISTS(SELECT 1 FROM business_manager WHERE business_id = p_business_id AND manager_user_id = p_manager_user_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Not your business';
  END IF;
  INSERT INTO role(
    business_id, position, payment_per_hour, location, latitude, longitude,
    when_need, experience_required, shift_morning, shift_evening, shift_weekends,
    shift_full_time, shift_part_time, about_job, min_hourly_wage, is_active
  ) VALUES (
    p_business_id, p_position, p_payment_per_hour, p_location, p_latitude, p_longitude,
    p_when_need, p_experience_required, p_shift_morning, p_shift_evening, p_shift_weekends,
    p_shift_full_time, p_shift_part_time, p_about_job, p_min_hourly_wage, IFNULL(p_is_active,1)
  );
  SELECT LAST_INSERT_ID() AS id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_role_get(IN p_role_id BIGINT)
BEGIN
  SELECT * FROM role WHERE id = p_role_id LIMIT 1;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_role_update(
  IN p_role_id BIGINT,
  IN p_manager_user_id BIGINT,
  IN p_updates JSON
)
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM role r JOIN business_manager bm ON bm.business_id = r.business_id
    WHERE r.id = p_role_id AND bm.manager_user_id = p_manager_user_id
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Not your business';
  END IF;
  UPDATE role r
  JOIN business b ON b.id = r.business_id
  SET r.position = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(p_updates,'$.position')), r.position),
      r.payment_per_hour = COALESCE(JSON_EXTRACT(p_updates,'$.payment_per_hour'), r.payment_per_hour),
      r.location = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(p_updates,'$.location')), r.location),
      r.latitude = COALESCE(JSON_EXTRACT(p_updates,'$.latitude'), r.latitude),
      r.longitude = COALESCE(JSON_EXTRACT(p_updates,'$.longitude'), r.longitude),
      r.when_need = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(p_updates,'$.when_need')), r.when_need),
      r.experience_required = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(p_updates,'$.experience_required')), r.experience_required),
      r.shift_morning = COALESCE(JSON_EXTRACT(p_updates,'$.shift_morning'), r.shift_morning),
      r.shift_evening = COALESCE(JSON_EXTRACT(p_updates,'$.shift_evening'), r.shift_evening),
      r.shift_weekends = COALESCE(JSON_EXTRACT(p_updates,'$.shift_weekends'), r.shift_weekends),
      r.shift_full_time = COALESCE(JSON_EXTRACT(p_updates,'$.shift_full_time'), r.shift_full_time),
      r.shift_part_time = COALESCE(JSON_EXTRACT(p_updates,'$.shift_part_time'), r.shift_part_time),
      r.about_job = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(p_updates,'$.about_job')), r.about_job),
      r.min_hourly_wage = COALESCE(JSON_EXTRACT(p_updates,'$.min_hourly_wage'), r.min_hourly_wage),
      r.is_active = COALESCE(JSON_EXTRACT(p_updates,'$.is_active'), r.is_active)
  WHERE r.id = p_role_id;
  SELECT * FROM role WHERE id = p_role_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_role_delete(IN p_role_id BIGINT, IN p_manager_user_id BIGINT)
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM role r JOIN business_manager bm ON bm.business_id = r.business_id
    WHERE r.id = p_role_id AND bm.manager_user_id = p_manager_user_id
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Not your business';
  END IF;
  DELETE FROM role WHERE id = p_role_id;
  SELECT 1 AS ok;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_role_like(IN p_role_id BIGINT, IN p_user_id BIGINT)
BEGIN
  INSERT IGNORE INTO role_like(role_id, user_id) VALUES(p_role_id, p_user_id);
  SELECT 1 AS liked;
END$$
DELIMITER ;

INSERT IGNORE INTO report_configuration (report_name, parameters, procedure_name, is_active, authorized_required) VALUES
('role_create', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_business_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_position','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_payment_per_hour','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_location','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_latitude','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_longitude','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_when_need','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_experience_required','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_shift_morning','is_mandatory',false,'default_value',0),
  JSON_OBJECT('parameter_name','p_shift_evening','is_mandatory',false,'default_value',0),
  JSON_OBJECT('parameter_name','p_shift_weekends','is_mandatory',false,'default_value',0),
  JSON_OBJECT('parameter_name','p_shift_full_time','is_mandatory',false,'default_value',0),
  JSON_OBJECT('parameter_name','p_shift_part_time','is_mandatory',false,'default_value',0),
  JSON_OBJECT('parameter_name','p_about_job','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_min_hourly_wage','is_mandatory',false,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_is_active','is_mandatory',false,'default_value',1),
  JSON_OBJECT('parameter_name','p_manager_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_role_create', 1, 1),
('role_get', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_role_id','is_mandatory',true,'default_value',NULL)
), 'sp_role_get', 1, 0),
('role_update', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_role_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_manager_user_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_updates','is_mandatory',true,'default_value',JSON_OBJECT())
), 'sp_role_update', 1, 1),
('role_delete', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_role_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_manager_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_role_delete', 1, 1),
('role_like', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_role_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_role_like', 1, 1);

-- ================= Notifications (reports) =================
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_notifications_list(IN p_user_id BIGINT)
BEGIN
  SELECT * FROM notification WHERE user_id = p_user_id ORDER BY created_at DESC LIMIT 500;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_notifications_create(IN p_user_id BIGINT, IN p_type VARCHAR(64), IN p_payload JSON)
BEGIN
  INSERT INTO notification(user_id, type, payload) VALUES(p_user_id, p_type, p_payload);
  SELECT LAST_INSERT_ID() AS id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_notification_mark_read(IN p_notification_id BIGINT, IN p_user_id BIGINT)
BEGIN
  UPDATE notification SET read_at = NOW() WHERE id = p_notification_id AND user_id = p_user_id;
  SELECT 1 AS ok;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_notification_delete(IN p_notification_id BIGINT, IN p_user_id BIGINT)
BEGIN
  DELETE FROM notification WHERE id = p_notification_id AND user_id = p_user_id;
  SELECT 1 AS ok;
END$$
DELIMITER ;

INSERT IGNORE INTO report_configuration (report_name, parameters, procedure_name, is_active, authorized_required) VALUES
('notifications_list', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_notifications_list', 1, 1),
('notifications_create', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_user_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_type','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_payload','is_mandatory',false,'default_value',NULL)
), 'sp_notifications_create', 1, 1),
('notification_mark_read', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_notification_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_notification_mark_read', 1, 1),
('notification_delete', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_notification_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_notification_delete', 1, 1);

-- ================= Chat (reports) =================
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_chat_create_conversation(IN p_initiator_user_id BIGINT, IN p_participant_user_ids JSON)
BEGIN
  DECLARE v_conversation_id BIGINT UNSIGNED;
  INSERT INTO conversation() VALUES();
  SET v_conversation_id = LAST_INSERT_ID();
  INSERT IGNORE INTO conversation_participant(conversation_id, user_id)
  VALUES(v_conversation_id, p_initiator_user_id);
  IF p_participant_user_ids IS NOT NULL THEN
    INSERT IGNORE INTO conversation_participant(conversation_id, user_id)
    SELECT v_conversation_id, jt.user_id
    FROM JSON_TABLE(p_participant_user_ids, '$[*]' COLUMNS(user_id BIGINT PATH '$')) jt;
  END IF;
  SELECT v_conversation_id AS id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_chat_list_conversations(IN p_user_id BIGINT)
BEGIN
  SELECT c.* FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  WHERE cp.user_id = p_user_id
  ORDER BY c.created_at DESC LIMIT 500;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_chat_post_message(IN p_conversation_id BIGINT, IN p_sender_user_id BIGINT, IN p_body TEXT)
BEGIN
  IF NOT EXISTS (SELECT 1 FROM conversation_participant WHERE conversation_id = p_conversation_id AND user_id = p_sender_user_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Not a participant';
  END IF;
  INSERT INTO message(conversation_id, sender_user_id, body) VALUES(p_conversation_id, p_sender_user_id, p_body);
  SELECT LAST_INSERT_ID() AS id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_chat_list_messages(IN p_conversation_id BIGINT, IN p_user_id BIGINT)
BEGIN
  IF NOT EXISTS (SELECT 1 FROM conversation_participant WHERE conversation_id = p_conversation_id AND user_id = p_user_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Not a participant';
  END IF;
  SELECT * FROM message WHERE conversation_id = p_conversation_id ORDER BY created_at ASC LIMIT 1000;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS sp_chat_mark_message_read(IN p_message_id BIGINT, IN p_user_id BIGINT)
BEGIN
  UPDATE message SET read_at = NOW() WHERE id = p_message_id AND EXISTS (
    SELECT 1 FROM conversation_participant cp JOIN message m ON m.conversation_id = cp.conversation_id
    WHERE m.id = p_message_id AND cp.user_id = p_user_id
  );
  SELECT 1 AS ok;
END$$
DELIMITER ;

INSERT IGNORE INTO report_configuration (report_name, parameters, procedure_name, is_active, authorized_required) VALUES
('chat_create_conversation', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_initiator_user_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_participant_user_ids','is_mandatory',false,'default_value',JSON_ARRAY())
), 'sp_chat_create_conversation', 1, 1),
('chat_list_conversations', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_chat_list_conversations', 1, 1),
('chat_post_message', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_conversation_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_sender_user_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_body','is_mandatory',true,'default_value',NULL)
), 'sp_chat_post_message', 1, 1),
('chat_list_messages', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_conversation_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_chat_list_messages', 1, 1),
('chat_mark_message_read', JSON_ARRAY(
  JSON_OBJECT('parameter_name','p_message_id','is_mandatory',true,'default_value',NULL),
  JSON_OBJECT('parameter_name','p_user_id','is_mandatory',true,'default_value',NULL)
), 'sp_chat_mark_message_read', 1, 1);

