-- 1. Count total customers
-- Table: customers
SELECT COUNT(*) AS total_customers
FROM customers;

-- 2. Count total sellers
-- Table: sellers
SELECT COUNT(*) AS total_sellers
FROM sellers;

-- 3. Count total orders
-- Table: orders
SELECT COUNT(*) AS total_orders
FROM orders;

-- 4. Count total products
-- Table: products
SELECT COUNT(*) AS total_products
FROM products;

-- 5. Top 10 most ordered products
-- Tables: order_items, products
SELECT p.product_id, COUNT(oi.order_id) AS order_count
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY order_count DESC
LIMIT 10;

-- 6. Top 10 sellers by number of orders
-- Table: order_items
SELECT oi.seller_id, COUNT(oi.order_id) AS total_orders
FROM order_items oi
GROUP BY oi.seller_id
ORDER BY total_orders DESC
LIMIT 10;

-- 7. Total orders per customer (top 10)
-- Table: orders
SELECT customer_id, COUNT(order_id) AS total_orders
FROM orders
GROUP BY customer_id
ORDER BY total_orders DESC
LIMIT 10;

-- 8. Total order items
-- Table: order_items
SELECT COUNT(*) AS total_order_items
FROM order_items;
