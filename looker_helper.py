import json
import logging
import time

from locust import events
from locust.exception import RescheduleTask


def login(self) -> None:
    url = '{}{}'.format(self.hostname, 'login')
    params = {'client_id': self.token,
              'client_secret': self.secret}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    with self.client.post(url,
                          headers=headers,
                          data=params,
                          catch_response=True) as r:  # add verify=False if using a self-signed cert
        access_token = None
        if r.status_code:
            if r.status_code == 200:
                access_token = r.json().get('access_token')
            else:
                r.failure("Login Failure")
        else:
            r.failure(url + ':failure exceed maximum time')

    self.client.headers.update(
        {'Authorization': 'token {}'.format(access_token)})


def sudo(self, user_id) -> None:
    url = '{}{}/%i?associative={}'.format(self.hostname, 'login', 'false')
    with self.client.post(url % user_id, name="/login/[user_id]") as r:
        access_token = None
        if r.status_code:
            if r.status_code == 200:
                access_token = r.json().get('access_token')
                logging.info(url + ': success (' + str(user_id) + ')')
            else:
                logging.error("Login Failure")
        else:
            logging.error(url + ':failure exceed maximum time')
    self.client.headers.update(
        {'Authorization': 'token {}'.format(access_token)})


def get_user_id() -> int:
    filename = "list_of_user_ids.txt"
    user_lists = [line.strip() for line in open(filename, 'r')]

    file = open('list_of_user_ids.txt', 'w')
    for user_id in user_lists[1:]:
        file.write(user_id + "\n")
    file.close()

    return int(user_lists[0])


def logout(user_id) -> None:
    """Add your logout logic here."""
    logging.info("Logging out...")
    disable_user(user_id)


def create_user() -> int:
    import random

    import looker_sdk
    sdk = looker_sdk.init40()
    mdls = looker_sdk.models40

    random_int = random.randint(1000000, 99999999)

    first_name = f"mock_user_{random_int}"
    last_name = "test"

    response = sdk.create_user(
        body=mdls.WriteUser(
            is_disabled=False,
            models_dir_validated=False,
            first_name=first_name,
            last_name=last_name
        ))

    user_id = response.id
    sdk.set_user_roles(user_id, [5])

    return int(user_id)


def delete_user(user_id):
    import looker_sdk

    sdk = looker_sdk.init40()
    sdk.delete_user(str(user_id))


def run_query(self,query_id):
    url='{}{}/{}/{}/{}'.format(self.hostname,'queries',query_id,'run','json_detail')
    data={"cache":True}
    with self.client.get(url,catch_response=True) as r:
        if r.status_code == 200:
            print("query done")
        else:
            print("query fail")

def wrap_for_locust(self, request_type, name, func, *args, **kwargs):
    try:
        start_time = time.time()
        result = func(*args, **kwargs)
    except Exception as event_exception:
        total_time = int((time.time() - start_time) * 1000)
        events.request_failure.fire(
            request_type=request_type,
            name=name,
            response_time=total_time,
            response_length=0,
            exception=event_exception
        )
        logging.error(event_exception)
        raise RescheduleTask()
    else:
        total_time = int((time.time() - start_time) * 1000)
        events.request_success.fire(
            request_type=request_type,
            name=name,
            response_time=total_time,
            response_length=0
        )
        return result


def disable_user(user_id):
    import looker_sdk
    sdk = looker_sdk.init40()
    mdls = looker_sdk.models40

    sdk.update_user(str(user_id), body=mdls.WriteUser(
        is_disabled=True
    ))

