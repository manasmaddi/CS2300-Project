-- Drop tables if they already exist
DROP TABLE IF EXISTS FoodEntry CASCADE;
DROP TABLE IF EXISTS FoodLog CASCADE;
DROP TABLE IF EXISTS WeightLog CASCADE;
DROP TABLE IF EXISTS CaloricPlan CASCADE;
DROP TABLE IF EXISTS Authentication CASCADE;
DROP TABLE IF EXISTS "User" CASCADE;

-- User table
CREATE TABLE "User" (
    userID SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, 
    height INT,
    startingWeight FLOAT,
    currentWeight FLOAT,
    goalWeight FLOAT
);


-- Authentication table
CREATE TABLE Authentication (
    authID SERIAL PRIMARY KEY,
    userID INT,
    hashedPassword TEXT NOT NULL,
    last_login TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES "User"(userID) ON DELETE CASCADE
);

-- WeightLog table
CREATE TABLE WeightLog (
    logID SERIAL PRIMARY KEY,
    userID INT,
    weight FLOAT NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (userID) REFERENCES "User"(userID) ON DELETE CASCADE
);

-- FoodLog table
CREATE TABLE FoodLog (
    entryID SERIAL PRIMARY KEY,
    userID INT,
    date DATE NOT NULL,
    totalCalories INT DEFAULT 0,
    totalFats INT DEFAULT 0,
    totalCarbs INT DEFAULT 0,
    totalProteins INT DEFAULT 0,
    FOREIGN KEY (userID) REFERENCES "User"(userID) ON DELETE CASCADE
);

-- FoodEntry table
CREATE TABLE FoodEntry (
    id SERIAL PRIMARY KEY,
    entryID INT,
    foodName VARCHAR(255) NOT NULL,
    calories INT DEFAULT 0,
    fats INT DEFAULT 0,
    carbs INT DEFAULT 0,
    proteins INT DEFAULT 0,
    date DATE NOT NULL,
    FOREIGN KEY (entryID) REFERENCES FoodLog(entryID) ON DELETE CASCADE
);

-- CaloricPlan table
CREATE TABLE CaloricPlan (
    planID SERIAL PRIMARY KEY,
    userID INT,
    recCalories INT DEFAULT 0,
    recProtein INT DEFAULT 0,
    recCarbs INT DEFAULT 0,
    recFats INT DEFAULT 0,
    goalType VARCHAR(50),
    FOREIGN KEY (userID) REFERENCES "User"(userID) ON DELETE CASCADE
);
