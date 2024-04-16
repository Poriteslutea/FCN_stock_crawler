CREATE TABLE member (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(100) NOT NULL 
);

CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    code VARCHAR(30),
    start_date DATE NOT NULL,
    start_trace_date DATE NOT NULL,
    end_date DATE NOT NULL,
    ko_limit FLOAT NOT NULL,
    ki_limit FLOAT NOT NULL,
    price_type VARCHAR(30) NOT NULL DEFAULT 'close'
);

CREATE TABLE stock (
    id SERIAL PRIMARY KEY,
    code VARCHAR(30) NOT NULL
);

CREATE TABLE daily_report (
    id SERIAL PRIMARY KEY,
    product_id_fk INT REFERENCES product(id),
    stock_id_fk INT REFERENCES stock(id),
    date DATE,
    close NUMERIC(10, 2),
    ko_base NUMERIC(10, 2),
    ki_base NUMERIC(10, 2),
    ko_diff NUMERIC(10, 2),
    ki_diff NUMERIC(10, 2),
    is_ko BOOLEAN,
    is_ki BOOLEAN 
);

CREATE TABLE member_product (
    member_id INT REFERENCES member(id),
    product_id INT REFERENCES product(id),
    PRIMARY KEY (member_id, product_id)
);

CREATE TABLE product_stock (
    product_id INT REFERENCES product(id),
    stock_id INT REFERENCES stock(id),
    PRIMARY KEY (product_id, stock_id)
);
