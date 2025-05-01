from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(1, 3)  # seconds between tasks

    @task
    def test_home(self):
        self.client.get("/")  # this hits http://localhost:8081/

