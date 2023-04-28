"""Peewee Handlers for user model"""

import logging
from datetime import datetime
from typing import Optional

from src.orm.peewee.models.user import User
from src.orm.peewee.handlers.project import ProjectHandler

logger = logging.getLogger(__name__)


class UserHandler(ProjectHandler):
    """
    A class for handling CRUD operations on the User model, including managing projects.
    """

    def create_user(self, email: str, password: str, **kwargs) -> Optional[User]:
        """Create a new user.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.
            kwargs: additional optional fields for the user model.

        Returns:
            The newly created user, or None if user already exists.
        """
        # Check if a user already exists with the same email
        existing_user = self.get_users_by_field(email=email)

        if existing_user[0] > 0 and len(existing_user[1]) > 0:
            if len(existing_user[1]) > 1:
                logger.critical("User %s has multiple accounts.", email)
                return None

            logger.error("User %s already exists.", email)
            return None

        try:
            user = User.create(email=email, password=password, **kwargs)

            logger.info("User created successfully.")

            return user

        except Exception as error:
            logger.error("Error creating user")
            raise error

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by its ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The retrieved user, or None if no user with that ID exists.
        """
        try:
            user = User.get(id=user_id)
            return user

        except User.DoesNotExist:
            logger.error("User with ID %s does not exist.", user_id)
            return None

    def get_users_by_field(
        self, data_range: list = None, sort: list = None, **kwargs
    ) -> list:
        """Retrieve all users with the given field(s).

        Args:
            data_range (list): A list of two int values representing the offset and limit of the data to retrieve. Default is None, which retrieves all users.
            sort (list): A list of field and order to sort the users by. Default is None, which returns the users in the order they were retrieved.
            kwargs: fields for users to retrieve. Default is None, which retrieves all users.

        Returns:
            A list of the total number of records retrieved and the retrieved users, or an empty list if no users.
        """
        try:
            where_fields = ()
            users = User.select()

            for field, value in kwargs.items():
                if field == "password":
                    logger.warning("The password field cannot be queried directly")
                    continue

                if field[-5:] == "_name":
                    where_fields += (getattr(User, field).contains(value),)
                    continue

                if field[-3:] == "_at" or field[-5:] == "_seen":
                    date_at = datetime.strptime(value, "%Y-%m-%d").date()
                    start = datetime(date_at.year, date_at.month, date_at.day, 0, 0, 0)
                    end = datetime(date_at.year, date_at.month, date_at.day, 23, 59, 59)

                    where_tuple += (getattr(User, field).between(start, end),)
                    continue

                if hasattr(User, field):
                    where_fields += (getattr(User, field) == value,)
                    continue

                logger.warning("Field %s does not exist for users model.", field)

            if sort and len(sort) > 0:
                sort_field = getattr(User, sort[0])
                if sort[1] != "ASC":
                    sort_field = sort_field.desc()
                users = users.order_by(sort_field)

            if len(where_fields) > 0:
                users = users.where(*where_fields)

            total = users.count()

            if data_range and len(data_range) > 0:
                limit = int(data_range[1])
                offset = int(data_range[0])
                users = users.offset(offset).limit(limit)

            logger.info("Successfully retrieved users")

            return [total, list(users)]

        except Exception as error:
            logger.error("Error retrieving users.")
            raise error

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update an existing user.

        Args:
            user_id: The ID of the user to be updated.
            kwargs: fields to be updated for the user.

        Returns:
            The updated user, or None if the user with the ID does not exist.
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                logger.error("User with ID %s does not exist.", user_id)
                return None

            # Generate a dictionary of fields to update.
            update_fields = {}
            for field, value in kwargs.items():
                if hasattr(user, field):
                    update_fields[field] = value
                else:
                    logger.warning("Field %s does not exist for user model.", field)

            if update_fields:
                User.update(**update_fields).where(User.id == user_id).execute()

                # Reload the updated user and return it.
                updated_user = self.get_user_by_id(user_id)

                logger.info("User updated successfully.")

                return updated_user

            logger.warning("No valid fields provided for update.")
            return None

        except Exception as error:
            logger.error("Error updating user: %s", error)
            raise

    def delete_user(self, user_id: int) -> bool:
        """Delete a user by its ID.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            True if the user was deleted, False otherwise.
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                logger.error("User with ID %s does not exist.", user_id)
                return False

            # delete all the user's projects before deleting the user
            [total, projects_list] = self.get_projects_by_field(user_id=user_id)

            for project in projects_list:
                self.delete_project(project.id)

            user.delete_instance()

            logger.info("User deleted successfully.")

            return True

        except Exception as error:
            logger.error("Error deleting user: %s", error)
            return False
