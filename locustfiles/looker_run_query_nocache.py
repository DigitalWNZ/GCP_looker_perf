import looker_helper
import settings
from locust import TaskSet, between, events, task


class LookerRunQueryNoCache(TaskSet):
    """Description . . ."""

    wait_time = between(1, 3)

    def on_start(self) -> None:
        """Logins and stuff before starting a user session."""
        self.hostname = f"{settings.LOOKER_HOST}/api/4.0/"
        self.token = settings.LOOKER_CLIENT_ID
        self.secret = settings.LOOKER_CLIENT_SECRET
        self.cache_flag = True

        self.user_id = looker_helper.create_user()

        looker_helper.login(self)
        looker_helper.sudo(self, self.user_id)
        query_id = '495597'
        looker_helper.run_query(self, query_id)

    @task(1)
    def run_query(self) -> None:
        query_id = '495597'
        looker_helper.run_query(self, query_id)

    def on_stop(self) -> None:
        """Logout and stuff after ending a user session."""
        looker_helper.logout(self.user_id)


