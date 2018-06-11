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

INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password) VALUES ('letty@smu.edu.sg', 'smustu\letty', 'Letty', 'Hefty', 'ZxcvB12345');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password) VALUES ('meat@smu.edu.sg', 'smustu\meat', 'Meat', 'Fish', 'ABcde12345');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password) VALUES ('teo@smu.edu.sg', 'smustu\teo', 'Teo', 'Hong', 'SdfgH45678');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password) VALUES ('levid@smu.edu.sg', 'smustu\levid', 'Levid', 'Peh', 'ghjLL90876');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password) VALUES ('punna@smu.edu.sg', 'smustu\punna', 'Punna', 'Nie', 'QwErt12345');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password) VALUES ('mama@smu.edu.sg', 'smustu\mama', 'Mama', 'Mayo', 'aSdfG12345');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password) VALUES ('eddye@smu.edu.sg', 'smustu\eddye', 'Eddye', 'Tan', 'mnLoP12345');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password) VALUES ('maddie@smu.edu.sg', 'smustu\maddie', 'Maddie', 'Teh', 'zXCvb09876');

INSERT INTO Section (Section_Number) VALUES ('G1');
INSERT INTO Section (Section_Number) VALUES ('G2');
INSERT INTO Section (Section_Number) VALUES ('G3');
INSERT INTO Section (Section_Number) VALUES ('G4');

INSERT INTO Team (Team_Number, Section_Number) VALUES ('T1', 'G1');
INSERT INTO Team (Team_Number, Section_Number) VALUES ('T2', 'G1');
INSERT INTO Team (Team_Number, Section_Number) VALUES ('T1', 'G2');
INSERT INTO Team (Team_Number, Section_Number) VALUES ('T2', 'G2');
INSERT INTO Team (Team_Number, Section_Number) VALUES ('T1', 'G3');
INSERT INTO Team (Team_Number, Section_Number) VALUES ('T2', 'G3');
INSERT INTO Team (Team_Number, Section_Number) VALUES ('T1', 'G4');
INSERT INTO Team (Team_Number, Section_Number) VALUES ('T2', 'G4');

INSERT INTO Section_Instructor (Section_Number, Instructor_Email) VALUES ('G1', 'letty@smu.edu.sg');
INSERT INTO Section_Instructor (Section_Number, Instructor_Email) VALUES ('G1', 'meat@smu.edu.sg');
INSERT INTO Section_Instructor (Section_Number, Instructor_Email) VALUES ('G2', 'teo@smu.edu.sg');
INSERT INTO Section_Instructor (Section_Number, Instructor_Email) VALUES ('G3', 'teo@smu.edu.sg');
INSERT INTO Section_Instructor (Section_Number, Instructor_Email) VALUES ('G2', 'levid@smu.edu.sg');
INSERT INTO Section_Instructor (Section_Number, Instructor_Email) VALUES ('G4', 'punna@smu.edu.sg');
INSERT INTO Section_Instructor (Section_Number, Instructor_Email) VALUES ('G3', 'eddye@smu.edu.sg');

INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section_Number, Team_Number) VALUES ('alfaried@smu.edu.sg', 'smustu\alfaried', 'Al Faried', 'Yusoff', 'Zxcvb12345', 'G1', 'T1');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section_Number, Team_Number) VALUES ('joel@smu.edu.sg', 'smustu\joel', 'Joel', 'Tay', 'Abcde12345', 'G1', 'T2');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section_Number, Team_Number) VALUES ('martin@smu.edu.sg', 'smustu\martin', 'Martin', 'Teo', 'Sdfgh45678', 'G2', 'T1');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section_Number, Team_Number) VALUES ('rizudin@smu.edu.sg', 'smustu\rizudin', 'Rizudin', 'Jalar', 'ghjkL90876', 'G2', 'T2');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section_Number, Team_Number) VALUES ('bernadine@smu.edu.sg', 'smustu\bernadine', 'Bernadine', 'Lye', 'qwErt12345', 'G3', 'T1');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section_Number, Team_Number) VALUES ('tom@smu.edu.sg', 'smustu\tom', 'Tom', 'cat', 'asdfG12345', 'G3', 'T2');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section_Number, Team_Number) VALUES ('eddie@smu.edu.sg', 'smustu\eddie', 'Eddie', 'Hall', 'mnloP12345', 'G4', 'T1');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section_Number, Team_Number) VALUES ('ben@smu.edu.sg', 'smustu\ben', 'Ben', 'Ten', 'zXcvb09876', 'G4', 'T2');

