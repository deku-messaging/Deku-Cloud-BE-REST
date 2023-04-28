"""Controller Functions for Service Operations"""

import logging
from typing import Optional, Dict

from playhouse.shortcuts import model_to_dict

from werkzeug.exceptions import Unauthorized

from src.orm.peewee.handlers.project import ProjectHandler
from src.orm.peewee.handlers.user import UserHandler
from src.utils import rabbitmq

logger = logging.getLogger(__name__)


def create_project(friendly_name: str, user_id: int) -> Optional[Dict]:
    """Creates a new project and corresponding RabbitMQ exchange.

    :param friendly_name: str - The friendly name of the project.
    :param user_id: int - The ID of the user that the project belongs to.

    :return: Optional[Dict] - A dictionary representation of the new project, or None if creation failed.
    """
    project_handler = ProjectHandler()

    new_project = project_handler.create_project(
        friendly_name=friendly_name, user_id=user_id
    )

    if not new_project:
        return None

    user_handler = UserHandler()
    user = user_handler.get_user_by_id(user_id=user_id)

    if not user:
        raise Unauthorized()

    try:
        rabbitmq.create_exchange(
            name=new_project.reference, virtual_host=user.account_sid
        )
    except Exception as error:
        # Rollback changes.
        rabbitmq.delete_exchange(
            virtual_host=user.account_sid, name=new_project.reference
        )
        new_project.delete_instance()

        raise error

    return model_to_dict(new_project, recurse=False)


def get_project_by_id(project_id: str) -> Optional[Dict]:
    """
    Retrieves a project by its ID.

    :param project_id: str - The ID of the project to retrieve.

    :return: Dict - A dictionary representation of the project, or None if the project could not be found.

    :raises: Unauthorized if the user that the project belongs to does not exist.
    """
    project_handler = ProjectHandler()

    project = project_handler.get_project_by_id(project_id=project_id)

    if not project:
        return None

    user_handler = UserHandler()
    user = user_handler.get_user_by_id(user_id=project.user_id)

    if not user:
        raise Unauthorized()

    if not rabbitmq.get_exhange_by_name(
        name=project.reference, virtual_host=user.account_sid
    ):
        project.delete_instance()
        return None

    return model_to_dict(project, recurse=False)


def get_projects_by_field(user_id: int, **kwargs) -> list:
    """
    Retrieves projects based on the given search criteria.

    :param user_id: int - The ID of the user that the projects belong to.
    :param kwargs: keyword arguments representing the search criteria (e.g. name="project name").

    :return: List - A list containing the total number of projects that match the search criteria and a list of their dictionary representations.

    :raises: Unauthorized if the user with the given user_id does not exist.
    """
    project_handler = ProjectHandler()
    user_handler = UserHandler()

    [total, projects_list] = project_handler.get_projects_by_field(
        user_id=user_id, **kwargs
    )

    result = [0, []]

    for project in projects_list:
        user = user_handler.get_user_by_id(user_id=project.user_id)

        if not user:
            raise Unauthorized()

        if not rabbitmq.get_exhange_by_name(
            name=project.reference, virtual_host=user.account_sid
        ):
            project.delete_instance()
            continue

        result[0] += 1
        result[1].append(model_to_dict(project, recurse=False))

    return result
