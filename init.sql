-- Schéma de base de données pour AgriDetect

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table des utilisateurs
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    preferred_language VARCHAR(5) DEFAULT 'fr',
    location JSONB,
    farm_size DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des cultures
CREATE TABLE crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name_fr VARCHAR(100) NOT NULL,
    name_wo VARCHAR(100),
    name_pu VARCHAR(100),
    scientific_name VARCHAR(255),
    category VARCHAR(50),
    growth_cycle_days INTEGER,
    optimal_temperature_min DECIMAL(5, 2),
    optimal_temperature_max DECIMAL(5, 2),
    water_requirements VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des maladies
CREATE TABLE diseases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name_fr VARCHAR(255) NOT NULL,
    name_wo VARCHAR(255),
    name_pu VARCHAR(255),
    scientific_name VARCHAR(255),
    pathogen_type VARCHAR(50), -- fungus, bacteria, virus, etc.
    severity_level VARCHAR(20), -- low, medium, high
    description_fr TEXT,
    description_wo TEXT,
    description_pu TEXT,
    symptoms JSONB,
    causes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de relation cultures-maladies
CREATE TABLE crop_diseases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_id UUID REFERENCES crops(id) ON DELETE CASCADE,
    disease_id UUID REFERENCES diseases(id) ON DELETE CASCADE,
    prevalence VARCHAR(20), -- rare, common, very_common
    season VARCHAR(50),
    UNIQUE(crop_id, disease_id)
);

-- Table des traitements
CREATE TABLE treatments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name_fr VARCHAR(255) NOT NULL,
    name_wo VARCHAR(255),
    name_pu VARCHAR(255),
    type VARCHAR(50), -- organic, chemical, cultural
    description_fr TEXT,
    description_wo TEXT,
    description_pu TEXT,
    application_method TEXT,
    frequency VARCHAR(100),
    dosage VARCHAR(100),
    precautions JSONB,
    is_organic BOOLEAN DEFAULT FALSE,
    estimated_cost_per_hectare DECIMAL(10, 2),
    effectiveness_rating INTEGER CHECK (effectiveness_rating >= 1 AND effectiveness_rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de relation maladies-traitements
CREATE TABLE disease_treatments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    disease_id UUID REFERENCES diseases(id) ON DELETE CASCADE,
    treatment_id UUID REFERENCES treatments(id) ON DELETE CASCADE,
    effectiveness VARCHAR(20), -- low, medium, high
    application_stage VARCHAR(50), -- preventive, early, advanced
    priority INTEGER,
    UNIQUE(disease_id, treatment_id)
);

-- Table des détections
CREATE TABLE detections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    crop_id UUID REFERENCES crops(id),
    disease_id UUID REFERENCES diseases(id),
    image_url TEXT,
    confidence_score DECIMAL(5, 4),
    severity VARCHAR(20),
    location JSONB,
    weather_conditions JSONB,
    detection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    feedback_provided BOOLEAN DEFAULT FALSE,
    feedback_correct BOOLEAN,
    actual_disease_id UUID REFERENCES diseases(id),
    notes TEXT
);

-- Table des messages de chat
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    detection_id UUID REFERENCES detections(id),
    message_text TEXT NOT NULL,
    sender VARCHAR(10) NOT NULL, -- 'user' or 'bot'
    language VARCHAR(5),
    intent VARCHAR(50),
    context JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des conseils de prévention
CREATE TABLE prevention_tips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    disease_id UUID REFERENCES diseases(id) ON DELETE CASCADE,
    tip_fr TEXT NOT NULL,
    tip_wo TEXT,
    tip_pu TEXT,
    category VARCHAR(50), -- cultural, chemical, biological
    effectiveness VARCHAR(20),
    cost_level VARCHAR(20), -- free, low, medium, high
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50), -- alert, reminder, info, warning
    language VARCHAR(5),
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

-- Table des parcelles agricoles
CREATE TABLE farm_plots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    size_hectares DECIMAL(10, 2),
    location JSONB,
    soil_type VARCHAR(100),
    current_crop_id UUID REFERENCES crops(id),
    planting_date DATE,
    expected_harvest_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de l'historique des cultures
CREATE TABLE crop_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plot_id UUID REFERENCES farm_plots(id) ON DELETE CASCADE,
    crop_id UUID REFERENCES crops(id),
    planting_date DATE,
    harvest_date DATE,
    yield_kg DECIMAL(10, 2),
    diseases_encountered JSONB,
    treatments_applied JSONB,
    notes TEXT
);

-- Table des alertes saisonnières
CREATE TABLE seasonal_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region VARCHAR(100),
    season VARCHAR(50),
    crop_id UUID REFERENCES crops(id),
    disease_id UUID REFERENCES diseases(id),
    alert_level VARCHAR(20), -- low, medium, high
    message_fr TEXT,
    message_wo TEXT,
    message_pu TEXT,
    valid_from DATE,
    valid_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_detections_user_date ON detections(user_id, detection_date DESC);
CREATE INDEX idx_detections_disease ON detections(disease_id);
CREATE INDEX idx_chat_messages_user ON chat_messages(user_id, created_at DESC);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read);
CREATE INDEX idx_seasonal_alerts_valid ON seasonal_alerts(valid_from, valid_to);

-- Vues utiles
CREATE VIEW detection_statistics AS
SELECT 
    d.disease_id,
    dis.name_fr as disease_name,
    COUNT(*) as detection_count,
    AVG(d.confidence_score) as avg_confidence,
    DATE_TRUNC('month', d.detection_date) as month
FROM detections d
JOIN diseases dis ON d.disease_id = dis.id
GROUP BY d.disease_id, dis.name_fr, DATE_TRUNC('month', d.detection_date);

CREATE VIEW user_activity AS
SELECT 
    u.id,
    u.name,
    COUNT(DISTINCT d.id) as total_detections,
    COUNT(DISTINCT cm.id) as total_messages,
    MAX(d.detection_date) as last_detection,
    MAX(cm.created_at) as last_message
FROM users u
LEFT JOIN detections d ON u.id = d.user_id
LEFT JOIN chat_messages cm ON u.id = cm.user_id
GROUP BY u.id, u.name;

-- Fonctions triggers pour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insertion de données initiales
INSERT INTO crops (name_fr, name_wo, name_pu, scientific_name, category, growth_cycle_days, water_requirements) VALUES
('Tomate', 'Tomate', 'Tomate', 'Solanum lycopersicum', 'Légume', 90, 'Élevé'),
('Oignon', 'Soble', 'Albasal', 'Allium cepa', 'Légume', 120, 'Modéré'),
('Maïs', 'Mbay', 'Gawri', 'Zea mays', 'Céréale', 100, 'Élevé'),
('Mil', 'Dugub', 'Gawri', 'Pennisetum glaucum', 'Céréale', 80, 'Faible'),
('Arachide', 'Tigadega', 'Birtiije', 'Arachis hypogaea', 'Légumineuse', 120, 'Modéré'),
('Manioc', 'Ñambi', 'Mburu', 'Manihot esculenta', 'Tubercule', 240, 'Faible'),
('Gombo', 'Kànja', 'Baskooje', 'Abelmoschus esculentus', 'Légume', 60, 'Modéré'),
('Piment', 'Kaani', 'Barkono', 'Capsicum', 'Légume', 90, 'Modéré');

INSERT INTO diseases (code, name_fr, name_wo, name_pu, pathogen_type, severity_level) VALUES
('MILDEW_001', 'Mildiou', 'Mildiou', 'Mildiou', 'fungus', 'high'),
('BLIGHT_001', 'Flétrissure bactérienne', 'Feebar bakteriya', 'Ñawu bakteriya', 'bacteria', 'high'),
('RUST_001', 'Rouille', 'Xonq', 'Dila', 'fungus', 'medium'),
('MOSAIC_001', 'Mosaïque virale', 'Wirùs mosayik', 'Virus mosaïque', 'virus', 'high'),
('SPOT_001', 'Tache foliaire', 'Tàkk ci xob bi', 'Tache e leeɗe', 'fungus', 'medium'),
('ROT_001', 'Pourriture des racines', 'Xëy réew yi', 'Boɗde ɗaɗe', 'fungus', 'high');

INSERT INTO treatments (code, name_fr, name_wo, name_pu, type, is_organic, effectiveness_rating) VALUES
('COPPER_001', 'Bouillie bordelaise', 'Garab kuivre', 'Lekki kuivre', 'organic', true, 4),
('NEEM_001', 'Huile de Neem', 'Diw Neem', 'Neɓɓam Neem', 'organic', true, 4),
('SOAP_001', 'Savon noir', 'Saabun ñuul', 'Saabun ɓalewo', 'organic', true, 3),
('SULFUR_001', 'Soufre', 'Sufar', 'Sufar', 'chemical', false, 4),
('ROTATION_001', 'Rotation des cultures', 'Soppi mbay', 'Waylude gese', 'cultural', true, 5),
('DRAINAGE_001', 'Amélioration du drainage', 'Baaxal ndox', 'Moƴƴinde ndiyam', 'cultural', true, 4);