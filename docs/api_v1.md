# API V1 References

## Table of Content

1. [Signup](#signup)
2. [Login](#login)
3. [Create Project](#create-project)

---

## Path Details

---

### Signup

- Summary: Create a new User
- Path: /signup
- Method: POST

---

#### RequestBody

- application/json

```json
{
	"email": "string",
	"password": "string",
	"phone_number": "string",
	"name": "string"
}
```

---

#### Responses

- 200 Success

`application/json`

```json
string
```

- 400 Bad Request

`application/json`

```json
string
```

- 401 Unauthorized

`application/json`

```json
string
```

- 409 Conflict

`application/json`

```json
string
```

- 500 Internal Server Error

`application/json`

```json
string
```

---

### Login

- Summary: Verify an account's credentials
- Path: /login
- Method: POST

---

#### RequestBody

- application/json

```json
{
	"email": "",
	"password": ""
}
```

---

#### Responses

- 200 Success

`application/json`

```json
string
```

- 400 Bad Request

`application/json`

```json
string
```

- 401 Unauthorized

`application/json`

```json
string
```

- 409 Conflict

`application/json`

```json
string
```

- 500 Internal Server Error

`application/json`

```json
string
```

---

### Create Project

- Summary: Create a new project
- Path: /projects
- Method: POST

---

#### RequestBody

- application/json

```json
{
	"name": "string"
}
```

---

#### Responses

- 200 Success

`application/json`

```json
{
	"id": "",
	"name": "",
	"created_at": ""
}
```

- 400 Bad Request

`application/json`

```json
string
```

- 401 Unauthorized

`application/json`

```json
string
```

- 409 Conflict

`application/json`

```json
string
```

- 500 Internal Server Error

`application/json`

```json
string
```

---
