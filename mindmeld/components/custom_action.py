import asyncio
import logging

import aiohttp
import requests


logger = logging.getLogger(__name__)


class CustomActionException(Exception):
    pass


class CustomAction:
    """
    This class allows the client to send Request and Responder to another server and return the
      the directives and frame in the response.
    """

    def __init__(self, name: str = None, config: dict = None):
        self._name = name
        self._config = config or {}
        self.url = self._config.get("url")

    def get_json_payload(self, request, responder):
        request_json = {
            "text": request.text,
            "domain": request.domain,
            "intent": request.intent,
            "context": dict(request.context),
            "params": request.params.to_dict(),
            "frame": dict(request.frame),
        }
        responder_json = {"directives": responder.directives, "frame": responder.frame}
        return {
            "request": request_json,
            "responder": responder_json,
            "action": self._name,
        }

    def invoke(self, request, responder, asynch=False):
        """Invoke the custom action with Request and Responder and return True if the action is
        executed successfully, False otherwise. Upon successful execution, we update the Frame
        and Directives of the Responder object.

        Args:
            request (Request)
            responder (DialogueResponder)
            asynch (bool): Whether we should invoke this payload asynchronously

        Returns:
            (bool)
        """
        if not self.url:
            raise CustomActionException(
                "No URL is given for custom action {}.".format(self._name)
            )

        json_data = self.get_json_payload(request, responder)

        try:
            status_code, result_json = self.post(json_data, asynch=asynch)

            if status_code == 200:
                fields = ["frame", "directives"]
                for field in fields:
                    if field not in result_json:
                        logger.warning(
                            "`%s` not in the response of custom action %s",
                            field,
                            self._name,
                        )
                responder.frame.update(result_json.get("frame", {}))
                responder.directives.extend(result_json.get("directives", []))
                return True
            else:
                logger.error(
                    "Error %s trying to reach custom action server %s.",
                    status_code,
                    self.url,
                )
                return False
        except ConnectionError:
            logger.error(
                "Connection error trying to reach custom action server %s.", self.url
            )
            return False

    def post(self, json_data, asynch=False):
        if asynch:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.post_async(json_data))
        else:
            result = requests.post(url=self.url, json=json_data)
            if result.status_code == 200:
                return 200, result.json()
            else:
                return result.status_code, {}

    async def post_async(self, json_data):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=json_data) as response:
                if response.status == 200:
                    json_resonse = await response.json()
                    return 200, json_resonse
                else:
                    return response.status, {}

    def invoke_async(self, request, responder):
        """Asynchronously invoke the custom action with Request and Responder and return True if
        the action is executed successfully, False otherwise. Upon successful execution, we update
        the Frame and Directives of the Responder object.

        Args:
            request (Request)
            responder (DialogueResponder)

        Returns:
            (bool)
        """
        return self.invoke(request, responder, asynch=True)
