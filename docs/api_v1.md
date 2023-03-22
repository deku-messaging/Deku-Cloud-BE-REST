# API V1 References

## Table of Content

1. [Users](#users)
   1. [Create a user](#create-a-user)
   2. [Authenticate](#authentication)
   3. [Get user](#get-user)
2. [Projects](#projects)
   1. [Create a project](#create-a-project)
3. [Publications](#publications)
   1. [Publish](#publish)

---

## Users

---

User management resources.

### Create a user

Create a new user's account on the deku cloud server.

```
POST /signup
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

_**Body**_

| Attribute      | Type   | Required | Description                                         |
| :------------- | :----- | :------- | :-------------------------------------------------- |
| `email`        | string | Yes      | An active email address for account identification. |
| `password`     | string | Yes      | A a word, phrase, or string for account security.   |
| `phone_number` | string | No       | An active phone number for extra account security.  |
| `name`         | string | No       | A name for account personalization.                 |

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/signup' --header 'Content-Type: application/json' --data-raw '{"email": "", "password": "", "name": "", "phone_number": ""}'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json

```

> [400] Bad Request

Raised when some attributes are omitted or the request isn't structured
correctly.

> [401] Unauthorized

Raised when the request lacks valid authentication credentials for the requested
resource.

> [409] Conflict

Raised when the requested resource already exist and cannot be duplicated.

> [500] Internal Server Error

Raised when the server encountered an unexpected condition that prevented it
from fulfilling the request.

### Authentication

Login to an existing user's account.

```
POST /login
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

_**Body**_

| Attribute  | Type   | Required | Description                                         |
| :--------- | :----- | :------- | :-------------------------------------------------- |
| `email`    | string | Yes      | An active email address for account identification. |
| `password` | string | Yes      | A a word, phrase, or string for account security.   |

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/login' --header 'Content-Type: application/json' --data-raw '{"email": "", "password": ""}'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json
{
	"account_sid": "",
	"auth_token": ""
}
```

> [400] Bad Request

Raised when some attributes are omitted or the request isn't structured
correctly.

> [401] Unauthorized

Raised when the request lacks valid authentication credentials for the requested
resource.

> [500] Internal Server Error

Raised when the server encountered an unexpected condition that prevented it
from fulfilling the request.

### Get User

> _**[Authentication](#authentication) Required**_

Details of the currently authenticated user.

```
GET /
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/' --header 'Content-Type: application/json'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json
{
	"account_sid": "",
	"auth_token": "",
	"created_at": "",
	"email": "",
	"id": "",
	"name": "",
	"phone_number": "",
	"twilio_account_sid": "",
	"twilio_auth_token": "",
	"twilio_service_sid": ""
}
```

> [400] Bad Request

Raised when some attributes are omitted or the request isn't structured
correctly.

> [401] Unauthorized

Raised when the request lacks valid authentication credentials for the requested
resource.

> [500] Internal Server Error

Raised when the server encountered an unexpected condition that prevented it
from fulfilling the request.

### Update User

> _**[Authentication](#authentication) Required**_

Update currently authenticated user's account.

```
PUT /
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

_**Body**_

| Attribute            | Type   | Required | Description                                                                                            |
| :------------------- | :----- | :------- | :----------------------------------------------------------------------------------------------------- |
| `name`               | string | No       | A name for account personalization.                                                                    |
| `phone_number`       | string | No       | An active phone number for extra account security.                                                     |
| `twilio_account_sid` | string | No       | [Twilio account_sid](https://www.twilio.com/blog/better-twilio-authentication-csharp-twilio-api-keys). |
| `twilio_auth_token`  | string | No       | [Twilio auth_token](https://www.twilio.com/blog/better-twilio-authentication-csharp-twilio-api-keys).  |
| `twilio_service_sid` | string | No       | [Twilio messaging service_sid](https://www.twilio.com/docs/glossary/what-is-a-sid)                     |

```shell
curl --location --request PUT 'https://staging.smswithoutborders.com:12000/v1/' --header 'Content-Type: application/json' --data-raw '{"name": "", "phone_number": "", "twilio_account_sid": "", "twilio_auth_token": "", "twilio_service_sid": ""}'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json
{
	"account_sid": "",
	"auth_token": "",
	"created_at": "",
	"email": "",
	"id": "",
	"name": "",
	"phone_number": "",
	"twilio_account_sid": "",
	"twilio_auth_token": "",
	"twilio_service_sid": ""
}
```

> [400] Bad Request

Raised when some attributes are omitted or the request isn't structured
correctly.

> [401] Unauthorized

Raised when the request lacks valid authentication credentials for the requested
resource.

> [409] Conflict

Raised when the requested resource already exist and cannot be duplicated.

> [500] Internal Server Error

Raised when the server encountered an unexpected condition that prevented it
from fulfilling the request.

## Projects

---

Project management resources.

### Create a project

> _**[Authentication](#authentication) Required**_

Create a new project for an existing user on the deku server.

```
POST /projects
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

_**Body**_

| Attribute | Type   | Required | Description          |
| :-------- | :----- | :------- | :------------------- |
| `name`    | string | Yes      | Unique project name. |

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/projects' --header 'Content-Type: application/json' --data-raw '{"name": ""}'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json
{
	"id": "",
	"name": "",
	"created_at": ""
}
```

> [400] Bad Request

Raised when some attributes are omitted or the request isn't structured
correctly.

> [401] Unauthorized

Raised when the request lacks valid authentication credentials for the requested
resource.

> [409] Conflict

Raised when the requested resource already exist and cannot be duplicated.

> [500] Internal Server Error

Raised when the server encountered an unexpected condition that prevented it
from fulfilling the request.

## Publications

Publication management resources.

### Publish

Make a request to deku server to publish.

```
POST /projects/:project_id/services/:service
```

_**Headers**_

| Attribute       | Value                                                 | Required | Description                                                                                                              |
| :-------------- | :---------------------------------------------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type`  | application/json                                      | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |
| `Authorization` | Basic _**Base64 encoded account_sid and auth_token**_ | Yes      | Used to provide credentials that authenticate a user with a server.                                                      |

_**Params**_

| Attribute    | Type   | Required | Description                                 |
| :----------- | :----- | :------- | :------------------------------------------ |
| `project_id` | string | Yes      | A unique string used to identify a project. |
| `service`    | string | Yes      | a Deku service.                             |

_**Body**_

| Attribute | Type   | Required | Description                          |
| :-------- | :----- | :------- | :----------------------------------- |
| `body`    | string | Yes      | Content to be sent via deku service. |
| `to`      | string | Yes      | Recipient.                           |

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/projects/:project_id/services/:service' --header 'Content-Type: application/json' --user "account_sid:auth_token" --data-raw '{"body": "", "to": ""}'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json
{
	"sid": "",
	"created_at": "",
	"direction": "",
	"status": "",
	"from": "",
	"to": "",
	"channel": "",
	"body": "",
	"reason": ""
}
```

> [400] Bad Request

Raised when some attributes are omitted or the request isn't structured
correctly.

> [401] Unauthorized

Raised when the request lacks valid authentication credentials for the requested
resource.

> [500] Internal Server Error

Raised when the server encountered an unexpected condition that prevented it
from fulfilling the request.
