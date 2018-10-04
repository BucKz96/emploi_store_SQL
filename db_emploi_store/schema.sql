-- MySQL dump 10.13  Distrib 8.0.12, for macos10.13 (x86_64)
--
-- Host: localhost    Database: emploi_store
-- ------------------------------------------------------
-- Server version	5.7.23

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8mb4 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `o_geoloc`
--

DROP TABLE IF EXISTS `o_geoloc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `o_geoloc` (
  `g_o_id` varchar(45) NOT NULL,
  `g_gps_latitude` float(10,6) DEFAULT NULL,
  `g_gps_longitude` float(10,6) DEFAULT NULL,
  PRIMARY KEY (`g_o_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `o_salary`
--

DROP TABLE IF EXISTS `o_salary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `o_salary` (
  `slry_o_id` varchar(45) NOT NULL,
  `slry_min_salary` int(11) DEFAULT NULL,
  `slry_max_salary` int(11) DEFAULT NULL,
  PRIMARY KEY (`slry_o_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `o_skills`
--

DROP TABLE IF EXISTS `o_skills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `o_skills` (
  `s_id` int(11) NOT NULL AUTO_INCREMENT,
  `s_skill_name` varchar(255) DEFAULT NULL,
  `o_id` varchar(45) NOT NULL,
  PRIMARY KEY (`s_id`),
  KEY `o_id` (`o_id`),
  CONSTRAINT `o_skills_ibfk_1` FOREIGN KEY (`o_id`) REFERENCES `offer` (`o_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8262 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `offer`
--

DROP TABLE IF EXISTS `offer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `offer` (
  `o_id` varchar(45) NOT NULL,
  `o_search_keyword` varchar(100) NOT NULL,
  `o_title` varchar(100) NOT NULL,
  `o_department_code` int(11) DEFAULT NULL,
  `o_city_code` int(11) DEFAULT NULL,
  `o_city` varchar(100) DEFAULT NULL,
  `o_company_name` varchar(100) DEFAULT NULL,
  `o_description` text,
  `o_contract` varchar(45) DEFAULT NULL,
  `o_contact_mail` varchar(255) DEFAULT NULL,
  `g_o_id` varchar(45) DEFAULT NULL,
  `slry_o_id` varchar(45) DEFAULT NULL,
  `o_added_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `o_updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`o_id`),
  KEY `g_o_id` (`g_o_id`),
  KEY `slry_o_id` (`slry_o_id`),
  CONSTRAINT `offer_ibfk_1` FOREIGN KEY (`g_o_id`) REFERENCES `o_geoloc` (`g_o_id`),
  CONSTRAINT `offer_ibfk_2` FOREIGN KEY (`slry_o_id`) REFERENCES `o_salary` (`slry_o_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-10-04  0:56:23
