"""Projects Handler"""

import logging
from uuid import uuid1

from werkzeug.exceptions import Conflict, NotFound

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

    def create(self, name: str, user_id: str) -> object:
        """Create a project.

        Keyword arguments:
        name -- project's name
        user_id -- user's ID

        return: object
        """

        try:
            logger.debug("[*] Finding project '%s' ...", name)

            project = self.projects.get(
                self.projects.name == name, self.projects.user_id == user_id
            )

        except self.projects.DoesNotExist:
            try:
                logger.debug("[*] Creating project '%s' ...", name)

                project = self.projects.create(name=name, user_id=user_id)

                project.project_ref = "PJ" + str(project.id) + str(uuid1())[0:8]
                project.save()

                user = self.users.get(self.users.id == project.user_id)

                rabbitmq = self.rabbitmq(vhost=user.account_sid)

                rabbitmq.add_exchange(name=project.project_ref)

                logger.info("[x] Successfully created project")

                return project

            except Exception as error:
                logger.error("[!] Error creating project. See logs below")
                raise error

        else:
            logger.error("[!] Project '%s' exists", project.name)
            raise Conflict()

    def find_one(self, pid: str, user_id: str) -> object:
        """Find a project.

        Keyword arguments:
        pid -- project's ID
        user_id -- project owner's ID

        return: object
        """

        try:
            logger.debug("[*] Finding project ...")

            project = self.projects.get(
                self.projects.project_ref == pid, self.projects.user_id == user_id
            )

        except self.projects.DoesNotExist:
            msg = "Invalid Project ID."
            logger.error("[!] %s", msg)
            raise NotFound(msg)

        else:
            logger.info("[x] Project Found.")
            return project

    def find_many(self, user_id: str) -> object:
        """Find all projects.

        Keyword arguments:
        user_id -- project owner's ID

        return: object
        """

        result = []

        try:
            logger.debug("[*] Finding projects ...")

            projects = self.projects.select().where(self.projects.user_id == user_id)

        except Exception as error:
            logger.error("[!] Error finding projects. See logs below")
            raise error

        else:
            for project in projects.iterator():
                result.append(
                    {
                        "id": project.project_ref,
                        "name": project.name,
                        "created_at": project.created_at,
                    }
                )

            logger.info("[x] Projects Found.")

            return result
