"""Projects Handler"""

import logging
from uuid import uuid1

from werkzeug.exceptions import Conflict

from src.schemas.projects import Projects
from src.schemas.users import Users

from src.models.rabbitmq import RabbitMQModel

logger = logging.getLogger(__name__)


class ProjectModel:
    """Handler definition"""

    def __init__(self):
        self.projects = Projects
        self.users = Users
        self.rabbitmq = RabbitMQModel

    def create(
        self,
        name: str,
        user_id: str
    ) -> object:
        """Create a project.

        Keyword arguments:
        name -- project's name
        user_id -- user's ID

        return: object
        """

        rabbitmq = self.rabbitmq()

        try:
            logger.debug("[*] Finding project '%s' ...", name)

            project = self.projects.get(
                self.projects.name == name,
                self.projects.user_id == user_id
            )

        except self.projects.DoesNotExist:
            try:
                logger.debug("[*] Creating project '%s' ...", name)

                project = self.projects.create(
                    name=name,
                    user_id=user_id
                )

                project.project_ref = "PJ" + str(project.id) + str(uuid1())[0:8]
                project.save()

                user = self.users.get(self.users.id == project.user_id)

                rabbitmq.add_exchange(name=project.project_ref, vhost=user.account_sid)

                logger.info("[x] Successfully created project")

                return project

            except Exception as error:
                logger.error("[!] Error creating project. See logs below")
                raise error

        else:
            logger.error("[!] Project '%s' exists", project.name)
            raise Conflict()
