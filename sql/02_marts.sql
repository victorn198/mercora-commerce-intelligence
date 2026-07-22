create or replace table mart_orders as
with item_totals as (
    select
        order_id,
        sum(price) as item_revenue,
        sum(freight_value) as freight_value,
        count(*) as item_lines,
        count(distinct product_id) as distinct_products,
        count(distinct seller_id) as distinct_sellers
    from fact_order_items
    group by order_id
),
payment_totals as (
    select
        order_id,
        sum(payment_value) as payment_value,
        max(payment_installments) as max_installments,
        string_agg(distinct payment_type, ', ' order by payment_type) as payment_types
    from fact_payments
    group by order_id
)
select
    o.*,
    coalesce(i.item_revenue, 0) as item_revenue,
    coalesce(i.freight_value, 0) as freight_value,
    coalesce(i.item_lines, 0) as item_lines,
    coalesce(i.distinct_products, 0) as distinct_products,
    coalesce(i.distinct_sellers, 0) as distinct_sellers,
    coalesce(p.payment_value, 0) as payment_value,
    p.max_installments,
    p.payment_types,
    r.review_score,
    r.review_count
from fact_orders o
left join item_totals i using(order_id)
left join payment_totals p using(order_id)
left join fact_reviews r using(order_id);

create or replace table mart_sales_lines as
select
    o.order_id,
    i.order_item_id,
    o.customer_key,
    o.customer_state,
    o.customer_city,
    o.order_status,
    o.purchase_date,
    o.purchased_at,
    o.is_delivered,
    o.is_cancelled,
    o.is_on_time,
    o.delivery_days,
    i.product_id,
    i.seller_id,
    i.category_pt,
    i.category_en,
    i.seller_state,
    i.seller_city,
    i.price as item_revenue,
    i.freight_value,
    r.review_score
from fact_order_items i
join fact_orders o using(order_id)
left join fact_reviews r using(order_id);

create or replace table mart_customer_orders as
select
    customer_key,
    order_id,
    purchase_date,
    item_revenue,
    freight_value,
    review_score,
    is_on_time,
    row_number() over(partition by customer_key order by purchased_at, order_id) as customer_order_number
from mart_orders
where not is_cancelled and purchase_date <= date '2018-08-31';

create or replace table mart_customers as
with customer_rollup as (
    select
        customer_key,
        min(purchase_date) as first_purchase_date,
        max(purchase_date) as last_purchase_date,
        count(distinct order_id) as lifetime_orders,
        sum(item_revenue) as lifetime_revenue,
        avg(review_score) as average_review,
        avg(case when is_on_time then 1.0 when is_on_time is false then 0.0 end) as on_time_rate,
        max(case when customer_order_number = 2 then purchase_date end) as second_purchase_date
    from mart_customer_orders
    group by customer_key
),
scored as (
    select
        c.*,
        date_diff('day', last_purchase_date, date '2018-08-31') as recency_days,
        date_diff('day', first_purchase_date, second_purchase_date) as days_to_second_purchase,
        ntile(5) over(order by date_diff('day', last_purchase_date, date '2018-08-31') desc) as r_score,
        ntile(5) over(order by lifetime_orders) as f_score,
        ntile(5) over(order by lifetime_revenue) as m_score
    from customer_rollup c
)
select
    s.*,
    d.customer_state,
    d.customer_city,
    case
        when r_score >= 4 and f_score >= 4 then 'Campeões'
        when r_score >= 3 and f_score >= 3 then 'Leais'
        when r_score >= 4 and f_score <= 2 then 'Novos'
        when r_score <= 2 and f_score >= 3 then 'Em risco'
        when r_score <= 2 and f_score <= 2 then 'Hibernando'
        else 'Potenciais'
    end as rfm_segment
from scored s
left join dim_customers d using(customer_key);

create or replace table mart_cohorts as
with customer_months as (
    select
        customer_key,
        date_trunc('month', min(purchase_date))::date as cohort_month
    from mart_customer_orders
    group by customer_key
),
activity as (
    select distinct
        o.customer_key,
        c.cohort_month,
        date_trunc('month', o.purchase_date)::date as activity_month
    from mart_customer_orders o
    join customer_months c using(customer_key)
),
cohort_size as (
    select cohort_month, count(*) as cohort_customers
    from customer_months
    group by cohort_month
)
select
    a.cohort_month,
    date_diff('month', a.cohort_month, a.activity_month) as month_number,
    count(distinct a.customer_key) as active_customers,
    s.cohort_customers,
    count(distinct a.customer_key)::double / s.cohort_customers as retention_rate
from activity a
join cohort_size s using(cohort_month)
group by a.cohort_month, month_number, s.cohort_customers;

