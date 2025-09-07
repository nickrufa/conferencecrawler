-- MySQL dump 10.13  Distrib 8.0.34, for macos13 (arm64)
--
-- Host: localhost    Database: conference_crawler
-- ------------------------------------------------------
-- Server version	8.0.43-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ECCMID_2025`
--

DROP TABLE IF EXISTS `ECCMID_2025`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ECCMID_2025` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sessionLocalStart` varchar(45) DEFAULT NULL,
  `sessionLocalEnd` varchar(45) DEFAULT NULL,
  `sessionType` varchar(255) DEFAULT NULL,
  `sessionId` varchar(25) DEFAULT NULL,
  `sessionLabel` varchar(255) DEFAULT NULL,
  `sessionData` longtext,
  `dc` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_sessionId` (`sessionId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ECCMID_2025`
--

LOCK TABLES `ECCMID_2025` WRITE;
/*!40000 ALTER TABLE `ECCMID_2025` DISABLE KEYS */;
/*!40000 ALTER TABLE `ECCMID_2025` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ECCMID_2025_Sessions`
--

DROP TABLE IF EXISTS `ECCMID_2025_Sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ECCMID_2025_Sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sessionId` varchar(25) NOT NULL,
  `parentSessionId` int DEFAULT NULL,
  `title` text NOT NULL,
  `location` varchar(100) DEFAULT NULL,
  `sessionDate` varchar(50) DEFAULT NULL,
  `timeRange` varchar(50) DEFAULT NULL,
  `timezone` varchar(10) DEFAULT NULL,
  `sessionType` varchar(100) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `chairName` varchar(100) DEFAULT NULL,
  `chairCountry` varchar(50) DEFAULT NULL,
  `presenterName` varchar(100) DEFAULT NULL,
  `presenterCountry` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_sessionId` (`sessionId`),
  KEY `fk_parentSessionId` (`parentSessionId`),
  CONSTRAINT `fk_parentSessionId` FOREIGN KEY (`parentSessionId`) REFERENCES `ECCMID_2025_Sessions` (`id`),
  CONSTRAINT `fk_sessionId` FOREIGN KEY (`sessionId`) REFERENCES `ECCMID_2025` (`sessionId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ECCMID_2025_Sessions`
--

LOCK TABLES `ECCMID_2025_Sessions` WRITE;
/*!40000 ALTER TABLE `ECCMID_2025_Sessions` DISABLE KEYS */;
/*!40000 ALTER TABLE `ECCMID_2025_Sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `IDWEEK_2025`
--

DROP TABLE IF EXISTS `IDWEEK_2025`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `IDWEEK_2025` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sessionLocalStart` varchar(45) DEFAULT NULL,
  `sessionLocalEnd` varchar(45) DEFAULT NULL,
  `sessionType` varchar(255) DEFAULT NULL,
  `sessionId` varchar(25) DEFAULT NULL,
  `sessionLabel` varchar(255) DEFAULT NULL,
  `sessionData` longtext,
  `parsedSessionData` longtext,
  `dc` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `location` varchar(255) DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL,
  `name` text,
  `chair` text,
  `faculty` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `IDWEEK_2025`
--

LOCK TABLES `IDWEEK_2025` WRITE;
/*!40000 ALTER TABLE `IDWEEK_2025` DISABLE KEYS */;
/*!40000 ALTER TABLE `IDWEEK_2025` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `IDWEEK_Faculty_2025`
--

DROP TABLE IF EXISTS `IDWEEK_Faculty_2025`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `IDWEEK_Faculty_2025` (
  `id` int NOT NULL AUTO_INCREMENT,
  `presenterid` varchar(25) DEFAULT NULL,
  `rnd` float DEFAULT NULL,
  `raw_data` longtext,
  `parsedPosterData` longtext,
  `dc` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `IDWEEK_Faculty_2025`
--

LOCK TABLES `IDWEEK_Faculty_2025` WRITE;
/*!40000 ALTER TABLE `IDWEEK_Faculty_2025` DISABLE KEYS */;
/*!40000 ALTER TABLE `IDWEEK_Faculty_2025` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `IDWEEK_Posters_2025`
--

DROP TABLE IF EXISTS `IDWEEK_Posters_2025`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `IDWEEK_Posters_2025` (
  `id` int NOT NULL AUTO_INCREMENT,
  `poster_topic` varchar(255) DEFAULT NULL,
  `poster_id` int DEFAULT NULL,
  `poster_number` varchar(25) DEFAULT NULL,
  `session_title` varchar(255) DEFAULT NULL,
  `location` varchar(1) DEFAULT NULL,
  `row` int DEFAULT '0',
  `position` int DEFAULT '0',
  `abstract_number` varchar(25) DEFAULT NULL,
  `abstract_title` varchar(255) DEFAULT NULL,
  `session_date` date DEFAULT NULL,
  `session_number` varchar(5) DEFAULT NULL,
  `poster_presenters` longtext,
  `rawPosterData` longtext,
  `cleanPosterData` longtext,
  `dc` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `starttime` varchar(45) DEFAULT NULL,
  `endtime` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `IDWEEK_Posters_2025`
--

LOCK TABLES `IDWEEK_Posters_2025` WRITE;
/*!40000 ALTER TABLE `IDWEEK_Posters_2025` DISABLE KEYS */;
/*!40000 ALTER TABLE `IDWEEK_Posters_2025` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-05  8:05:40
