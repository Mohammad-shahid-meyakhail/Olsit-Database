-- 1. Pie chart: Distribution of orders by payment type
SELECT p.payment_type, COUNT(*) AS total_orders
FROM orders o
LEFT JOIN payments p ON o.order_id = p.order_id
GROUP BY p.payment_type;

-- 2. Bar chart: Number of products per category
SELECT pc.product_category_name, COUNT(*) AS total_products
FROM products pr
RIGHT JOIN product_category_name_translation pc
  ON pr.product_category_name = pc.product_category_name
GROUP BY pc.product_category_name;

-- 3. Horizontal bar chart: Sellers and their total sales
SELECT s.seller_id, SUM(oi.price) AS total_sales
FROM order_items oi
LEFT JOIN sellers s ON oi.seller_id = s.seller_id
GROUP BY s.seller_id
ORDER BY total_sales DESC
LIMIT 10;

-- 4. Line chart: Monthly number of orders
SELECT DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
       COUNT(*) AS total_orders
FROM orders o
-- no join here, so nothing to change
GROUP BY month
ORDER BY month;

-- 5. Histogram: Distribution of product prices
SELECT oi.price
FROM order_items oi;
-- no join here, so nothing to change

-- 6. Scatter plot: Shipping days vs product price
SELECT (o.order_delivered_customer_date - o.order_purchase_timestamp) AS shipping_days,
       oi.price
FROM orders o
RIGHT JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_delivered_customer_date IS NOT NULL;
