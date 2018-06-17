-- ***************************************************************************************
-- DROP DATABASE if exists CLEdb;
CREATE DATABASE IF NOT EXISTS CLEdb;
USE CLEdb;

-- ***************************************************************************************
-- Create Tables;

    CREATE TABLE `Instructor` (
      `Email` varchar(255) NOT NULL,
      `Username` varchar(255),
      `Firstname` varchar(255),
      `Lastname` varchar(255),
      `Password` varchar(255),
      PRIMARY KEY (`Email`)
    );

    CREATE TABLE `Section` (
      `Section_Number` varchar(255) NOT NULL,
      PRIMARY KEY (`Section_Number`)
    );

    CREATE TABLE `Team` (
      `Team_Number` varchar(255),
      `Section_Number` varchar(255),
      PRIMARY KEY (`Section_Number`,`Team_Number`),
      FOREIGN KEY (`Section_Number`) REFERENCES `Section`(`Section_Number`)
    );

    CREATE TABLE `Section_Instructor` (
      `Section_Number` varchar(255),
      `Instructor_Email` varchar(255),
      PRIMARY KEY (`Section_Number`,`Instructor_Email`),
      FOREIGN KEY (`Section_Number`) REFERENCES `Section`(`Section_Number`),
      FOREIGN KEY (`Instructor_Email`) REFERENCES `Instructor`(`Email`)
    );

    CREATE TABLE `Student` (
      `Email` varchar(255) NOT NULL,
      `Username` varchar(255),
      `Firstname` varchar(255),
      `Lastname` varchar(255),
      `Password` varchar(255),
      `Section_Number` varchar(255),
      `Team_Number` varchar(255),
      PRIMARY KEY (`Email`),
      FOREIGN KEY (`Section_Number`,`Team_Number`) REFERENCES `Team`(`Section_Number`,`Team_Number`)
    );


-- DROP TABLE CLEdb;
