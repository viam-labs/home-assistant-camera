"""
This file registers the model with the Python SDK.
"""

from viam.components.camera import Camera
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .homeassistant import homeassistant

Registry.register_resource_creator(
    Camera.SUBTYPE,
    homeassistant.MODEL,
    ResourceCreatorRegistration(homeassistant.new, homeassistant.validate),
)
