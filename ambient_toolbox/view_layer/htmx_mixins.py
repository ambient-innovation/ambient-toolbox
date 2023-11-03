import json
from typing import Dict, Union


class HtmxResponseMixin:
    """
    View mixin to be able to simply set "HX-Redirect" and "HX-Trigger" for using HTMX in the frontend.
    "hx_redirect_url": Takes a reverse_lazy URL to a valid Django URL
    "hx_trigger": Takes either a string "updateComponentX" or a dictionary with a key-value-pair, where the key is
    the signal and the value is a parameter passed to the frontend. If you don't need the value, set it to None.
    """

    hx_redirect_url: str = None
    hx_trigger: Union[str, Dict[str, str]] = None

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        # Get attributes
        hx_redirect_url = self.get_hx_redirect_url()
        hx_trigger = self.get_hx_trigger()

        # Set redirect header if set
        if hx_redirect_url:
            response["HX-Redirect"] = hx_redirect_url

        # Set trigger header if set
        if isinstance(hx_trigger, dict):
            response["HX-Trigger"] = json.dumps(hx_trigger)
        elif isinstance(hx_trigger, str):
            response["HX-Trigger"] = hx_trigger

        # Return augmented response
        return response

    def get_hx_redirect_url(self):
        """
        Getter for "hx_redirect_url" to be able to work with dynamic data
        """
        return self.hx_redirect_url

    def get_hx_trigger(self):
        """
        Getter for "hx_trigger" to be able to work with dynamic data
        """
        return self.hx_trigger
