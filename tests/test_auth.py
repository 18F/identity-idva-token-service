# tests/test_auth.py

from time import sleep
import unittest
import json

from server import db, config
from server.models import Token
from tests.base import BaseTestCase


class TestAuthBlueprint(BaseTestCase):
    def test_registration(self):
        """Test for token registration"""
        with self.client:
            response = self.client.post(
                "/auth/register", headers={"X_API_KEY": config["SECRET_KEY"]}
            )
            data = json.loads(response.data)
            self.assertEquals(data["status"], "success")
            self.assertEquals(data["message"], "Successfully registered.")
            self.assertTrue(data["auth_token"])
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

    def test_validation(self):
        """Test for validity of registered token"""
        with self.client:
            response = self.client.post(
                "/auth/register", headers={"X_API_KEY": config["SECRET_KEY"]}
            )
            data = json.loads(response.data)
            auth_token = data["auth_token"]

            self.assertEquals(data["status"], "success")
            self.assertEquals(data["message"], "Successfully registered.")
            self.assertTrue(auth_token)
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)
            # registered user login
            response = self.client.post(
                "/auth/validate",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"auth_token": auth_token}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Token exists")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 200)

    def test_validation_does_not_exist(self):
        """Test for validity of registered token"""
        with self.client:
            response = self.client.post(
                "/auth/validate",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"auth_token": "NOT_A_TOKEN"}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(data["message"] == "Unauthorized")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 403)

    def test_validation_expired(self):
        """Test for validity of registered token"""
        with self.client:
            # register token with 1 second expiration
            response = self.client.post(
                "/auth/register",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"seconds": 1}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            auth_token = data["auth_token"]

            self.assertEquals(data["status"], "success")
            self.assertEquals(data["message"], "Successfully registered.")
            self.assertTrue(auth_token)
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

            # validate token
            # wait for token to expire
            sleep(5)
            response = self.client.post(
                "/auth/validate",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"auth_token": auth_token}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(data["message"] == "Token expired")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 403)

    def test_validation_invoke(self):
        """Test for validity of registered token"""
        with self.client:
            # register token with 1 second expiration
            response = self.client.post(
                "/auth/register",
                headers={"X-API-Key": config["SECRET_KEY"]},
            )
            data = json.loads(response.data)
            auth_token = data["auth_token"]

            self.assertEquals(data["status"], "success")
            self.assertEquals(data["message"], "Successfully registered.")
            self.assertTrue(auth_token)
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

            # invoke token (valid attempt)
            response = self.client.post(
                "/auth/invoke",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"auth_token": auth_token}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Token successfully invoked")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 200)

    def test_validation_invoke_exhausted(self):
        """Test for validity of registered token"""
        with self.client:
            # register token with 1 second expiration
            # key = "something " + config["SECRET_KEY"]
            x = config["SECRET_KEY"]
            response = self.client.post(
                "/auth/register",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"seconds": 60}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            auth_token = data["auth_token"]

            self.assertEquals(data["status"], "success")
            self.assertEquals(data["message"], "Successfully registered.")
            self.assertTrue(auth_token)
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

            # invoke token (valid attempt)
            key = "something " + config["SECRET_KEY"]
            self.client.post(
                "/auth/invoke",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"auth_token": auth_token}),
                content_type="application/json",
            )
            response = self.client.post(
                "/auth/invoke",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"auth_token": auth_token}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertEquals(data["status"], "fail")
            self.assertEquals(data["message"], "Token exhausted")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 403)

    def test_exhaust(self):
        with self.client:
            # register token with 1 second expiration
            response = self.client.post(
                "/auth/register",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"seconds": 60}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            auth_token = data["auth_token"]

            self.assertEquals(data["status"], "success")
            self.assertEquals(data["message"], "Successfully registered.")
            self.assertTrue(auth_token)
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

            # exhaust token (valid attempt)
            response = self.client.post(
                "/auth/exhaust",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"auth_token": auth_token}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertEquals(data["status"], "success")
            self.assertEquals(data["message"], "Token successfully exhausted")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
