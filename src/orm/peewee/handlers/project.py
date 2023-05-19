"""Peewee Handlers for project model"""

import logging
from datetime import datetime
from typing import Optional
import secrets

from src.orm.peewee.models.project import Project

logger = logging.getLogger(__name__)


class ProjectHandler:
    """
    A class for handling CRUD operations on the Project model.
    """

    def create_project(
        self,
        friendly_name: str,
        description: str,
        user_id: int,
    ) -> Optional[Project]:
        """
        Create a new project.

        :param friendly_name: str - The friendly name of the project.
        :param description: str - The description of the project.
        :param user_id: int - The ID of the user associated with the project.

        :return: Optional[Project] - The newly created project if successful, otherwise None.
        """
        # Check if a project already exists for the user
        existing_project = self.get_projects_by_field(
            user_id=user_id, friendly_name=friendly_name
        )

        if existing_project[0] > 0 and len(existing_project[1]) > 0:
            logger.error(
                "A project with name %s already exists for user ID %s",
                friendly_name,
                user_id,
            )
            return None

        try:
            project = Project.create(
                friendly_name=friendly_name, description=description, user_id=user_id
            )

            project.reference = "PJ" + str(project.id) + secrets.token_hex(8)
            project.save()

            logger.info("Project created successfully.")

            return project

        except Exception as error:
            logger.error("Error creating project")
            raise error

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Retrieve a project by its ID.

        :param project_id: int - The ID of the project to retrieve.

        :return: Optional[Project] - The retrieved project, or None if no project with that ID exists.
        """
        try:
            project = Project.get(id=project_id)
            return project

        except Project.DoesNotExist:
            logger.error("Project with ID %s does not exist.", project_id)
            return None

    def get_projects_by_field(
        self, data_range: list = None, sort: list = None, **kwargs
    ) -> list:
        """Retrieve all projects with the given field(s).

        :param data_range: list - A list of two int values representing the offset and limit of the data to retrieve. Default is None, which retrieves all projects.
        :param sort: list - A list of field and order to sort the projects by. Default is None, which returns the projects in the order they were retrieved.
        :param kwargs: dict - fields for projects to retrieve. Default is None, which retrieves all projects.

        :return: list - A list of the total number of records retrieved and the retrieved projects, or an empty list if no projects.
        """
        try:
            where_fields = ()
            projects = Project.select()

            for field, value in kwargs.items():
                if field == "user_id":
                    where_fields += (Project.user_id == value,)
                    continue

                if field == "friendly_name":
                    where_fields += (getattr(Project, field).contains(value),)
                    continue

                if field[-3:] == "_at":
                    date_at = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").date()
                    start = datetime.combine(date_at, datetime.min.time())
                    end = datetime.combine(date_at, datetime.max.time())

                    where_fields += (getattr(Project, field).between(start, end),)
                    continue

                if hasattr(Project, field):
                    where_fields += (getattr(Project, field) == value,)
                    continue

                logger.warning("Field %s does not exist for projects model.", field)

            if sort and len(sort) > 0:
                sort_field = getattr(Project, sort[0])
                if sort[1] != "ASC":
                    sort_field = sort_field.desc()
                projects = projects.order_by(sort_field)

            if len(where_fields) > 0:
                projects = projects.where(*where_fields)

            total = projects.count()

            if data_range and len(data_range) > 0:
                limit = int(data_range[1])
                offset = int(data_range[0])
                projects = projects.offset(offset).limit(limit)

            logger.info("Successfully retrieved projects")

            return [total, list(projects)]

        except Exception as error:
            logger.error("Error retrieving projects.")
            raise error

    def update_project(self, project_id: int, **kwargs) -> Optional[Project]:
        """Update an existing project.

        :param project_id: int - The ID of the project to be updated.
        :param kwargs: dict - fields to be updated for the project.

        :erturn: Optional[Project] - The updated project, or None if the project with the ID does not exist.
        """
        try:
            project = self.get_project_by_id(project_id)
            if not project:
                logger.error("Project with ID %s does not exist.", project_id)
                return None

            # Generate a dictionary of fields to update.
            update_fields = {}
            for field, value in kwargs.items():
                if hasattr(project, field):
                    update_fields[field] = value
                else:
                    logger.warning("Field %s does not exist for project model.", field)

            if update_fields:
                Project.update(**update_fields).where(
                    Project.id == project_id
                ).execute()

                # Reload the updated project and return it.
                updated_project = self.get_project_by_id(project_id)

                logger.info("Project updated successfully.")

                return updated_project

            logger.warning("No valid fields provided for update.")
            return None

        except Exception as error:
            logger.error("Error updating project: %s", error)
            raise

    def delete_project(self, project_id: int) -> bool:
        """Delete a project by its ID.

        :param project_id: int - The ID of the project to delete.

        :return: bool - True if the project was deleted, False otherwise.
        """
        try:
            project = self.get_project_by_id(project_id)
            if not project:
                logger.error("Project with ID %s does not exist.", project_id)
                return False

            project.delete_instance()

            logger.info("Project deleted successfully.")

            return True

        except Exception as error:
            logger.error("Error deleting project: %s", error)
            return False
