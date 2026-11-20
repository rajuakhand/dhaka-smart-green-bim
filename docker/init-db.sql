-- DhakaSmart Database Schema
-- PostgreSQL 15+ with PostGIS

CREATE EXTENSION IF NOT EXISTS postgis;

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    building_name TEXT,
    city TEXT DEFAULT 'Dhaka',
    building_type TEXT NOT NULL,
    num_floors INT NOT NULL,
    floor_to_floor_height NUMERIC NOT NULL,
    total_floor_area NUMERIC,
    orientation_deg NUMERIC,
    construction_year INT,
    structural_system TEXT,
    plot_area NUMERIC,
    building_footprint GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Rooms table
CREATE TABLE IF NOT EXISTS rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    room_type TEXT NOT NULL,
    length NUMERIC NOT NULL,
    width NUMERIC NOT NULL,
    height NUMERIC NOT NULL,
    floor_area NUMERIC,
    volume NUMERIC,
    window_area NUMERIC DEFAULT 0,
    openable_window_area NUMERIC DEFAULT 0,
    occupants INT NOT NULL,
    occupancy_schedule TEXT,
    orientation_deg NUMERIC,
    glazing_type TEXT,
    external_obstruction_height NUMERIC DEFAULT 0,
    shading_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Calculation results
CREATE TABLE IF NOT EXISTS calculation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    module_id TEXT NOT NULL,
    version INT DEFAULT 1,
    input_snapshot JSONB NOT NULL,
    result JSONB NOT NULL,
    confidence TEXT NOT NULL,
    limitations JSONB,
    source_references JSONB,
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Emission factors reference data
CREATE TABLE IF NOT EXISTS emission_factors (
    id SERIAL PRIMARY KEY,
    source_id TEXT NOT NULL UNIQUE,
    year INT NOT NULL,
    factor_kg_co2_per_kwh NUMERIC NOT NULL,
    scope TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    verified BOOLEAN DEFAULT FALSE,
    source_url TEXT
);

-- Seed emission factors
INSERT INTO emission_factors (source_id, year, factor_kg_co2_per_kwh, scope, is_default, verified, source_url)
VALUES
    ('DoE-GEF', 2022, 0.62, 'location-based', TRUE, TRUE, 'DoE letter 22.02.0000.063.61.009.23-37'),
    ('Ember-OWID', 2025, 0.696, 'generation-based', FALSE, TRUE, 'github.com/owid/energy-data')
ON CONFLICT (source_id) DO NOTHING;

-- BNBC rules reference data
CREATE TABLE IF NOT EXISTS bnbc_rules (
    id SERIAL PRIMARY KEY,
    rule_id TEXT NOT NULL UNIQUE,
    section TEXT NOT NULL,
    description TEXT NOT NULL,
    formula TEXT,
    required_inputs TEXT[],
    applicability TEXT,
    verified BOOLEAN DEFAULT FALSE
);

-- Seed BNBC rules
INSERT INTO bnbc_rules (rule_id, section, description, formula, required_inputs, applicability, verified)
VALUES
    ('BNBC-2020-2.14.6.1', '2.14.6.1', 'Natural light: min 10% glazed area of floor area', 'glazed_area / floor_area >= 0.10', ARRAY['window_area', 'floor_area'], 'All occupied rooms', TRUE),
    ('BNBC-2020-2.14.6.1b', '2.14.6.1', 'Natural ventilation: min 5% openable area of floor area', 'openable_area / floor_area >= 0.05', ARRAY['openable_window_area', 'floor_area'], 'All occupied rooms', TRUE)
ON CONFLICT (rule_id) DO NOTHING;

-- Weather stations
CREATE TABLE IF NOT EXISTS weather_stations (
    id SERIAL PRIMARY KEY,
    wmo_code TEXT UNIQUE,
    city TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    elevation NUMERIC,
    epw_source TEXT,
    epw_path TEXT,
    tm_years TEXT[]
);

-- Seed weather stations
INSERT INTO weather_stations (wmo_code, city, latitude, longitude, elevation, epw_source, epw_path, tm_years)
VALUES
    ('419230', 'Dhaka', 23.728, 90.407, 6, 'EnergyPlus/SWERA', 'data/epw/Dhaka_419230.epw', ARRAY['2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021'])
ON CONFLICT (wmo_code) DO NOTHING;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rooms_project_id ON rooms(project_id);
CREATE INDEX IF NOT EXISTS idx_calc_results_project_id ON calculation_results(project_id);
CREATE INDEX IF NOT EXISTS idx_calc_results_module ON calculation_results(module_id);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();