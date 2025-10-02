## Reports Catalog

This document lists available reports and their parameters for the dynamic reports API.

Base endpoint: POST /reports/run (Authorization: Bearer <access_token>)

Request body shape:
```json
{
  "report_name": "...",
  "parameters": { "param": "value", "...": "..." }
}
```

### 1) roles_by_position
- Procedure: sp_roles_by_position
- Parameters (order matters):
  - p_position (string, mandatory)

Example request:
```json
{
  "report_name": "roles_by_position",
  "parameters": { "p_position": "waiter" }
}
```

### 2) unswiped_roles_nearby
### 3) user_get_by_email
- Procedure: sp_user_get_by_email
- Params: p_email (string)

Example:
```json
{ "report_name": "user_get_by_email", "parameters": { "p_email": "user@example.com" } }
```

### 4) user_register_manager_basic
- Procedure: sp_user_register_manager_basic
- Params: p_display_name (string), p_email (string), p_password_hash (string)

### 5) waiter_register_full
- Procedure: sp_waiter_register_full
- Params: p_display_name, p_email, p_password_hash, p_status, p_about_me, p_distance_km, p_min_hourly_wage, p_shifts_per_week, p_hours (json array), p_experience (json array), p_people_say (json array), p_skills (json array), p_looking_for (json array)

### 6) waiter_upsert_profile
- Procedure: sp_waiter_upsert_profile
- Params: p_user_id, p_status, p_about_me, p_distance_km, p_min_hourly_wage, p_shifts_per_week, p_hours (json array), p_experience (json array), p_people_say (json array), p_skills (json array), p_looking_for (json array)

### 7) business_create
- Procedure: sp_business_create
- Params: p_name, p_location, p_business_type, p_menu_url, p_images (json array), p_manager_user_ids (json array of ints)

### 8) business_list_by_manager
- Procedure: sp_business_list_by_manager
- Params: p_manager_user_id

### 9) business_get
- Procedure: sp_business_get
- Params: p_business_id, p_manager_user_id

### 10) business_update
- Procedure: sp_business_update
- Params: p_business_id, p_manager_user_id, p_updates (json object)

### 11) business_delete
- Procedure: sp_business_delete
- Params: p_business_id, p_manager_user_id

### 12) business_add_manager_by_email
- Procedure: sp_business_add_manager_by_email
- Params: p_business_id, p_requester_id, p_email

- Procedure: sp_unswiped_roles_nearby
- Parameters (order matters):
  - p_user_id (number, mandatory)
  - p_lat (number, mandatory)
  - p_lng (number, mandatory)
  - p_distance_km (number, optional; null or <= 0 to return all distances)

Example request:
```json
{
  "report_name": "unswiped_roles_nearby",
  "parameters": {
    "p_user_id": 123,
    "p_lat": 32.0853,
    "p_lng": 34.7818,
    "p_distance_km": 10
  }
}
```


