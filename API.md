## WaiterJobs API – HTTP contract for frontend

Base URL: http://localhost:8000

Auth
- Use header: Authorization: Bearer <access_token>
- Obtain tokens from /auth/login or during registration.

Tokens object (response)
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "timeout_token": "..."
}
```

### 1) Auth (via dynamic reports)
Notes:
- Some reports require Authorization. This is controlled by the `authorized_required` flag in `report_configuration`.
- Signup-related reports do not require Authorization (flag = 0).

- Register manager (basic): POST /reports/run
  - Body:
  ```json
  {
    "report_name": "user_register_manager_basic",
    "parameters": {
      "p_display_name": "Manager One",
      "p_email": "manager1@example.com",
      "p_password_hash": "<bcrypt-or-pbkdf2-hash>"
    }
  }
  ```

- Get user by email: POST /reports/run
  - Body:
  ```json
  { "report_name": "user_get_by_email", "parameters": { "p_email": "user@example.com" } }
  ```

- POST /auth/refresh
  - Body:
  ```json
  { "refresh_token": "<refresh_token>" }
  ```
  - Response: Tokens
  - Notes: Rotates tokens and sets the new access token; requires no Authorization header.

Notes: Passwords are stored with PBKDF2-SHA256. No 72-byte limit.

### 2) Waiters (via dynamic reports)

- Register waiter (full): POST /reports/run
  - Body:
  ```json
  {
    "report_name": "waiter_register_full",
    "parameters": {
      "p_display_name": "Waiter One",
      "p_email": "waiter1@example.com",
      "p_password_hash": "<hash>",
      "p_status": "pre_army",
      "p_about_me": "Friendly and fast.",
      "p_distance_km": 10,
      "p_min_hourly_wage": 40,
      "p_shifts_per_week": 4,
      "p_hours": ["morning"],
      "p_experience": ["waiter"],
      "p_people_say": ["good_vibe"],
      "p_skills": ["teamwork"],
      "p_looking_for": ["waiter"]
    }
  }
  ```

- Upsert waiter profile: POST /reports/run
  - Body:
  ```json
  {
    "report_name": "waiter_upsert_profile",
    "parameters": {
      "p_user_id": 123,
      "p_status": "post_army",
      "p_about_me": "Updated",
      "p_hours": ["morning","weekends"]
    }
  }
  ```

- DELETE /waiters/{user_id}
  - Response: { "ok": true }

- POST /waiters/{waiter_user_id}/like
  - Manager likes a waiter profile
  - Response:
  ```json
  { "liked": true, "mutual_match": false }
  ```

### 3) Businesses (via dynamic reports)

- Create business: POST /reports/run
  - Body:
  ```json
  {
    "report_name": "business_create",
    "parameters": {
      "p_name": "Cafe Luna", "p_location": "Tel Aviv", "p_business_type": "cafe",
      "p_menu_url": "https://example.com/menu.pdf",
      "p_images": ["https://.../cafe-1.jpg"],
      "p_manager_user_ids": [123,456]
    }
  }
  ```
  - Notes:
    - If `manager_user_ids` is omitted, the authenticated user is added as a manager.
    - `images` is an array of image URLs (Cloudinary). You can also upload files via a dedicated endpoint below.

- List my businesses: POST /reports/run
  - Body:
  ```json
  { "report_name": "business_list_by_manager", "parameters": { "p_manager_user_id": 123 } }
  ```

- Get a business: POST /reports/run
  - Body:
  ```json
  { "report_name": "business_get", "parameters": { "p_business_id": 1, "p_manager_user_id": 123 } }
  ```

- Update business: POST /reports/run
  - Body (partial updates via JSON):
  ```json
  {
    "report_name": "business_update",
    "parameters": {
      "p_business_id": 1,
      "p_manager_user_id": 123,
      "p_updates": { "name": "Cafe Luna Updated", "images": ["https://.../cafe-1.jpg"] }
    }
  }
  ```
  - Notes: Setting `images` here replaces the entire list. To append images, use the upload endpoint.

- POST /businesses/{business_id}/images
  - Description: Upload one or more images (multipart/form-data). Files are stored in Cloudinary; the resulting secure URLs are appended to `images`.
  - Request: multipart/form-data with field name `files` (can repeat or send multiple files)
  - Response: BusinessOut
  - Example (curl):
  ```bash
  curl -X POST \
    -H "Authorization: Bearer <access_token>" \
    -F "files=@/path/to/pic1.jpg" \
    -F "files=@/path/to/pic2.jpg" \
    http://localhost:8000/businesses/1/images
  ```

- Add manager by email: POST /reports/run
  - Body:
  ```json
  {
    "report_name": "business_add_manager_by_email",
    "parameters": { "p_business_id": 1, "p_requester_id": 123, "p_email": "manager2@example.com" }
  }
  ```

- DELETE /businesses/{business_id}
  - Response: { "ok": true }

### 4) Roles (via dynamic reports)

- Create role: POST /reports/run
  - Body:
  ```json
  {
    "report_name": "role_create",
    "parameters": {
      "p_business_id": 1,
      "p_position": "waiter",
      "p_payment_per_hour": 45,
      "p_location": "Tel Aviv",
      "p_latitude": 32.0853,
      "p_longitude": 34.7818,
      "p_when_need": "this_week",
      "p_experience_required": "no_experience",
      "p_shift_morning": true,
      "p_shift_evening": false,
      "p_shift_weekends": true,
      "p_shift_full_time": false,
      "p_shift_part_time": true,
      "p_about_job": "Friendly team",
      "p_min_hourly_wage": 40,
      "p_is_active": 1,
      "p_manager_user_id": 123
    }
  }
  ```

- Get role: POST /reports/run
  - Body:
  ```json
  { "report_name": "role_get", "parameters": { "p_role_id": 1 } }
  ```

- Update role: POST /reports/run
  - Body:
  ```json
  {
    "report_name": "role_update",
    "parameters": { "p_role_id": 1, "p_manager_user_id": 123, "p_updates": { "position": "bartender" } }
  }
  ```

- Delete role: POST /reports/run
  - Body:
  ```json
  { "report_name": "role_delete", "parameters": { "p_role_id": 1, "p_manager_user_id": 123 } }
  ```

- Like role: POST /reports/run
  - Body:
  ```json
  { "report_name": "role_like", "parameters": { "p_role_id": 1, "p_user_id": 456 } }
  ```

### 5) Notifications (via dynamic reports)

- List: POST /reports/run
  - Body: `{ "report_name": "notifications_list", "parameters": { "p_user_id": 123 } }`

- Create: POST /reports/run
  - Body: `{ "report_name": "notifications_create", "parameters": { "p_user_id": 123, "p_type": "new_message", "p_payload": {"text":"hi"} } }`

- Mark read: POST /reports/run
  - Body: `{ "report_name": "notification_mark_read", "parameters": { "p_notification_id": 1, "p_user_id": 123 } }`

- Delete: POST /reports/run
  - Body: `{ "report_name": "notification_delete", "parameters": { "p_notification_id": 1, "p_user_id": 123 } }`

### 6) Reports

- POST /reports/run
  - Body:
  ```json
  {
    "report_name": "roles_by_position",
    "parameters": { "p_position": "waiter" }
  }
  ```
  - Response:
  ```json
  {
    "report_name": "roles_by_position",
    "rows": [ { "id": 1, "position": "waiter", "business_name": "Cafe Luna" } ]
  }
  ```

### 7) Chat (via dynamic reports)

- Create conversation: POST /reports/run
  - Body: `{ "report_name": "chat_create_conversation", "parameters": { "p_initiator_user_id": 123, "p_participant_user_ids": [456] } }`

- List conversations: POST /reports/run
  - Body: `{ "report_name": "chat_list_conversations", "parameters": { "p_user_id": 123 } }`

- Post message: POST /reports/run
  - Body: `{ "report_name": "chat_post_message", "parameters": { "p_conversation_id": 99, "p_sender_user_id": 123, "p_body": "Hello!" } }`

- List messages: POST /reports/run
  - Body: `{ "report_name": "chat_list_messages", "parameters": { "p_conversation_id": 99, "p_user_id": 123 } }`

- Mark message read: POST /reports/run
  - Body: `{ "report_name": "chat_mark_message_read", "parameters": { "p_message_id": 1, "p_user_id": 123 } }`

### Enumerations (allowed values)
- waiter status: pre_army | post_army | student | other
- looking_for: waiter | bartender | barista | hostess | shift_manager | manager
- hours: part_time | full_time | morning | evening | weekends
- experience: waiter | barman | barista | shift_manager | host
- people_say: best_coffee_maker | good_vibe | best_cocktails | customers_love_me
- skills: customer_service | basic_computer | coffee_making | teamwork | food_service | working_under_pressure | table_management
- business_type: bar | restaurant | cafe | hotel
- role position: waiter | bartender | barista | hostess | shift_manager
- when_need: this_week | always_looking
- experience_required: no_experience | some_experience | experience_only
- notification type: upcoming_interview | new_match | business_liked_you | interview_succeeded | arriving_for_shift | new_message

### Notes
- All protected routes require Authorization header.
- Likes create a mutual_match=true when both sides liked each other; notifications are generated automatically.
- Reports require the report configuration to exist in table `report_configuration`.


