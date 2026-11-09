import json
import logging
import os
import time
from threading import Event

import httpx
import jwt
from pydantic import TypeAdapter, ValidationError

from .schemas import (
    AuthKind,
    CloudConfigResponse,
    CloudSyncSignin,
    CloudSyncToken,
    Config,
)
from .utilities import Utilities

log = logging.getLogger("centre")


class CloudSync:
    SIGN_IN_ADAPTER = TypeAdapter(CloudSyncSignin)
    TOKEN_ADAPTER = TypeAdapter(CloudSyncToken)

    def __init__(self, log_enabled: bool = False):
        self.__username = os.getenv("CENTRE_CLOUD_USERNAME", None)
        self.__passwd = os.getenv("CENTRE_CLOUD_PASSWORD", None)

        if not (self.__username and self.__passwd):
            raise OSError(
                "The following environment variables are not defined or null:\n"
                "'CENTRE_CLOUD_USERNAME' and 'CENTRE_CLOUD_PASSWORD'\n\n"
                "Open https://centre-signup.syntaxly.bond/ to Create an account"
            )

        self.logging = log_enabled
        self.__auth_url = "https://ep-quiet-poetry-b9zv1wpx.neonauth.c-7.eu-central-1.aws.neon.tech/neondb/auth"
        self.__data_url = "https://ep-quiet-poetry-b9zv1wpx.apirest.c-7.eu-central-1.aws.neon.tech/neondb/rest/v1"

        self.__auth_file_path = Utilities.get_auth_file_path()
        self.__token_file_path = Utilities.get_token_file_path()

        if not os.path.isfile(self.__auth_file_path):
            with open(self.__auth_file_path, 'w'):
                pass

        if not os.path.isfile(self.__token_file_path):
            with open(self.__token_file_path, 'w'):
                pass

        self.__headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://centre.syntaxly.bond'
        }
        self.__client = httpx.Client(
            headers=self.__headers,
            default_encoding='utf-8'
        )

    def __read_auth_file(self, kind: AuthKind) -> CloudSyncSignin | CloudSyncToken | None:
        path = (
            self.__auth_file_path
            if kind == AuthKind.SIGN_IN
            else self.__token_file_path
        )
        adapter = self.SIGN_IN_ADAPTER if kind == AuthKind.SIGN_IN else self.TOKEN_ADAPTER

        try:
            with open(path, encoding="utf-8") as file:
                return adapter.validate_json(file.read())
        except (FileNotFoundError, ValidationError):
            return None

    def __write_auth_file(self, data: CloudSyncSignin | CloudSyncToken):
        match data:
            case CloudSyncSignin():
                serialized = self.SIGN_IN_ADAPTER.dump_python(data, mode="json")
                auth = AuthKind.SIGN_IN
            case CloudSyncToken():
                serialized = self.TOKEN_ADAPTER.dump_python(data, mode="json")
                auth = AuthKind.TOKEN
            case _:
                raise TypeError(f"Unsupported auth response: {type(data).__name__}")

        with open(self.__auth_file_path if auth == AuthKind.SIGN_IN else self.__token_file_path, 'w') as file:
            json.dump(serialized, file)

    def __authenticate(self) -> tuple[bool, CloudSyncSignin | None]:
        auth = self.__client.post(
            f"{self.__auth_url}/sign-in/email",
            json={
                "email": self.__username,
                "password": self.__passwd
            }
        )
        if not auth.is_success:
            error = auth.json()
            if error.get("code") == "INVALID_EMAIL_OR_PASSWORD" and self.logging:
                log.error(
                    "Sign in failed.\n"
                    "If you don't have an account, create one by signing up here:\n"
                    "Sign up -> https://centre-signup.syntaxly.bond/\n"
                    "Then Update your environment variables.\n"
                    "Or Correct your credentials"
                )
            return False, None

        resp: CloudSyncSignin = CloudSyncSignin(**auth.json())
        self.__write_auth_file(resp)
        return True, resp

    def __authorize(self) -> tuple[bool, CloudSyncToken | None]:
        auth = self.__read_auth_file(kind=AuthKind.SIGN_IN)
        if auth is None:
            raise RuntimeError("Could not obtain JWT")

        auth = self.__client.get(
            f"{self.__auth_url}/token",
            headers={
                "Authorization": f"Bearer {auth.token}",
            }
        )
        if not auth.is_success:
            if self.logging:
                log.error(f"Unable to authorize: {auth.reason_phrase}")
            return False, None

        resp: CloudSyncToken = CloudSyncToken(**auth.json())
        self.__write_auth_file(resp)
        return True, resp

    def __is_jwt_valid(self) -> bool:
        auth = self.__read_auth_file(kind=AuthKind.TOKEN)
        if auth is None:
            return False

        claims = jwt.decode(auth.token, options={"verify_signature": False})
        expires_at = claims.get("exp")

        return time.time() < expires_at

    def __get_jwt_token(self) -> str | None:
        auth = self.__read_auth_file(kind=AuthKind.TOKEN)
        if auth is None:
            return None

        claims = jwt.decode(auth.token, options={"verify_signature": False})
        expires_at = claims.get("exp")

        if time.time() < expires_at:
            return auth.token

        success, resp = self.__authorize()
        if success and resp is not None:
            return resp.token

        return None

    def __sign_in(self) -> bool:
        success, resp = self.__authenticate()
        if not success or not resp:
            return False

        success, _ = self.__authorize()
        return success

    def get_cloud_config(self) -> CloudConfigResponse | None:
        config = self.__client.get(
            f"{self.__data_url}/config",
            headers={
                "Accept": "application/vnd.pgrst.object+json",
                "Authorization": f"Bearer {self.__get_jwt_token()}",
            }
        )

        if config.status_code == 406:
            if self.logging:
                log.info("There was no matching config stored on cloud")
            return None
        elif not config.is_success:
            if self.logging:
                log.error(f"Could not get cloud config: {config.reason_phrase}")
            return None

        response = CloudConfigResponse(**config.json())

        return response

    def sync_local(self, local_config: Config):
        if not self.__is_jwt_valid():
            self.__sign_in()

        if self.logging:
            log.info("Starting Cloud Sync")

        remote_conf = self.get_cloud_config()
        if not remote_conf:
            raise ValueError("Could not get cloud config")

        local_version = local_config.cloud.version

        if remote_conf.version >= local_version:
            if self.logging:
                log.info(f"Local/Remote Versions:\n{local_version}/{remote_conf.version}")
            return

        # construct a payload to upload to the cloud
        patch = self.__client.patch(
            f"{self.__data_url}/config",
            params={
                "id": f"eq.{remote_conf.id}",
                "version": f"eq.{remote_conf.version}"
            },
            headers={
                "Accept": "application/vnd.pgrst.object+json",
                "Authorization": f"Bearer {self.__get_jwt_token()}",
                "Prefer": "return=representation"
            },
            json={
                "json": local_config.model_dump(mode="json"),
                "version": local_version
            }
        )

        if patch.is_success:
            if self.logging:
                log.info(f"Config Version: '{local_config}' Synced")
        else:
            if self.logging:
                log.error(f"Could not sync config: {patch.reason_phrase}")

    def start(self, centre, sync_event: Event):
        sign_in = self.__read_auth_file(kind=AuthKind.SIGN_IN)
        auth = self.__read_auth_file(kind=AuthKind.TOKEN)

        if (None in (auth, sign_in)) or not self.__is_jwt_valid():
            success = self.__sign_in()
            if not success:
                raise ConnectionError("Sign In failed")

        self.sync_local(local_config=centre.config)

        while True:
            # Wait for first edit
            sync_event.wait()

            while True:
                sync_event.clear()
                # reset the timer if any edit occurs withing the 60 seconds window
                if sync_event.wait(timeout=60):
                    continue

                # break out of the loop and eventually sync with remote
                break

            self.sync_local(local_config=centre.config)
