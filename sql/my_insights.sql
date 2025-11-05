CREATE DATABASE my_insights;
USE my_insights;

-- Routes
CREATE TABLE routes (
    route_id VARCHAR(20) PRIMARY KEY,
    route_number VARCHAR(20) NOT NULL,
    route_name VARCHAR(100) NOT NULL,
    route_type VARCHAR(50),
    route_status VARCHAR(50),
    geometry TEXT
);

-- Stops
CREATE TABLE stops (
    stop_id VARCHAR(20) PRIMARY KEY,
    stop_name VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

-- Trips
CREATE TABLE trips (
    trip_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id VARCHAR(20),
    start_stop_id VARCHAR(20),
    end_stop_id VARCHAR(20),
    start_time DATETIME,
    end_time DATETIME,
    passenger_count INT,
    fare_amount FLOAT,
    FOREIGN KEY (route_id) REFERENCES routes(route_id),
    FOREIGN KEY (start_stop_id) REFERENCES stops(stop_id),
    FOREIGN KEY (end_stop_id) REFERENCES stops(stop_id)
);

-- Add columns to stops
ALTER TABLE stops
ADD COLUMN stop_type VARCHAR(50),
ADD COLUMN stop_status VARCHAR(20),
ADD COLUMN stop_description TEXT;


-- verify data
SELECT COUNT(*) FROM routes;
SELECT COUNT(*) FROM stops;

-- check for duplicates and anomalies
SELECT route_id, COUNT(*) 
FROM routes 
GROUP BY route_id 
HAVING COUNT(*) > 1;

SELECT stop_id, COUNT(*) 
FROM stops 
GROUP BY stop_id 
HAVING COUNT(*) > 1;

-- Reconfigure id data types for routes
-- Temporarily drop foreign key constraints
ALTER TABLE trips DROP FOREIGN KEY trips_ibfk_2;
ALTER TABLE trips DROP FOREIGN KEY trips_ibfk_3;

-- Change column types
ALTER TABLE stops MODIFY stop_id INT;
ALTER TABLE trips MODIFY start_stop_id INT;
ALTER TABLE trips MODIFY end_stop_id INT;

-- Re-add foreign keys
ALTER TABLE trips
ADD CONSTRAINT trips_ibfk_2 FOREIGN KEY (start_stop_id) REFERENCES stops(stop_id),
ADD CONSTRAINT trips_ibfk_3 FOREIGN KEY (end_stop_id) REFERENCES stops(stop_id);

-- Reconfigure id data types for routes
-- 1️⃣ Drop foreign key constraint temporarily
ALTER TABLE trips DROP FOREIGN KEY trips_ibfk_1;

-- 2️⃣ Modify the column types
ALTER TABLE routes MODIFY route_id INT;
ALTER TABLE trips MODIFY route_id INT;

-- 3️⃣ Re-add the foreign key constraint
ALTER TABLE trips
ADD CONSTRAINT trips_ibfk_1 FOREIGN KEY (route_id) REFERENCES routes(route_id);


-- duplicates strict check 
SELECT 
    route_number, 
    route_name, 
    COUNT(*) AS count
FROM routes
GROUP BY route_number, route_name
HAVING COUNT(*) > 1;

-- prevent duplicates at database level
ALTER TABLE routes 
ADD CONSTRAINT unique_route UNIQUE (route_number, route_name);

-- truncate tables to load improved data with no 0 duplicates
SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE stops;
TRUNCATE TABLE routes;
SET FOREIGN_KEY_CHECKS=1;



