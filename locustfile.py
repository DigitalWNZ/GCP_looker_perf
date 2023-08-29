import logging
from typing import Any

from locust import HttpUser, events
from locustfiles.looker_run_query_nocache import LookerRunQueryNoCache


class ApiUser(HttpUser):
    tasks = [LookerRunQueryNoCache]

@events.quitting.add_listener
def _(environment, **kwargs: Any) -> None:
    print(type(environment))
    if environment.stats.total.fail_ratio > 0:
        logging.error("Test failed due to failure ratio > 1%")
        environment.process_exit_code = 1
