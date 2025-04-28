DROP TABLE IF EXISTS FoodEntry CASCADE;
DROP TABLE IF EXISTS FoodLog CASCADE;
DROP TABLE IF EXISTS WeightLog CASCADE;
DROP TABLE IF EXISTS CaloricPlan CASCADE;
DROP TABLE IF EXISTS Authentication CASCADE;
DROP TABLE IF EXISTS "User" CASCADE;


-- User table
CREATE TABLE "User" (
    user_id INT GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    height INT,
    starting_weight FLOAT,
    current_weight FLOAT,
    goal_weight FLOAT,
    PRIMARY KEY (user_id)
);

-- Authentication table
CREATE TABLE Authentication (
    auth_id INT GENERATED ALWAYS AS IDENTITY,
    user_id INT,
    hashed_password TEXT NOT NULL,
    last_login TIMESTAMP,
    PRIMARY KEY (auth_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE CASCADE
);

-- WeightLog table
CREATE TABLE WeightLog (
    log_id INT GENERATED ALWAYS AS IDENTITY,
    user_id INT,
    weight FLOAT NOT NULL,
    date DATE NOT NULL,
    PRIMARY KEY (log_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE CASCADE
);

-- FoodLog table
CREATE TABLE FoodLog (
    entry_id INT GENERATED ALWAYS AS IDENTITY,
    user_id INT,
    date DATE NOT NULL,
    total_calories INT DEFAULT 0,
    total_fats INT DEFAULT 0,
    total_carbs INT DEFAULT 0,
    total_proteins INT DEFAULT 0,
    PRIMARY KEY (entry_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE CASCADE
);

-- FoodEntry table
CREATE TABLE FoodEntry (
    id INT GENERATED ALWAYS AS IDENTITY,
    entry_id INT,
    food_name VARCHAR(255) NOT NULL,
    calories INT DEFAULT 0,
    fats INT DEFAULT 0,
    carbs INT DEFAULT 0,
    proteins INT DEFAULT 0,
    date DATE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (entry_id) REFERENCES FoodLog(entry_id) ON DELETE CASCADE
);

-- CaloricPlan table
CREATE TABLE CaloricPlan (
    plan_id INT GENERATED ALWAYS AS IDENTITY,
    user_id INT,
    rec_calories INT DEFAULT 0,
    rec_carbs INT DEFAULT 0,
    rec_fats INT DEFAULT 0,
    goal_type VARCHAR(50),
    PRIMARY KEY (plan_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE CASCADE
);
