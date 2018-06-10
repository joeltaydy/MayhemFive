CREATE TABLE `Instructor` (
  `Email` varchar(255),
  `Username` varchar(255),
  `Firstname` varchar(255),
  `Lastname` varchar(255),
  `Password` varchar(255),
  `Section` varchar(255),
  PRIMARY KEY (`Email`)
);

CREATE TABLE `Student` (
  `Email` varchar(255),
  `Username` varchar(255),
  `Firstname` varchar(255),
  `Lastname` varchar(255),
  `Password` varchar(255),
  `Section` varchar(255),
  `Team` varchar(255),
  PRIMARY KEY (`Email`)
);

INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section, Team) VALUES ('alfaried@smu.edu.sg', 'smustu\alfaried', 'Al Faried', 'Yusoff', 'Zxcvb12345', 'G1', 'T1');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section, Team) VALUES ('joel@smu.edu.sg', 'smustu\joel', 'Joel', 'Tay', 'Abcde12345', 'G1', 'T2');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section, Team) VALUES ('martin@smu.edu.sg', 'smustu\martin', 'Martin', 'Teo', 'Sdfgh45678', 'G2', 'T1');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section, Team) VALUES ('rizudin@smu.edu.sg', 'smustu\rizudin', 'Rizudin', 'Jalar', 'ghjkL90876', 'G2', 'T2');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section, Team) VALUES ('bernadine@smu.edu.sg', 'smustu\bernadine', 'Bernadine', 'Lye', 'qwErt12345', 'G3', 'T1');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section, Team) VALUES ('tom@smu.edu.sg', 'smustu\tom', 'Tom', 'cat', 'asdfG12345', 'G3', 'T2');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section, Team) VALUES ('eddie@smu.edu.sg', 'smustu\eddie', 'Eddie', 'Hall', 'mnloP12345', 'G4', 'T1');
INSERT INTO Student (Email, Username, Firstname, Lastname, Password, Section, Team) VALUES ('ben@smu.edu.sg', 'smustu\ben', 'Ben', 'Ten', 'zXcvb09876', 'G4', 'T2');

INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password, Section) VALUES ('letty@smu.edu.sg', 'smustu\letty', 'Letty', 'Hefty', 'ZxcvB12345', 'G1');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password, Section) VALUES ('meat@smu.edu.sg', 'smustu\meat', 'Meat', 'Fish', 'ABcde12345', 'G1');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password, Section) VALUES ('teo@smu.edu.sg', 'smustu\teo', 'Teo', 'Hong', 'SdfgH45678', 'G2');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password, Section) VALUES ('levid@smu.edu.sg', 'smustu\levid', 'Levid', 'Peh', 'ghjLL90876', 'G2');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password, Section) VALUES ('punna@smu.edu.sg', 'smustu\punna', 'Punna', 'Nie', 'QwErt12345', 'G3');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password, Section) VALUES ('mama@smu.edu.sg', 'smustu\mama', 'Mama', 'Mayo', 'aSdfG12345', 'G3');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password, Section) VALUES ('eddye@smu.edu.sg', 'smustu\eddye', 'Eddye', 'Tan', 'mnLoP12345', 'G4');
INSERT INTO Instructor (Email, Username, Firstname, Lastname, Password, Section) VALUES ('maddie@smu.edu.sg', 'smustu\maddie', 'Maddie', 'Teh', 'zXCvb09876', 'G4');
