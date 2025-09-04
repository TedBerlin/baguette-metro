-- Script d'initialisation de la base de données Baguette Metro
-- PostgreSQL

-- Création des extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des trajets
CREATE TABLE IF NOT EXISTS routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    start_lat DECIMAL(10, 8) NOT NULL,
    start_lon DECIMAL(11, 8) NOT NULL,
    end_lat DECIMAL(10, 8) NOT NULL,
    end_lon DECIMAL(11, 8) NOT NULL,
    start_location VARCHAR(255),
    end_location VARCHAR(255),
    eta_minutes DECIMAL(5, 2),
    distance_km DECIMAL(6, 3),
    include_bakery BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des boulangeries
CREATE TABLE IF NOT EXISTS bakeries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    lat DECIMAL(10, 8) NOT NULL,
    lon DECIMAL(11, 8) NOT NULL,
    rating DECIMAL(3, 2),
    opening_hours JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des prédictions ETA
CREATE TABLE IF NOT EXISTS eta_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id UUID REFERENCES routes(id) ON DELETE CASCADE,
    model_type VARCHAR(50) NOT NULL,
    predicted_eta DECIMAL(5, 2) NOT NULL,
    actual_eta DECIMAL(5, 2),
    confidence DECIMAL(3, 2),
    features JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des conversations chat
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    language VARCHAR(10) DEFAULT 'fr',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des messages chat
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL, -- 'user' ou 'assistant'
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des métriques système
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10, 4) NOT NULL,
    metric_unit VARCHAR(20),
    tags JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimiser les performances
CREATE INDEX IF NOT EXISTS idx_routes_user_id ON routes(user_id);
CREATE INDEX IF NOT EXISTS idx_routes_created_at ON routes(created_at);
CREATE INDEX IF NOT EXISTS idx_bakeries_location ON bakeries USING GIST (ST_SetSRID(ST_MakePoint(lon, lat), 4326));
CREATE INDEX IF NOT EXISTS idx_eta_predictions_route_id ON eta_predictions(route_id);
CREATE INDEX IF NOT EXISTS idx_eta_predictions_created_at ON eta_predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);

-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bakeries_updated_at BEFORE UPDATE ON bakeries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Données de test
INSERT INTO users (email, username) VALUES 
    ('test@baguette-metro.com', 'test_user')
ON CONFLICT (email) DO NOTHING;

INSERT INTO bakeries (name, address, lat, lon, rating) VALUES 
    ('Boulangerie du Louvre', '123 Rue de Rivoli, 75001 Paris', 48.8606, 2.3376, 4.5),
    ('Boulangerie de Châtelet', '456 Rue de Rivoli, 75001 Paris', 48.8584, 2.3476, 4.2),
    ('Boulangerie de la Tour Eiffel', '789 Avenue des Champs-Élysées, 75008 Paris', 48.8584, 2.2945, 4.7)
ON CONFLICT DO NOTHING;

-- Vues utiles
CREATE OR REPLACE VIEW route_stats AS
SELECT 
    COUNT(*) as total_routes,
    AVG(eta_minutes) as avg_eta,
    AVG(distance_km) as avg_distance,
    COUNT(CASE WHEN include_bakery THEN 1 END) as routes_with_bakery
FROM routes;

CREATE OR REPLACE VIEW bakery_popularity AS
SELECT 
    b.name,
    b.rating,
    COUNT(r.id) as route_count
FROM bakeries b
LEFT JOIN routes r ON ST_DWithin(
    ST_SetSRID(ST_MakePoint(b.lon, b.lat), 4326),
    ST_SetSRID(ST_MakePoint(r.end_lon, r.end_lat), 4326),
    1000  -- 1km radius
)
GROUP BY b.id, b.name, b.rating
ORDER BY route_count DESC;





