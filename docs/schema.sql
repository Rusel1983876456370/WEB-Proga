CREATE INDEX ix_parts_category_id ON parts (category_id);

CREATE TABLE categories (
	id INTEGER NOT NULL, 
	name VARCHAR(60) NOT NULL, 
	slug VARCHAR(30) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_category_name CHECK (length(trim(name)) BETWEEN 1 AND 60), 
	CONSTRAINT ck_category_slug CHECK (length(trim(slug)) BETWEEN 1 AND 30), 
	UNIQUE (name), 
	UNIQUE (slug)
);

CREATE TABLE parts (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
	name VARCHAR(60) NOT NULL, 
	description TEXT NOT NULL, 
	article VARCHAR(20) NOT NULL, 
	price NUMERIC(10, 2) NOT NULL, 
	category_id INTEGER NOT NULL, 
	parameter VARCHAR(120) NOT NULL, 
	image_url VARCHAR(100) NOT NULL, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT ck_part_name CHECK (length(trim(name)) BETWEEN 3 AND 60), 
	CONSTRAINT ck_part_description CHECK (length(trim(description)) BETWEEN 10 AND 240), 
	CONSTRAINT ck_part_article CHECK (length(trim(article)) BETWEEN 4 AND 20 AND article = upper(article)), 
	CONSTRAINT ck_part_price CHECK (price >= 1 AND price <= 1000000 AND abs(price * 100 - round(price * 100)) < 0.00001), 
	CONSTRAINT ck_part_parameter CHECK (length(parameter) <= 120), 
	CONSTRAINT ck_part_image CHECK (image_url IN ('/assets/images/filter.svg', '/assets/images/brake.svg', '/assets/images/plug.svg', '/assets/images/air.svg', '/assets/images/shock.svg', '/assets/images/belt.svg')), 
	UNIQUE (article), 
	FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE RESTRICT
);

CREATE TABLE sqlite_sequence(name,seq);
