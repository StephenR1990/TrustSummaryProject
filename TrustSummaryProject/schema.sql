

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    fullname TEXT NOT NULL,
    accounttype TEXT NOT NULL);

 INSERT INTO users(username,password,fullname,accounttype)
 VALUES("SRogers","Test1234","Stephen Rogers","Admin");

 INSERT INTO users(username,password,fullname,accounttype)
 VALUES("SJones","Test6789","Stephen Jones","User");

  DROP TABLE IF EXISTS DailySummary;
 CREATE TABLE DailySummary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dte TEXT NOT NULL ,
    [SiteManager] TEXT,
    [PatientsInCorridor] INTEGER,
    [EscalationLevel] TEXT,
    [TriageTimehrs] REAL,
    [PatientsAwaitingBeds] INTEGER,
    [WaitingTimeMajorshrs] REAL,
    [TotalPatientsED] INTEGER,
    [userid] INTEGER
    );

    INSERT INTO DailySummary(dte,[SiteManager],[PatientsInCorridor], [EscalationLevel],
                               [TriageTimehrs], [PatientsAwaitingBeds],[WaitingTimeMajorshrs],
                                 [TotalPatientsED], [userid])
    VALUES("10/06/2025","Stephen",13,"Amber",3.5, 4,1.8,45,1)
            ,("11/06/2025","Sharon",18,"Red",3, 2,3,55,1)
            ,("12/06/2025","Mark",11,"Amber",2.5, 1,2.2,40,1)
            ,("13/06/2025","Mark",15,"Amber",4.7, 6,2.6,39,1)
            ,("14/06/2025","Mary",9,"Amber",3, 1,1.7,33,1)
            ,("15/06/2025","Stephen",5,"Green",1.5,4,1.4,44,1)
            ,("16/06/2025","Mark",21,"Red",5, 7,1.8,66,1)
            ,("17/06/2025","Sharon",15,"Red",3.9, 4,1.8,49,1)
            ,("18/06/2025","Sharon",12,"Amber",2.5, 6,3,43,1)
            ,("19/06/2025","Sharon",16,"Red",3.1, 5,1.7,67,1)
            ,("20/06/2025","Mary",13,"Amber",2.7, 1,3.8,41,1)
            ,("21/06/2025","Mark",12,"Amber",3.3, 2,2.8,35,1)
