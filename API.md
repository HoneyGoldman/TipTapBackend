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

### 1) Auth

- POST /auth/register-manager
  - Body:
  ```json
  {
    "display_name": "Manager One",
    "email": "manager1@example.com",
    "password": "Passw0rd!",
    "business_name": "Cafe Luna",
    "business_location": "Tel Aviv",
    "business_type": "cafe",
    "menu_url": "https://example.com/menu.pdf"
  }
  ```
  - Response: Tokens

- POST /auth/register
  - Creates a basic waiter account; minimal payload same as login request
  - Body:
  ```json
  {
    "email": "waiter1@example.com",
    "password": "Passw0rd!"
  }
  ```
  - Response: Tokens

- POST /auth/login
  - Body:
  ```json
  {
    "email": "manager1@example.com",
    "password": "Passw0rd!"
  }
  ```
  - Response: Tokens

Notes: Passwords are stored with PBKDF2-SHA256. No 72-byte limit.

### 2) Waiters

All endpoints require Authorization header.

- POST /waiters
  - Body (WaiterCreate):
  ```json
  {
    "display_name": "Waiter One",
    "email": "waiter1@example.com",
    "password": "Passw0rd!",
    "status": "pre_army",
    "looking_for": ["waiter", "bartender"],
    "about_me": "Friendly and fast.",
    "distance_km": 10,
    "min_hourly_wage": 40,
    "shifts_per_week": 4,
    "hours": ["morning", "weekends"],
    "experience": ["waiter"],
    "people_say": ["good_vibe"],
    "skills": ["customer_service", "teamwork"]
  }
  ```
  - Response (WaiterOut): waiter profile with all lists

- GET /waiters/{user_id}
  - Response: WaiterOut

- PUT /waiters/{user_id}
  - Body (any subset):
  ```json
  {
    "display_name": "Updated Name",
    "about_me": "Updated bio",
    "looking_for": ["waiter", "barista"],
    "hours": ["morning"],
    "experience": ["waiter"],
    "people_say": ["good_vibe"],
    "skills": ["teamwork"]
  }
  ```
  - Response: WaiterOut

- DELETE /waiters/{user_id}
  - Response: { "ok": true }

- POST /waiters/{waiter_user_id}/like
  - Manager likes a waiter profile
  - Response:
  ```json
  { "liked": true, "mutual_match": false }
  ```

### 3) Businesses (manager only)

- POST /businesses
  - Body:
  ```json
  { "name": "Cafe Luna", "location": "Tel Aviv", "business_type": "cafe", "menu_url": "https://example.com/menu.pdf" }
  ```
  - Response:
  ```json
  { "id": 1, "manager_user_id": 123, "name": "Cafe Luna", "location": "Tel Aviv", "business_type": "cafe", "menu_url": "https://example.com/menu.pdf" }
  ```

- GET /businesses
  - Response: [BusinessOut]

- GET /businesses/{business_id}
  - Response: BusinessOut

- PUT /businesses/{business_id}
  - Body: partial update fields (name, location, business_type, menu_url)
  - Response: BusinessOut

- DELETE /businesses/{business_id}
  - Response: { "ok": true }

### 4) Roles (job postings)

- POST /roles (manager)
  - Body:
  ```json
  {
    "business_id": 1,
    "position": "waiter",
    "payment_per_hour": 45,
    "location": "Tel Aviv",
    "when_need": "this_week",
    "experience_required": "no_experience",
    "shift_morning": true,
    "shift_evening": false,
    "shift_weekends": true,
    "shift_full_time": false,
    "shift_part_time": true,
    "about_job": "Friendly team"
  }
  ```
  - Response: RoleOut

- GET /roles (public)
  - Response: [RoleOut] for active roles

- GET /roles/{role_id} (public)
  - Response: RoleOut

- PUT /roles/{role_id} (manager who owns the business)
  - Body: RoleUpdate (any subset of fields)
  - Response: RoleOut

- DELETE /roles/{role_id} (manager who owns the business)
  - Response: { "ok": true }

- POST /roles/{role_id}/like (waiter)
  - Response:
  ```json
  { "liked": true, "mutual_match": false }
  ```

### 5) Notifications

- GET /notifications
  - Response: [NotificationOut]

- POST /notifications
  - Body:
  ```json
  { "user_id": 123, "type": "new_message", "payload": {"text": "hi"} }
  ```
  - Response: NotificationOut

- POST /notifications/{notification_id}/read
  - Response: { "ok": true }

- DELETE /notifications/{notification_id}
  - Response: { "ok": true }

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

### 7) Chat (optional)

- POST /chat/conversations
  - Body:
  ```json
  { "participant_user_ids": [456] }
  ```
  - Response:
  ```json
  { "id": 99, "participant_user_ids": [123, 456] }
  ```

- GET /chat/conversations
  - Response: [ { "id": 99, "participant_user_ids": [123,456] } ]

- POST /chat/messages
  - Body:
  ```json
  { "conversation_id": 99, "body": "Hello!" }
  ```
  - Response (MessageOut): id, conversation_id, sender_user_id, body, created_at, read_at

- GET /chat/messages?conversation_id={id}
  - Response: [MessageOut]

- POST /chat/messages/{message_id}/read
  - Response: { "ok": true }

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


