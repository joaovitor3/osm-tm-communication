CREATE TABLE PROJECT (
    projectId INTEGER NOT NULL,
    timeframe DATE NOT NULL,
    externalSource VARCHAR(300) NOT NULL,
    description VARCHAR(300) NOT NULL,
    creationDate DATE DEFAULT CURRENT_DATE,
    CONSTRAINT PROJECT_PK PRIMARY KEY(projectId)
);
-- \du