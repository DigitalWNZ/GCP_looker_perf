import requests
import looker_sdk
from looker_sdk import models40, methods40, requests_transport
from looker_sdk.rtl import transport, serialize, auth_session, api_settings
from locust import HttpUser, task
from typing import Optional

def init40(
    session: requests.Session = requests.Session(),
    config_file: str = "looker.ini",
    section: Optional[str] = None,
) -> methods40.Looker40SDK:
    """Default dependency configuration"""
    settings = (
        looker_sdk._settings(config_file, section)
    )
    settings.is_configured()
    transport = requests_transport.RequestsTransport(settings, session)
    return methods40.Looker40SDK(
        auth_session.AuthSession(settings, transport, serialize.deserialize40, "4.0"),
        serialize.deserialize40,
        serialize.serialize40,
        transport,
        "4.0",
    )

class LookerUser(HttpUser):
    sdk = init40()
    model="aftership_mysql"
    explore="rt_stock"
    fields=["rt_stock.dt_date","rt_stock.average_price"]
    print("Create original query")
    query = sdk.create_query(
        body=models40.WriteQuery(model=model, view=explore, fields=fields)
    )
    print(query)
    print("Run orginal query to get the drill down URL")
    # print(sdk.me())
    print(query.id)
    query_run = sdk.run_query(
        query_id=query.id,
        result_format="json",
        limit=10
        # generate_drill_links=True
    )
    print(query_run)

    def on_start(self):
        sdk = init40(self.client)
        self.sdk = sdk
        model="aftership_mysql"
        explore="rt_stock"
        fields=["rt_stock.dt_date","rt_stock.average_price"]
        print("Create original query")
        self.query = sdk.create_query(
            body=models40.WriteQuery(model=model, view=explore, fields=fields)
        )
        print("Run orginal query to get the drill down URL")
        query_run = self.sdk.run_query(
            cache=True,
            query_id=self.query.id,
            result_format='json_detail',
            generate_drill_links=True
        )
        print(query_run)

    @task
    def user_daily(self):
        while True:
            query_run = self.sdk.run_query(
                cache=True,
                query_id=self.query.id,
                result_format='json_detail',
                generate_drill_links=True
            )

