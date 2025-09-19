-- parking_db.sql

CREATE TABLE parking_spots (
                               id SERIAL PRIMARY KEY,
                               latitude DOUBLE PRECISION NOT NULL,
                               longitude DOUBLE PRECISION NOT NULL,
                               location VARCHAR(100) NOT NULL,
                               status VARCHAR(20) NOT NULL DEFAULT 'Available',
                               last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX idx_parking_spots_status ON parking_spots (status);
CREATE INDEX idx_parking_spots_location ON parking_spots (location);

-- Status log
CREATE TABLE spot_status_log (
                                 id SERIAL PRIMARY KEY,
                                 spot_id INTEGER NOT NULL,
                                 status VARCHAR(20) NOT NULL,
                                 timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
                                 FOREIGN KEY (spot_id) REFERENCES parking_spots(id) ON DELETE CASCADE
);

-- Users
CREATE TABLE users (
                       id SERIAL PRIMARY KEY,
                       email VARCHAR(100) UNIQUE NOT NULL,
                       password_hash TEXT NOT NULL,
                       full_name VARCHAR(100),
                       created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
);

-- Favorites
CREATE TABLE user_favorites (
                                user_id INTEGER,
                                spot_id INTEGER,
                                PRIMARY KEY (user_id, spot_id),
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                                FOREIGN KEY (spot_id) REFERENCES parking_spots(id) ON DELETE CASCADE
);

-- Reservations
CREATE TABLE reservations (
                              id SERIAL PRIMARY KEY,
                              user_id INTEGER NOT NULL,
                              spot_id INTEGER NOT NULL,
                              start_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                              end_time TIMESTAMP WITHOUT TIME ZONE,
                              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                              FOREIGN KEY (spot_id) REFERENCES parking_spots(id) ON DELETE CASCADE
);