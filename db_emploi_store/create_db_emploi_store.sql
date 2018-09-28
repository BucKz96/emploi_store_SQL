-- ****************** SqlDBM: MySQL ******************;
-- ***************************************************;

-- ************************************** `o_salary`

CREATE TABLE `o_salary`
(
 `slry_id`         INT NOT NULL AUTO_INCREMENT ,
 `slry_min_salary` INT ,
 `slry_max_salary` INT ,

PRIMARY KEY (`slry_id`)
) ENGINE=INNODB COLLATE=utf8mb4_general_ci;

-- ************************************** `o_geoloc`

CREATE TABLE `o_geoloc`
(
 `g_id`            INT NOT NULL AUTO_INCREMENT ,
 `g_gps_latitude`  FLOAT(10,6) ,
 `g_gps_longitude` FLOAT(10,6) ,

PRIMARY KEY (`g_id`)
) ENGINE=INNODB COLLATE=utf8mb4_general_ci;

-- ************************************** `offer`

CREATE TABLE `offer`
(
 `o_id`              VARCHAR(45) NOT NULL ,
 `o_title`           VARCHAR(100) NOT NULL ,
 `o_city_code`       INT ,
 `o_city`            VARCHAR(100) ,
 `o_company_name`    VARCHAR(100) ,
 `o_description`     TEXT ,
 `o_contract`        VARCHAR(45) ,
 `o_contact_mail`    VARCHAR(255) ,
 `o_update_datetime` DATETIME NOT NULL ,
 `o_fk_salary_id`    INT NOT NULL ,
 `o_fk_geoloc_id`    INT NOT NULL ,

PRIMARY KEY (`o_id`),
KEY `fkIdx_62` (`o_fk_salary_id`),
CONSTRAINT `FK_62` FOREIGN KEY `fkIdx_62` (`o_fk_salary_id`) REFERENCES `o_salary` (`slry_id`),
KEY `fkIdx_68` (`o_fk_geoloc_id`),
CONSTRAINT `FK_68` FOREIGN KEY `fkIdx_68` (`o_fk_geoloc_id`) REFERENCES `o_geoloc` (`g_id`)
) ENGINE=INNODB COLLATE=utf8mb4_general_ci;

-- ************************************** `o_skills`

CREATE TABLE `o_skills`
(
 `s_id`          INT NOT NULL AUTO_INCREMENT ,
 `s_skill_name`  VARCHAR(100) UNIQUE NULL,
 `s_fk_offer_id` VARCHAR(45) NOT NULL ,

PRIMARY KEY (`s_id`),
KEY `fkIdx_59` (`s_fk_offer_id`),
CONSTRAINT `FK_59` FOREIGN KEY `fkIdx_59` (`s_fk_offer_id`) REFERENCES `offer` (`o_id`)
) ENGINE=INNODB COLLATE=utf8mb4_general_ci;
