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

- POST /auth/register-manager-basic
  - Body:
  ```json
  {
    "display_name": "Manager One",
    "email": "manager1@example.com",
    "password": "Passw0rd!"
  }
  ```
  - Response: Tokens
  - Notes: Creates a manager account only (no business). You can add the user as a manager to an existing business later via `POST /businesses/{business_id}/managers`.

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

- POST /auth/refresh
  - Body:
  ```json
  { "refresh_token": "<refresh_token>" }
  ```
  - Response: Tokens
  - Notes: Rotates tokens and sets the new access token; requires no Authorization header.

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

- PUT /waiters/me
  - Description: Upsert current user's waiter profile. Creates the profile if it doesn't exist.
  - Body (any subset of WaiterUpdate):
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
  - Notes: Requires Authorization header.

- PUT /waiters/{user_id}
  - Description: Upsert waiter profile by user id. Creates the profile if it doesn't exist.
  - Body (any subset of WaiterUpdate):
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
  {
    "name": "Cafe Luna",
    "location": "Tel Aviv",
    "business_type": "cafe",
    "menu_url": "https://example.com/menu.pdf",
    "images": [
      "https://res.cloudinary.com/<cloud>/image/upload/v1699999999/cafe-1.jpg"
    ],
    "manager_user_ids": [123, 456]
  }
  ```
  - Response:
  ```json
  {
    "id": 1,
    "manager_user_ids": [123, 456],
    "name": "Cafe Luna",
    "location": "Tel Aviv",
    "business_type": "cafe",
    "menu_url": "https://example.com/menu.pdf",
    "images": [
      "https://res.cloudinary.com/<cloud>/image/upload/v1699999999/cafe-1.jpg"
    ]
  }
  ```
  - Notes:
    - If `manager_user_ids` is omitted, the authenticated user is added as a manager.
    - `images` is an array of image URLs (Cloudinary). You can also upload files via a dedicated endpoint below.

- GET /businesses
  - Response: [BusinessOut]

- GET /businesses/{business_id}
  - Response: BusinessOut

- PUT /businesses/{business_id}
  - Body (any subset):
  ```json
  {
    "name": "Cafe Luna Updated",
    "location": "Herzliya",
    "business_type": "cafe",
    "menu_url": "https://example.com/menu-v2.pdf",
    "images": [
      "https://res.cloudinary.com/<cloud>/image/upload/v1699999999/cafe-1.jpg",
      "https://res.cloudinary.com/<cloud>/image/upload/v1699999999/cafe-2.jpg"
    ]
  }
  ```
  - Response: BusinessOut
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

- POST /businesses/{business_id}/managers
  - Description: Add an existing business manager to the business by email.
  - Body:
  ```json
  { "email": "manager2@example.com" }
  ```
  - Response: BusinessOut (with updated `manager_user_ids`)
  - Notes:
    - Only a current manager of the business can add another manager.
    - The target user must exist and have `user_type` = `business_manager`.
    - Phone-based add is not yet supported and returns 400 if provided.
  - Example (curl):
  ```bash
  curl -X POST \
    -H "Authorization: Bearer <access_token>" \
    -H "Content-Type: application/json" \
    -d '{"email":"manager2@example.com"}' \
    http://localhost:8000/businesses/1/managers
  ```

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
    "latitude": 32.0853,
    "longitude": 34.7818,
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

- GET /roles (auth)
  - Description: Returns active roles the current user has not liked yet
  - Response: [RoleOut]

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


