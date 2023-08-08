"""Module to create RabbitMQ users via API."""

import argparse

from src.utils import rabbitmq


def create_rmq_user(account_sid: str, auth_token: str):
    """Create a new RabbitMQ user with a virtual host.

    :param account_sid: The account ID to use as the username.
    :param auth_token: The auth token to use as the password.
    :return: True if user created successfully, False otherwise.
    """

    try:
        if rabbitmq.create_virtual_host(name=account_sid):
            if rabbitmq.create_user(
                username=account_sid, password=auth_token, tags="management"
            ):
                rabbitmq.set_permissions(
                    configure=".*",
                    write=".*",
                    read=".*",
                    username=account_sid,
                    virtual_host=account_sid,
                )
                print("✅ User created successfully.")
                return True

        print("❌ Failed to create RabbitMQ user. See logs below")
        return False

    except Exception as error:
        print(f"Error creating user: {error}")

        # Rollback changes
        rabbitmq.delete_user(username=account_sid)
        rabbitmq.delete_virtual_host(name=account_sid)

        return False


def main():
    """Command line interface for creating RabbitMQ user."""

    parser = argparse.ArgumentParser(description="Create RabbitMQ user")
    parser.add_argument(
        "-u", "--username", required=True, help="The account ID to use as the username"
    )
    parser.add_argument(
        "-p", "--password", required=True, help="The auth token to use as the password"
    )
    args = parser.parse_args()

    create_rmq_user(args.username, args.password)


if __name__ == "__main__":
    main()

# python rmq_create_user.py -u myaccountid -p secretauthtoken 
