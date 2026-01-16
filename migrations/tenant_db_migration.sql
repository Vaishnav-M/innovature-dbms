-- Tenant Database Migration Script
-- This script creates the schema for tenant databases (one per company)
-- Each tenant database stores products isolated from other companies

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(280) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) DEFAULT 0.00 NOT NULL,
    cost_price DECIMAL(10, 2),
    sku VARCHAR(100),
    quantity INTEGER DEFAULT 0 NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    is_featured BOOLEAN DEFAULT FALSE NOT NULL,
    meta_title VARCHAR(255),
    meta_description TEXT,
    created_by TEXT,
    updated_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_is_featured ON products(is_featured);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);

-- Product Images table
CREATE TABLE IF NOT EXISTS product_images (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image VARCHAR(255) NOT NULL,
    alt_text VARCHAR(255),
    is_primary BOOLEAN DEFAULT FALSE NOT NULL,
    sort_order INTEGER DEFAULT 0 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_product_images_product_id ON product_images(product_id);
CREATE INDEX IF NOT EXISTS idx_product_images_is_primary ON product_images(is_primary);
CREATE INDEX IF NOT EXISTS idx_product_images_sort_order ON product_images(sort_order);

-- Sample product data for testing
-- Uncomment to insert test data

-- INSERT INTO products (id, name, slug, description, price, quantity, status, is_featured) VALUES
--     ('aaaa1111-1111-1111-1111-111111111111', 'Wireless Keyboard', 'wireless-keyboard', 'Ergonomic wireless keyboard with backlit keys', 79.99, 150, 'active', TRUE),
--     ('aaaa2222-2222-2222-2222-222222222222', 'USB-C Hub', 'usb-c-hub', '7-in-1 USB-C hub with HDMI and card reader', 49.99, 200, 'active', FALSE),
--     ('aaaa3333-3333-3333-3333-333333333333', 'Wireless Mouse', 'wireless-mouse', 'Silent click wireless mouse with 3-year battery', 39.99, 300, 'active', TRUE);
