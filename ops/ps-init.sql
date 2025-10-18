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

CREATE INDEX idx_spots_bbox ON parking_spots USING BTREE(latitude, longitude);
CREATE INDEX idx_spots_bbox_status ON parking_spots USING BTREE(status, latitude, longitude);

-- Paid parking spots
CREATE TABLE paid_parking (
    spot_id        INTEGER PRIMARY KEY
                   REFERENCES parking_spots(id) ON DELETE CASCADE,
    price_per_hour NUMERIC(8,2) NOT NULL CHECK (price_per_hour >= 0)
);

CREATE INDEX idx_paid_parking_price ON paid_parking (price_per_hour);


-- Athens parking spots
INSERT INTO parking_spots (latitude, longitude, location, status) VALUES
(37.9755, 23.7348, 'Athens - Syntagma Square', 'Available'),
(37.9838, 23.7275, 'Athens - Monastiraki', 'Available'),
(37.9879, 23.7300, 'Athens - Plaka District', 'Occupied'),
(37.9742, 23.7370, 'Athens - National Garden', 'Available'),
(37.9842, 23.7278, 'Athens - Omonia Square', 'Occupied'),
(37.9807, 23.7339, 'Athens - Panepistimiou', 'Available'),
(37.9786, 23.7406, 'Athens - Kolonaki', 'Available'),
(37.9653, 23.7284, 'Athens - Koukaki', 'Occupied'),
(37.9757, 23.7200, 'Athens - Thissio', 'Available'),
(37.9685, 23.7285, 'Athens - Acropolis Museum', 'Reserved'),
(37.9724, 23.7361, 'Athens - Zappeion', 'Available'),
(37.9770, 23.7187, 'Athens - Kerameikos', 'Occupied'),
(37.9785, 23.7116, 'Athens - Gazi', 'Available'),
(37.9680, 23.7085, 'Athens - Petralona', 'Available'),
(37.9675, 23.7450, 'Athens - Pangrati', 'Occupied'),
(37.9870, 23.7380, 'Athens - Exarchia', 'Reserved'),
(37.9952, 23.7303, 'Athens - Victoria Square', 'Available'),
(37.9830, 23.7210, 'Athens - Metaxourgeio', 'Available'),
(37.9762, 23.7278, 'Athens - Ermou Street', 'Occupied'),
(37.9724, 23.7288, 'Athens - Anafiotika', 'Available'),
(37.9789, 23.7320, 'Athens - Stadiou Street', 'Reserved'),
(37.9696, 23.7411, 'Athens - Panathenaic Stadium (Kallimarmaro)', 'Available'),
(37.9826, 23.7445, 'Athens - Lycabettus Hill Base', 'Occupied'),
(37.9891, 23.7610, 'Athens - Ampelokipoi', 'Available'),
(37.9769, 23.7690, 'Athens - Zografou', 'Available'),
(37.9563, 23.7289, 'Athens - Neos Kosmos', 'Occupied'),
(37.9458, 23.7142, 'Athens - Nea Smyrni Square', 'Available'),
(37.9644, 23.7266, 'Athens - Syngrou Fix', 'Reserved'),
(37.9780, 23.7365, 'Athens - Syntagma North', 'Available'),
(37.9751, 23.7379, 'Athens - Syntagma East', 'Available'),
(37.9761, 23.7245, 'Athens - Monastiraki Flea Market', 'Occupied'),
(37.9890, 23.7315, 'Athens - National Archaeological Museum', 'Available'),
(37.9768, 23.7480, 'Athens - Evangelismos', 'Available'),
(37.9799, 23.7573, 'Athens - Ilisia', 'Occupied'),
(37.9493, 23.7357, 'Athens - Dafni', 'Available'),
(37.9935, 23.7638, 'Athens - Kifisias (Ampelokipoi)', 'Reserved'),
(37.9767, 23.7331, 'Athens - Syntagma West', 'Available'),
(37.9780, 23.7238, 'Athens - Psyrri', 'Occupied'),
(37.9740, 23.7280, 'Athens - Acropolis North Slope', 'Available'),
(37.9720, 23.7207, 'Athens - Areopagus Hill', 'Available');


-- Larissa parking spots
INSERT INTO parking_spots (latitude, longitude, location, status) VALUES
(39.6390, 22.4194, 'Larissa - Central Square', 'Available'),
(39.6420, 22.4150, 'Larissa - Railway Station', 'Occupied'),
(39.6360, 22.4220, 'Larissa - Shopping Center', 'Available'),
(39.6380, 22.4180, 'Larissa - Municipal Park', 'Reserved');

-- paid parking spots
INSERT INTO paid_parking (spot_id, price_per_hour) VALUES
(1, 2.50),
(3, 3.00),
(5, 2.00),
(10, 4.00),
(11, 2.00),
(12, 5.00),
(15, 2.75);
