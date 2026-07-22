create or replace table raw_customers as
select * from read_csv_auto('{{RAW_DIR}}/olist_customers_dataset.csv', header=true);

create or replace table raw_orders as
select * from read_csv_auto('{{RAW_DIR}}/olist_orders_dataset.csv', header=true);

create or replace table raw_items as
select * from read_csv_auto('{{RAW_DIR}}/olist_order_items_dataset.csv', header=true);

create or replace table raw_payments as
select * from read_csv_auto('{{RAW_DIR}}/olist_order_payments_dataset.csv', header=true);

create or replace table raw_reviews as
select * from read_csv_auto('{{RAW_DIR}}/olist_order_reviews_dataset.csv', header=true);

create or replace table raw_products as
select * from read_csv_auto('{{RAW_DIR}}/olist_products_dataset.csv', header=true);

create or replace table raw_sellers as
select * from read_csv_auto('{{RAW_DIR}}/olist_sellers_dataset.csv', header=true);

create or replace table raw_category_translation as
select * from read_csv_auto('{{RAW_DIR}}/product_category_name_translation.csv', header=true);

create or replace table raw_geolocation as
select * from read_csv_auto('{{RAW_DIR}}/olist_geolocation_dataset.csv', header=true);

create or replace table dim_products as
select
    p.product_id,
    coalesce(nullif(p.product_category_name, ''), 'sem_categoria') as category_pt,
    coalesce(t.product_category_name_english, 'uncategorized') as category_en,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
from raw_products p
left join raw_category_translation t using(product_category_name);

create or replace table dim_sellers as
select
    seller_id,
    seller_city,
    seller_state,
    seller_zip_code_prefix
from raw_sellers;

create or replace table dim_customers as
select
    substr(sha256(customer_unique_id), 1, 12) as customer_key,
    any_value(customer_city) as customer_city,
    any_value(customer_state) as customer_state,
    any_value(customer_zip_code_prefix) as customer_zip_code_prefix
from raw_customers
group by customer_unique_id;

create or replace table dim_geography as
select
    geolocation_zip_code_prefix as zip_code_prefix,
    any_value(geolocation_city) as city,
    any_value(geolocation_state) as state,
    avg(geolocation_lat) as latitude,
    avg(geolocation_lng) as longitude
from raw_geolocation
group by geolocation_zip_code_prefix;

create or replace table fact_orders as
select
    o.order_id,
    substr(sha256(c.customer_unique_id), 1, 12) as customer_key,
    c.customer_state,
    c.customer_city,
    o.order_status,
    cast(o.order_purchase_timestamp as timestamp) as purchased_at,
    cast(o.order_purchase_timestamp as date) as purchase_date,
    cast(o.order_approved_at as timestamp) as approved_at,
    cast(o.order_delivered_carrier_date as timestamp) as carrier_at,
    cast(o.order_delivered_customer_date as timestamp) as delivered_at,
    cast(o.order_estimated_delivery_date as timestamp) as estimated_delivery_at,
    o.order_status = 'delivered' as is_delivered,
    o.order_status in ('canceled', 'unavailable') as is_cancelled,
    case
        when o.order_delivered_customer_date is null then null
        else cast(o.order_delivered_customer_date as timestamp) <= cast(o.order_estimated_delivery_date as timestamp)
    end as is_on_time,
    date_diff('day', cast(o.order_purchase_timestamp as timestamp), cast(o.order_delivered_customer_date as timestamp)) as delivery_days
from raw_orders o
join raw_customers c using(customer_id);

create or replace table fact_order_items as
select
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    cast(i.shipping_limit_date as timestamp) as shipping_limit_at,
    cast(i.price as double) as price,
    cast(i.freight_value as double) as freight_value,
    p.category_pt,
    p.category_en,
    s.seller_state,
    s.seller_city
from raw_items i
left join dim_products p using(product_id)
left join dim_sellers s using(seller_id);

create or replace table fact_payments as
select
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    cast(payment_value as double) as payment_value
from raw_payments;

create or replace table fact_reviews as
select
    order_id,
    avg(review_score) as review_score,
    count(*) as review_count,
    max(review_creation_date) as review_created_at
from raw_reviews
group by order_id;

create or replace table dim_date as
select
    cast(day as date) as date,
    year(day) as year,
    quarter(day) as quarter,
    month(day) as month,
    strftime(day, '%Y-%m') as year_month,
    dayofweek(day) as weekday_number,
    strftime(day, '%A') as weekday_name
from generate_series(date '2016-09-01', date '2018-10-31', interval 1 day) dates(day);

