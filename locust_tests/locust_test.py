from locust import HttpUser, task, between
import random

class ShortenURLUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def shorten_link(self):
        self.client.post("/links/shorten", json={"original_url": "http://example.com/" + str(random.randint(1, 1000))})


