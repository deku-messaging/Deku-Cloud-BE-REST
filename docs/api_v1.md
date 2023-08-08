# API V1 References

## Table of Content

1. [Users](#users)
   1. [Create a user](#create-a-user)
   2. [Authenticate](#authentication)
   3. [Get user](#get-user)
   4. [Update user](#update-user)
   5. [Delete user](#delete-user)
2. [Projects](#projects)
   1. [Create a project](#create-a-project)
   2. [List a single project](#list-a-single-project)
   3. [Update a single project](#update-a-single-project)
   4. [Delete a single project](#delete-a-single-project)
   5. [List all projects](#list-all-projects)
3. [Publications](#publications)
   1. [Publish JSON/ARRAY](#publish-jsonarray)
   2. [Publish CSV File](#publish-csv-file)
4. [Logs](#logs)
   1. [List all Logs](#list-all-logs)
   2. [Update a single log](#update-a-single-log)

---

## Users

---

User management resources.

### Create a user

Create a new user's account on the deku cloud server.

```
POST v1/signup
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

_**Body**_

| Attribute            | Type   | Required | Description                                                                                            |
| :------------------- | :----- | :------- | :----------------------------------------------------------------------------------------------------- |
| `email`              | string | Yes      | An active email address for account identification.                                                    |
| `password`           | string | Yes      | A a word, phrase, or string for account security.                                                      |
| `phone_number`       | string | No       | An active phone number for extra account security.                                                     |
| `first_name`         | string | No       | A first_name for account personalization.                                                              |
| `last_name`          | string | No       | A last_name for account personalization.                                                               |
| `twilio_account_sid` | string | No       | [Twilio account_sid](https://www.twilio.com/blog/better-twilio-authentication-csharp-twilio-api-keys). |
| `twilio_auth_token`  | string | No       | [Twilio auth_token](https://www.twilio.com/blog/better-twilio-authentication-csharp-twilio-api-keys).  |
| `twilio_service_sid` | string | No       | [Twilio messaging service_sid](https://www.twilio.com/docs/glossary/what-is-a-sid)                     |

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/signup' --header 'Content-Type: application/json' --data-raw '{"email": "", "password": "", "first_name": "", "last_name": "", "phone_number": "", "twilio_account_sid": "", "twilio_auth_token": "", "twilio_service_sid": ""}'
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
POST v1/login
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
GET v1/
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
	"first_name": "",
	"last_name": "",
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
PUT v1/
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

_**Body**_

| Attribute            | Type   | Required | Description                                                                                            |
| :------------------- | :----- | :------- | :----------------------------------------------------------------------------------------------------- |
| `first_name`         | string | No       | A first_name for account personalization.                                                              |
| `last_name`          | string | No       | A last_name for account personalization.                                                               |
| `phone_number`       | string | No       | An active phone number for extra account security.                                                     |
| `password`           | string | No       | Current user's password.                                                                               |
| `new_password`       | string | No       | A new secure password.                                                                                 |
| `twilio_account_sid` | string | No       | [Twilio account_sid](https://www.twilio.com/blog/better-twilio-authentication-csharp-twilio-api-keys). |
| `twilio_auth_token`  | string | No       | [Twilio auth_token](https://www.twilio.com/blog/better-twilio-authentication-csharp-twilio-api-keys).  |
| `twilio_service_sid` | string | No       | [Twilio messaging service_sid](https://www.twilio.com/docs/glossary/what-is-a-sid)                     |

```shell
curl --location --request PUT 'https://staging.smswithoutborders.com:12000/v1/' --header 'Content-Type: application/json' --data-raw '{"first_name": "", "last_name": "", "phone_number": "", "twilio_account_sid": "", "twilio_auth_token": "", "twilio_service_sid": ""}'
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
	"first_name": "",
	"last_name": "",
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

### Delete User

> _**[Authentication](#authentication) Required**_

Delete currently authenticated user's account.

```
DELETE v1/
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

```shell
curl --location --request DELETE 'https://staging.smswithoutborders.com:12000/v1/' --header 'Content-Type: application/json'
```

Example response:

> [200] Successful

Raised when the request to delete the user account is completed successfully.

> [401] Unauthorized

Raised when the request lacks valid authentication credentials for the requested
resource.

> [404] Not Found

Raised when the user account to be deleted is not found.

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
POST v1/projects
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

_**Body**_

| Attribute       | Type   | Required | Description                                                                                                           |
| :-------------- | :----- | :------- | :-------------------------------------------------------------------------------------------------------------------- |
| `friendly_name` | string | Yes      | The friendly name of the project. It should be unique and provide a descriptive name for the project.                 |
| `description`   | string | No       | A brief description of the project. This field allows you to provide additional details or context about the project. |
| `reference`     | string | No       | A unique reference ID for the project. If not provided, it will be auto-generated.                                    |

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/projects' --header 'Content-Type: application/json' --data-raw '{"friendly_name": "", "description": "", "reference": ""}'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json
{
	"id": "",
	"friendly_name": "",
	"reference": "",
	"description": "",
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

### List a single project

> _**[Authentication](#authentication) Required**_

Details of a single project for the authenticated user.

```
GET v1/projects/:project_id
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

_**Params**_

| Attribute    | Type   | Required | Description                                 |
| :----------- | :----- | :------- | :------------------------------------------ |
| `project_id` | string | Yes      | A unique string used to identify a project. |

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/projects/:project_id' --header 'Content-Type: application/json'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json
{
	"id": "",
	"friendly_name": "",
	"reference": "",
	"description": "",
	"created_at": ""
}
```

> [400] Bad Request

Raised when some attributes are omitted or the request isn't structured
correctly.

> [401] Unauthorized

Raised when the request lacks valid authentication credentials for the requested
resource.

> [404] Not Found

Raised when the server cannot find the requested resource.

> [500] Internal Server Error

Raised when the server encountered an unexpected condition that prevented it
from fulfilling the request.

### Update a single project

> _**[Authentication](#authentication) Required**_

Update details of a single project for the authenticated user.

```
PUT v1/projects/:project_id
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

_**Params**_

| Attribute    | Type   | Required | Description                                 |
| :----------- | :----- | :------- | :------------------------------------------ |
| `project_id` | string | Yes      | A unique string used to identify a project. |

_**Body**_

| Attribute       | Type   | Required | Description                           |
| :-------------- | :----- | :------- | :------------------------------------ |
| `friendly_name` | string | No       | Updated friendly name of the project. |
| `description`   | string | No       | Updated description of the project.   |

```shell
curl --location --request PUT 'https://staging.smswithoutborders.com:12000/v1/projects/:project_id' --header 'Content-Type: application/json' --data-raw '{"friendly_name": "", "description": ""}'
```

Example response:

> [200] Successful

Raised when the request to update the project details is completed successfully.

```json
{
	"id": "",
	"friendly_name": "",
	"reference": "",
	"description": "",
	"created_at": ""
}
```

> [400] Bad Request

Raised when some attributes are omitted or the request isn't structured
correctly.

> [401] Unauthorized

Raised when the request lacks valid authentication credentials for the requested
resource.

> [404] Not Found

Raised when the server cannot find the project to be updated.

> [500] Internal Server Error

Raised when the server encountered an unexpected condition that prevented it
from fulfilling the request.

### Delete a single project

> _**[Authentication](#authentication) Required**_

Delete a single project for the authenticated user.

```
DELETE v1/projects/:project_id
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

_**Params**_

| Attribute    | Type   | Required | Description                                 |
| :----------- | :----- | :------- | :------------------------------------------ |
| `project_id` | string | Yes      | A unique string used to identify a project. |

```shell
curl --location --request DELETE 'https://staging.smswithoutborders.com:12000/v1/projects/:project_id' --header 'Content-Type: application/json'
```

Example response:

> [200] Successful

Raised when the request to delete the project is completed successfully.

> [401] Unauthorized

Raised when the request lacks valid authentication credentials for the requested
resource.

> [404] Not Found

Raised when the server cannot find the project to be deleted.

> [500] Internal Server Error

Raised when the server encountered an unexpected condition that prevented it
from fulfilling the request.

### List all projects

> _**[Authentication](#authentication) Required**_

Details of all projects for the authenticated user.

```
GET v1/projects
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/projects' --header 'Content-Type: application/json'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json
[
	{
		"id": "",
		"friendly_name": "",
		"reference": "",
		"description": "",
		"created_at": ""
	}
]
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

## Publications

Publication management resources.

### Publish JSON/ARRAY

Make a request to deku server to publish a json/array body.

```
POST v1/projects/:reference/services/:service_id
```

_**Headers**_

| Attribute       | Value                                                 | Required | Description                                                                                                              |
| :-------------- | :---------------------------------------------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type`  | application/json                                      | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |
| `Authorization` | Basic _**Base64 encoded account_sid and auth_token**_ | Yes      | Used to provide credentials that authenticate a user with a server.                                                      |

_**Params**_

| Attribute    | Type   | Required | Description                                 |
| :----------- | :----- | :------- | :------------------------------------------ |
| `reference`  | string | Yes      | A unique string used to identify a project. |
| `service_id` | string | Yes      | a Deku service (SMS, NOTIFICATION).         |

_**Body**_

| Attribute | Type   | Required | Description                                          |
| :-------- | :----- | :------- | :--------------------------------------------------- |
| `body`    | string | Yes      | Content to be sent via deku service.                 |
| `to`      | string | Yes      | Recipient.                                           |
| `sid`     | string | No       | Optional state identifier to associate message with. |

> Object body

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/projects/:reference/services/:service_id' --header 'Content-Type: application/json' --user "account_sid:auth_token" --data-raw '{"body": "", "to": "", "sid": ""}'
```

> Array body

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/projects/:reference/services/:service_id' --header 'Content-Type: application/json' --user "account_sid:auth_token" --data-raw '[{"body": "", "to": "", "sid": ""}, {"body": "", "to": "", "sid": ""}]'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json
{
	"message": "",
	"errors": [],
	"response": [
		{
			"errors": [],
			"message": "",
			"sid": "",
			"warnings": []
		}
	],
	"warnings": []
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

### Publish CSV File

Make a request to deku server to publish a csv file.

```
POST v1/projects/:reference/services/:service_id
```

_**CSV File Format**_

| Attribute | Type   | Required | Description                                          |
| :-------- | :----- | :------- | :--------------------------------------------------- |
| `body`    | string | Yes      | Content to be sent via deku service.                 |
| `to`      | string | Yes      | Recipient.                                           |
| `sid`     | string | No       | Optional state identifier to associate message with. |

> **Note**: The first row contains the column headers. Each subsequent row
> contains the values for a single message.

_**Headers**_

| Attribute       | Value                                                 | Required | Description                                                         |
| :-------------- | :---------------------------------------------------- | :------- | :------------------------------------------------------------------ |
| `Authorization` | Basic _**Base64 encoded account_sid and auth_token**_ | Yes      | Used to provide credentials that authenticate a user with a server. |

_**Params**_

| Attribute    | Type   | Required | Description                                 |
| :----------- | :----- | :------- | :------------------------------------------ |
| `reference`  | string | Yes      | A unique string used to identify a project. |
| `service_id` | string | Yes      | a Deku service (SMS, NOTIFICATION).         |

_**Form**_

| Attribute     | Type   | Required | Description                                      |
| :------------ | :----- | :------- | :----------------------------------------------- |
| `key`         | string | Yes      | Key of the form field. (Requires "file")         |
| `type`        | string | Yes      | Type of the form field. (Requires "File")        |
| `value`       | string | Yes      | Value of the form field. (Requires path to file) |
| `description` | string | No       | Description of the form field                    |

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/projects/:reference/services/:service_id' --user "account_sid:auth_token" --form 'file=@"/path/to/sample.csv"'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json
{
	"message": "",
	"errors": [],
	"response": [
		{
			"errors": [],
			"message": "",
			"sid": "",
			"warnings": []
		}
	],
	"warnings": []
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

## Logs

Log management resources.

### List all Logs

> _**[Authentication](#authentication) Required**_

Details of all publication logs for the currently authenticated user.

```
GET v1/logs
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

```shell
curl --location 'https://staging.smswithoutborders.com:12000/v1/logs' --header 'Content-Type: application/json'
```

Example response:

> [200] Successful

Raised when request completed successfully.

```json
[
	{
		"channel": "",
		"sid": "",
		"from_": "",
		"direction": "",
		"status": "",
		"reason": "",
		"created_at": "",
		"to_": "",
		"body": ""
	}
]
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

### Update a single log

> _**[Authentication](#authentication) Required**_

Update details of a single log for the authenticated user.

```
PUT v1/logs/:log_id
```

_**Headers**_

| Attribute      | Value            | Required | Description                                                                                                              |
| :------------- | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------- |
| `Content-Type` | application/json | Yes      | Used to indicate the original [media type](https://developer.mozilla.org/en-US/docs/Glossary/MIME_type) of the resource. |

_**Params**_

| Attribute | Type   | Required | Description                             |
| :-------- | :----- | :------- | :-------------------------------------- |
| `log_id`  | string | Yes      | A unique string used to identify a log. |

_**Body**_

| Attribute | Type   | Required | Description                |
| :-------- | :----- | :------- | :------------------------- |
| `status`  | string | Yes      | Updated status of the log. |

```shell
curl --location --request PUT 'https://staging.smswithoutborders.com:12000/v1/logs/:log_id' --header 'Content-Type: application/json' --data-raw '{"status": ""}'
```

Example response:

> [200] Successful

Raised when the request to update the log details is completed successfully.

```json
{
	""
}
```

> [400] Bad Request

Raised when some attributes are omitted or the request isn't structured
correctly.

> [401] Unauthorized

Raised when the request lacks valid authentication credentials for the requested
resource.

> [404] Not Found

Raised when the server cannot find the log to be updated.

> [500] Internal Server Error

Raised when the server encountered an unexpected condition that prevented it
from fulfilling the request.
