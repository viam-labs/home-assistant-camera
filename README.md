# Home Assistant Camera Modular Component

_home-assistant-camera_ is a Viam modular component that provides a proxy camera for entities in [Home Assistant](https://www.home-assistant.io/) via the local [REST API](https://developers.home-assistant.io/docs/api/rest).

## Prerequisites

[Follow the instructions for enabling the REST API in your instance of Home Assistant](https://developers.home-assistant.io/docs/api/rest). The "Long-Lived Access Token" created through that process will be used by this component.

The Home Assistant instance should have at least one [camera integration](https://www.home-assistant.io/integrations/#camera) set up.

Whichever machine is running `viam-server` should be on the same network as Home Assistant, unless it has been opened to the public Internet.

## Viam Module Configuration

**host_address** (Optional):
This is the URL used to access Home Assistant, including the port number if applicable. This could be an IP address or mDNS name as well. 
Defaults to "homeassistant.local:8123"

**access_token** *Required*:
This is the "Long-Lived Access Token" created in the Home Assistant [Profile settings](https://www.home-assistant.io/docs/authentication/#your-account-profile).

**entity_id** *Required*:
This is the identifier name of the Camera entity defined in Home Assistant. A list of all available entities on the Home Assistant instance can be found at `<host_address>/config/entities` (with `<host_address>` filled in with the attribute described above).

## SDK Usage

After adding and configuring this module for your machine through the Viam app, the "Code Sample" tab will demonstrate how to use it with the SDK:

```python
import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.camera import Camera

async def connect():
    creds = Credentials(
        type='robot-location-secret',
		# Replace "<SECRET>" (including brackets) with your robot's secret
        payload='<SECRET>')
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address('<Robot Location>', opts)

async def main():
    robot = await connect()

    print('Resources:')
    print(robot.resource_names)
    
    # backyard
    backyard = Camera.from_robot(robot, "backyard")
    backyard_return_value = await backyard.get_image()
    print(f"backyard get_image return value: {backyard_return_value}")

    # Don't forget to close the robot when you're done!
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
```
