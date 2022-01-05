-- MySQL dump 10.13  Distrib 8.0.27, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: amazon_data
-- ------------------------------------------------------
-- Server version	8.0.27-0ubuntu0.20.04.1

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
-- Table structure for table `product_keywords`
--

DROP TABLE IF EXISTS `product_keywords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_keywords` (
  `KWYWORD` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `no_products` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_keywords`
--

LOCK TABLES `product_keywords` WRITE;
/*!40000 ALTER TABLE `product_keywords` DISABLE KEYS */;
INSERT INTO `product_keywords` VALUES ('best grease for rc cars',3),('Which automotive grease to use on RC cars',4),('best grease gun coupler',5),('best foam gun without pressure washer',6),('best smelling 2 stroke oil',7),('best sawzall blade for cutting tires',8),('best tool for cutting up tires',9),('best way to cut steel belted tires',10),('best antifreeze tester',11),('best wheel bearing removal tool',12),('best wheel bearing packer',13),('Best bearing packer tool',14),('Best Liquid Electrical Tape',15),('best aftermarket cv axles',16),('best anti seize lubricant',17),('how many cubic yards in a dump truck',18),('best automotive oscilloscopes',19),('best headers for 5.3 silverado',20),('best long tube headers for 5.3 silverado',21),('best oil for 3.5 ecoboost',22),('best leaf springs',23),('best jack stand for bmw',24),('How to Start a Car with a Bad Crankshaft Sensor',25),('best fluid transfer pump',26),('best handheld oil diffuser',27),('best portable fuel caddy',28),('best head studs for 6.0 powerstroke',29),('best long tube headers for 5.3 silverado',30),('best muffler delete for ram 1500',31),('best sounding exhaust for ram 5.7 hemi',32),('Best Water Pump for 7.3 Powerstroke',33),('Best Water Pump For 6.0 PowerStroke',34),('Best SBC Water Pump',35),('best engine support bar',36),('Best LS Oil Pump',37),('best coolant for bmw',38),('best racing oil',39),('best oil filter bob is the oil guy',40),('best noack oil',41),('best oil to use for undercoating',42),('best engine block heater for diesel trucks',43),('New KW',44),('best tire dressing applicator',45),('best way to wash a car without scratching',46),('best way to organize sockets',47),('best pdr tools',48),('best auto trim removal tools',49),('best pdr glue sticks',50),('best fabric protector for car seats',51),('best iron fallout remover',52),('best price autoglym products',53),('best interior protectant for bmw',54),('best interior protectant',55),('best exhaust gasket',56),('best steering shaft',57),('best grease for steering rack',58),('Best Topside Creepers',59),('bmw coolant alternative',60),('Best Coolant Temperature Sensors',61),('best coolant expansion tank',62),('Best Coolant Level Sensors',63),('best coolant expansion tank bmw',64),('best coolant hose',65),('best radiator hose',66),('best universal radiator hose',67),('Best Aluminum Radiator',68),('best Coolant Tank Bleeder Screw',69),('Expansion Tank Bleeder Screw',70),('Best Coolant Air Bleeder Screw Parts for Cars, Trucks & SUVs',71),('best Cooling System Leak Checker',72),('best Coolant System Refiller Kit',73),('best coolant funnel kit',74),('Spill Proof Radiator Coolant Filling Funnel Kit',75),('best Coolant Reservoir for bmw',76),('best engine block heater',77),('best spark plugs for toyota tacoma',78),('best oil for 6.7 powerstroke',79),('Best LS Oil Pump',80),('Best Oil Pump',81),('krylon vs rustoleum',82),('truxedo truxport review',83),('retrax bed cover reviews',84);
/*!40000 ALTER TABLE `product_keywords` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-01-01 22:03:38
