from typing import ClassVar, Mapping, Any, Dict, Optional, Tuple, List
from typing_extensions import Self

from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName, ResponseMetadata
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.media.video import CameraMimeType, NamedImage
from viam.utils import struct_to_dict

from viam.components.camera import (
    Camera,
    ViamImage,
    IntrinsicParameters,
    DistortionParameters,
)
from viam.logging import getLogger

import requests

LOGGER = getLogger(__name__)
DEFAULT_HOST_ADDRESS = "homeassistant.local:8123"


class Client:
    """Session wrapper for communicating with HA API."""

    def __init__(self, host_address: str, access_token: str) -> None:
        self.host_address = host_address
        self.access_token = access_token
        self.session = requests.Session()
        return

    def close(self) -> None:
        self.session.close()

    def camera_proxy(self, entity_id: str) -> None | bytes:
        """Retrieve latest image from camera, in bytes"""
        response = self.session.get(
            f"{self.host_address}/api/camera_proxy/{entity_id}",
            headers=self.headers,
        )
        if response.raise_for_status() is None:
            return response.content

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }


class homeassistant(Camera, Reconfigurable):
    MODEL: ClassVar[Model] = Model(
        ModelFamily("hipsterbrown", "camera"), "homeassistant"
    )

    host_address: str
    access_token: str
    entity_id: str
    client: Client

    # Constructor
    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        my_class = cls(config.name)
        my_class.reconfigure(config, dependencies)
        return my_class

    # Validates JSON Configuration
    @classmethod
    def validate(cls, config: ComponentConfig):
        attrs = struct_to_dict(config.attributes)
        # validate config
        access_token = attrs.get("access_token", "")
        if access_token == "":
            raise Exception("An access_token must be provided")

        entity_id = attrs.get("entity_id", "")
        if entity_id == "":
            raise Exception("An entity_id must be defined")

        return []

    # Handles attribute reconfiguration
    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        attrs = struct_to_dict(config.attributes)
        # here we initialize the resource instance
        self.host_address = attrs.get("host_address", DEFAULT_HOST_ADDRESS)
        self.access_token = attrs.get("access_token", "")
        self.entity_id = attrs.get("entity_id", "")
        self.client = Client(
            self.host_address,
            self.access_token,
        )
        return

    """ Implement the methods the Viam RDK defines for the Camera API (rdk:components:camera) """

    async def get_image(
        self,
        mime_type: str = "",
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> ViamImage:
        """Get the next image from the camera as an Image or RawImage.
        Be sure to close the image when finished.

        NOTE: If the mime type is ``image/vnd.viam.dep`` you can use :func:`viam.media.video.RawImage.bytes_to_depth_array`
        to convert the data to a standard representation.

        Args:
            mime_type (str): The desired mime type of the image. This does not guarantee output type

        Returns:
            ViamImage: The frame
        """
        bytes = self.client.camera_proxy(self.entity_id)
        if bytes is not None:
            return ViamImage(bytes, CameraMimeType.JPEG)
        return ViamImage(b"", CameraMimeType.JPEG)

    async def get_images(
        self, *, timeout: Optional[float] = None, **kwargs
    ) -> Tuple[List[NamedImage], ResponseMetadata]:
        """Get simultaneous images from different imagers, along with associated metadata.
        This should not be used for getting a time series of images from the same imager.

        Returns:
            Tuple[List[NamedImage], ResponseMetadata]:
                - List[NamedImage]:
                  The list of images returned from the camera system.

                - ResponseMetadata:
                  The metadata associated with this response
        """
        raise NotImplementedError("Method is not available for this module")

    async def get_point_cloud(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Tuple[bytes, str]:
        """
        Get the next point cloud from the camera. This will be
        returned as bytes with a mimetype describing
        the structure of the data. The consumer of this call
        should encode the bytes into the formatted suggested
        by the mimetype.

        To deserialize the returned information into a numpy array, use the Open3D library.
        ::

            import numpy as np
            import open3d as o3d

            data, _ = await camera.get_point_cloud()

            # write the point cloud into a temporary file
            with open("/tmp/pointcloud_data.pcd", "wb") as f:
                f.write(data)
            pcd = o3d.io.read_point_cloud("/tmp/pointcloud_data.pcd")
            points = np.asarray(pcd.points)

        Returns:
            bytes: The pointcloud data.
            str: The mimetype of the pointcloud (e.g. PCD).
        """
        raise NotImplementedError("Method is not available for this module")

    async def get_properties(
        self, *, timeout: Optional[float] = None, **kwargs
    ) -> Camera.Properties:
        """
        Get the camera intrinsic parameters and camera distortion parameters

        Returns:
            Properties: The properties of the camera
        """
        return Camera.Properties(False, IntrinsicParameters(), DistortionParameters())
