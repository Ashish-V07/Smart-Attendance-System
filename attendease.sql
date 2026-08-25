-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: attendease
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `attendance_id` int NOT NULL AUTO_INCREMENT,
  `class_id` int NOT NULL,
  `student_id` int NOT NULL,
  `attendance_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(10) NOT NULL,
  `confidence_score` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`attendance_id`),
  UNIQUE KEY `unique_class_student` (`class_id`,`student_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `classes` (`class_id`),
  CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (20,8,3,'2026-08-04 18:51:36','Present',70.49),(23,10,3,'2026-08-09 16:08:01','Absent',0.00);
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classes`
--

DROP TABLE IF EXISTS `classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classes` (
  `class_id` int NOT NULL AUTO_INCREMENT,
  `subject_id` int NOT NULL,
  `faculty_id` int NOT NULL,
  `class_date` date NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `attendance_started` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`class_id`),
  KEY `subject_id` (`subject_id`),
  KEY `faculty_id` (`faculty_id`),
  CONSTRAINT `classes_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`subject_id`),
  CONSTRAINT `classes_ibfk_2` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`faculty_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classes`
--

LOCK TABLES `classes` WRITE;
/*!40000 ALTER TABLE `classes` DISABLE KEYS */;
INSERT INTO `classes` VALUES (8,1,2,'2026-08-04','17:28:00','19:00:00',0),(9,3,4,'2026-08-04','17:07:00','18:05:00',0),(10,1,2,'2026-08-09','15:51:00','16:08:00',0);
/*!40000 ALTER TABLE `classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `course_id` int NOT NULL AUTO_INCREMENT,
  `course_name` varchar(100) NOT NULL,
  `course_code` varchar(20) NOT NULL,
  PRIMARY KEY (`course_id`),
  UNIQUE KEY `course_code` (`course_code`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (1,'BCA','BCA012'),(2,'BSC_IT','BSC_IT011'),(3,'BBA','BBA013'),(4,'BA','BA014'),(5,'B.Com','B.Com015'),(6,'MCA','MCA016'),(7,'MSC_IT','MSC_IT017'),(8,'MBA','MBA018'),(9,'MA','MA019'),(10,'M.Com','M.Com020');
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `face_data`
--

DROP TABLE IF EXISTS `face_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `face_data` (
  `face_id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `image_path` varchar(255) NOT NULL,
  `face_encoding` mediumtext,
  PRIMARY KEY (`face_id`),
  UNIQUE KEY `student_id` (`student_id`),
  CONSTRAINT `face_data_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `face_data`
--

LOCK TABLES `face_data` WRITE;
/*!40000 ALTER TABLE `face_data` DISABLE KEYS */;
INSERT INTO `face_data` VALUES (11,1,'/static/faces/student_1.jpg','[-0.24995094537734985, 0.11145520955324173, 0.11807036399841309, -0.018247416242957115, 0.05040901154279709, -0.1030619889497757, 0.04021092504262924, -0.10725060105323792, 0.1489226520061493, 0.007575003895908594, 0.20624147355556488, -0.03402160480618477, -0.14878714084625244, -0.16193723678588867, 0.027358856052160263, 0.09762800484895706, -0.10134612768888474, -0.13854435086250305, -0.0983135923743248, -0.03696395084261894, 0.05469894036650658, -0.03054971620440483, 0.043543703854084015, 0.14781823754310608, -0.15974989533424377, -0.3593018054962158, -0.08105285465717316, -0.13112077116966248, -0.08333426713943481, -0.09398980438709259, -0.04621107876300812, 0.026573946699500084, -0.20103755593299866, -0.08377058804035187, -0.06443321704864502, 0.11786023527383804, 0.04659639298915863, -0.028094984591007233, 0.14934101700782776, -0.06046310067176819, -0.18015021085739136, -0.042265888303518295, 0.10513272881507874, 0.2652166783809662, 0.1833435595035553, -0.03939065337181091, 0.004933452233672142, 0.00256548635661602, 0.11378399282693863, -0.21704229712486267, 0.029303357005119324, 0.09001336246728897, 0.11555007100105286, 0.012834642082452774, 0.16859965026378632, -0.05645066499710083, 0.020446237176656723, 0.06289967149496078, -0.21763578057289124, 0.0889396145939827, 0.008556459099054337, -0.045660629868507385, -0.05112776160240173, -0.0488203726708889, 0.15521620213985443, 0.1799469143152237, -0.08392713218927383, -0.1252264827489853, 0.12688834965229034, -0.16272303462028503, -0.0059747654013335705, 0.11126086860895157, -0.05714874342083931, -0.22971230745315552, -0.29469361901283264, 0.06629597395658493, 0.3588842749595642, 0.14117838442325592, -0.23664569854736328, 0.04233122244477272, -0.13016073405742645, -0.06076754629611969, 0.0843462347984314, -0.003551986999809742, -0.0922798365354538, 0.11120974272489548, -0.18186220526695251, 0.05274641513824463, 0.19318532943725586, 0.1098114550113678, -0.00675872853025794, 0.24516640603542328, 0.004723906517028809, -0.02098318189382553, 0.06575548648834229, 0.06614453345537186, -0.08137315511703491, 0.056486696004867554, -0.17871764302253723, 0.05197261646389961, 0.08789300918579102, -0.08278688788414001, -0.004674157593399286, 0.024831831455230713, -0.171482652425766, 0.04835579916834831, 0.03964618965983391, 0.004917219281196594, -0.04221242666244507, 0.05047902092337608, -0.19343340396881104, -0.042385783046483994, 0.10781870782375336, -0.25721096992492676, 0.11885086447000504, 0.10847093909978867, -0.04065236449241638, 0.09623943269252777, 0.03929131478071213, 0.051684118807315826, -0.00010544713586568832, -0.04362337291240692, -0.06941690295934677, -0.010879884473979473, 0.11396230757236481, -0.0512842983007431, 0.07095466554164886, 0.05898372828960419]'),(24,3,'/static/faces/student_3.jpg','[-0.24339118599891663, 0.11631220579147339, 0.07830405235290527, -0.014898478053510189, 0.005886519327759743, -0.07516685128211975, 0.025240987539291382, -0.11942671239376068, 0.17100949585437775, 0.02483118139207363, 0.20726290345191956, -9.972229599952698e-05, -0.15928897261619568, -0.17272117733955383, 0.0032951636239886284, 0.10115425288677216, -0.08404054492712021, -0.18095310032367706, -0.0784582644701004, -0.04462410509586334, 0.02145439386367798, -0.07233339548110962, 0.028778566047549248, 0.15773925185203552, -0.1678806096315384, -0.3390343189239502, -0.07815515995025635, -0.14393922686576843, -0.055382996797561646, -0.09755516052246094, -0.04354415461421013, -0.01134382002055645, -0.21003688871860504, -0.11830919981002808, -0.04405919462442398, 0.10675925761461258, 0.016642572358250618, -0.030453769490122795, 0.186079204082489, -0.06064174324274063, -0.17834512889385223, -0.04458294436335564, 0.1191602349281311, 0.2643193006515503, 0.16152434051036835, 0.0028781909495592117, 0.022814244031906128, 0.015297180972993374, 0.12233162671327591, -0.2140371948480606, 0.10455546528100967, 0.08315642178058624, 0.16811367869377136, 0.01648261770606041, 0.15930680930614471, -0.10644514113664627, -0.006912047043442726, 0.09411653876304626, -0.21145576238632202, 0.10419756919145584, -0.0006741662509739399, -0.0115741528570652, -0.05135754495859146, -0.053801435977220535, 0.19396033883094788, 0.20721806585788727, -0.08035583794116974, -0.11755512654781342, 0.13384848833084106, -0.17193330824375153, -0.0019321832805871964, 0.10949698090553284, -0.04520825669169426, -0.21301569044589996, -0.29779037833213806, 0.08486286550760269, 0.37719273567199707, 0.15976999700069427, -0.23156704008579254, -0.0005505066365003586, -0.10541100054979324, -0.04665987938642502, 0.0633406788110733, -0.017446506768465042, -0.11098850518465042, 0.08733761310577393, -0.16039535403251648, -0.009771678596735, 0.1926894336938858, 0.12765547633171082, -0.03258340060710907, 0.21592514216899872, 0.015188736841082573, -0.01951492205262184, 0.06722153723239899, 0.05889388546347618, -0.0877179354429245, 0.03158752992749214, -0.1460169404745102, 0.029419830068945885, 0.05603805556893349, -0.056689657270908356, 0.014429977163672447, 0.021755892783403397, -0.16349995136260986, 0.029636094346642494, 0.03203270584344864, 0.012349030934274197, -0.055413294583559036, 0.09548203647136688, -0.19151218235492706, -0.0831550806760788, 0.10958390682935715, -0.26519808173179626, 0.14598996937274933, 0.09497255086898804, -0.04887606203556061, 0.10727397352457047, 0.05490221083164215, 0.05461103841662407, 0.01320482324808836, -0.0313960425555706, -0.0370141863822937, -0.029781339690089226, 0.11010816693305969, -0.08037450164556503, 0.11277823150157928, 0.07203008234500885]');
/*!40000 ALTER TABLE `face_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty` (
  `faculty_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `designation` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`faculty_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `faculty_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty`
--

LOCK TABLES `faculty` WRITE;
/*!40000 ALTER TABLE `faculty` DISABLE KEYS */;
INSERT INTO `faculty` VALUES (2,6,'Professor'),(3,8,'Assistant Professor'),(4,9,'Lecturer');
/*!40000 ALTER TABLE `faculty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `feedback_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `subject` varchar(100) DEFAULT NULL,
  `message` text,
  PRIMARY KEY (`feedback_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
INSERT INTO `feedback` VALUES (1,'Ashish','22bmiit150@gmail.com','Issue in login','fix the issue '),(2,'Ashish','ashishvaghasiya150@gmail.com','gv','bbbb');
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `role_id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Admin'),(2,'Faculty'),(3,'Student');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `semesters`
--

DROP TABLE IF EXISTS `semesters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `semesters` (
  `semester_id` int NOT NULL AUTO_INCREMENT,
  `semester_name` varchar(30) NOT NULL,
  PRIMARY KEY (`semester_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semesters`
--

LOCK TABLES `semesters` WRITE;
/*!40000 ALTER TABLE `semesters` DISABLE KEYS */;
INSERT INTO `semesters` VALUES (1,'FIRST'),(2,'SECOND'),(3,'THIRD'),(4,'FOURTH'),(5,'FIFTH'),(6,'SIXTH');
/*!40000 ALTER TABLE `semesters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `student_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `course_id` int NOT NULL,
  `semester_id` int NOT NULL,
  `face_registered` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`student_id`),
  KEY `user_id` (`user_id`),
  KEY `course_id` (`course_id`),
  KEY `students_semesters_FK` (`semester_id`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `students_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`),
  CONSTRAINT `students_semesters_FK` FOREIGN KEY (`semester_id`) REFERENCES `semesters` (`semester_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (1,7,7,3,1),(2,10,6,1,0),(3,11,2,2,1);
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subjects`
--

DROP TABLE IF EXISTS `subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subjects` (
  `subject_id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `semester_id` int NOT NULL,
  `faculty_id` int NOT NULL,
  `subject_name` varchar(100) NOT NULL,
  `subject_code` varchar(20) NOT NULL,
  PRIMARY KEY (`subject_id`),
  UNIQUE KEY `subject_code` (`subject_code`),
  KEY `course_id` (`course_id`),
  KEY `semester_id` (`semester_id`),
  KEY `faculty_id` (`faculty_id`),
  CONSTRAINT `subjects_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`),
  CONSTRAINT `subjects_ibfk_2` FOREIGN KEY (`semester_id`) REFERENCES `semesters` (`semester_id`),
  CONSTRAINT `subjects_ibfk_3` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`faculty_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subjects`
--

LOCK TABLES `subjects` WRITE;
/*!40000 ALTER TABLE `subjects` DISABLE KEYS */;
INSERT INTO `subjects` VALUES (1,2,2,2,'Operating System','OS012'),(2,2,2,3,'Computer Network','CS012'),(3,6,1,4,'AI/ML','AIML013'),(6,7,3,4,'Deep Learning','DL0012');
/*!40000 ALTER TABLE `subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `role_id` int DEFAULT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  `profile_img` varchar(100) DEFAULT NULL,
  `status` int NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `users_unique` (`email`),
  KEY `users_roles_FK` (`role_id`),
  CONSTRAINT `users_roles_FK` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,1,'Ashish Vaghasiya','ashishvaghasiya150@gmail.com','scrypt:32768:8:1$Mvj7c5hOYJoeJoKk$c1aaa6fdba999edb93f4601fc51335298feedc305d0aa4932ccd92a745425e9864c2249c253ca77c4aee4cc9262753bb3a3a450984746528a0599dde226802e7','/assets/img/Users/Admin/Admin.jpg',1,'2026-07-18 09:00:00'),(6,2,'Ashish Faculty','ashishkumarvaghasiya.25.msc@iict.indusuni.ac.in','scrypt:32768:8:1$KbphTYRjDheK9QBI$7f16dffef1e7103da4a5ea56bad749f0d6a15ed4231cdc9b87700ad52e313b36e09e9095d0f12f08f7b7d748387d9baca06c9f7ec165f3464a4624cf0977e8bd','/assets/img/Users/Faculty/IMG_20251013_233757.jpg',1,'2026-07-24 08:48:16'),(7,3,'Yash I Student','yashitaliya18@gmail.com','scrypt:32768:8:1$z5R7oKHOSMI8af8U$0bcf1172e09d7cc5619d61553cc530739a17f66f7da35eb24549415f6f907ed26016518d7512442f9b865e674e9d40260da9505eb00d774c74978405d0a91369','/assets/img/Users/Student/7_Yash_Italiya.jpg',1,'2026-07-24 13:09:43'),(8,2,'Yash Italiya','yashitaliya.25.msc@iict.indusuni.ac.in',NULL,'/assets/img/Users/Faculty/Default.jpg',1,'2026-07-31 13:59:34'),(9,2,'Utpal Parmar','utpalparmar.25.msc@iict.indusuni.ac.in',NULL,'/assets/img/Users/Faculty/Default.jpg',1,'2026-07-31 14:01:53'),(10,3,'Ashish Student','ashish.vaghasiya.077@gmail.com',NULL,'/assets/img/Users/Student/Default.jpg',1,'2026-07-31 14:04:49'),(11,3,'Sujal Shah','sujalshah.25.msc@iict.indusuni.ac.in','scrypt:32768:8:1$1ZAJPoiThuSGco1j$2e78a431b5d08fbfed72756c53bd5a6b534579fcd78feb913387eacf7c06826a9dbf4de901e82b611ad40fb9c90d849bb3c1d330f12ad9d4e22346f00f9056f9','/assets/img/Users/Student/Default.jpg',1,'2026-07-31 14:06:17');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'attendease'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-09 16:51:34
