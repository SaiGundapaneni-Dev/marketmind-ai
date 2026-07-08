# API Documentation

## GET /portfolio/

Returns the user's portfolio summary and holdings.

### Response

- total_cost
- total_value
- total_profit
- total_return_percent
- holdings

Each holding includes:

- asset_type
- symbol
- name
- quantity
- average_price
- current_price
- cost
- current_value
- profit
- profit_percent