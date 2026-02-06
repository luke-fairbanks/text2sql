### Response that did worked:

### Response that did NOT work:

Question: What are the three most ordered menu items, and how many times has each been ordered?

``` sql
Generated SQL: SELECT item_id, name, COUNT(item_id) AS order_count
FROM order_item
JOIN menu_item ON order_item.item_id = menu_item.item_id
GROUP BY item_id, name
ORDER BY order_count DESC
LIMIT 3;
```

### Other Example Questions:

1.
Question: How much total revenue has the restaurant made from closed orders?

Generated SQL:
``` sql
SELECT SUM(amount) AS total_revenue
FROM payment
INNER JOIN restaurant_order ON payment.order_id = restaurant_order.order_id
WHERE restaurant_order.status = 'Closed';
```
Response: _Hey there! The total revenue from closed orders is $90.25. It looks like the restaurant has made a decent amount from those completed orders. If you have any more questions or need further assistance, feel free to ask!_

2.
Question: Enter your question: Which customer has earned the most loyalty points, and how many do they have?
Generated SQL:
``` sql
SELECT customer_id, name, loyalty_points
FROM customer
ORDER BY loyalty_points DESC
LIMIT 1;
```

Response: _Hey there! 🍽️ It looks like Mia Patel is our most loyal customer, with a whopping 300 loyalty points! Mia's definitely racking up those points. Keep up the great work, Mia! If you need anything else, just let me know!_

Response: _An error occurred: column reference "item_id" is ambiguous
LINE 1: SELECT item_id, name, COUNT(item_id) AS order_count_

3.
Question: Which server handled the most dine-in orders in February 2026?

Generated SQL:
```sql
SELECT staff_id, COUNT(*) AS num_dinein_orders
FROM restaurant_order
WHERE order_type = 'DineIn' AND order_time >= '2026-02-01' AND order_time < '2026-03-01'
GROUP BY staff_id
ORDER BY num_dinein_orders DESC
LIMIT 1;
```

Response _Hey there! It looks like in February 2026, the server with the ID S001 handled the most dine-in orders, with a total of 2 orders. Good job, S001! If you need more info or have any other questions, feel free to ask!_
