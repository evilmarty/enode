# Enode

** This integration is still in development and is currently configured to use Enode's sandbox environment. **

## Description

Home Assistant integration for [Enode](https://enode.com), a service that provides integrations with 80+ OEMS and 1000+ energy devices.

## Installation

There are two ways this integration can be installed into [Home Assistant](https://www.home-assistant.io).

The easiest way is to install the integration using [HACS](https://hacs.xyz).

Alternatively, installation can be done manually by copying the files in this repository into the custom_components directory in the HA configuration directory:

1. Open the configuration directory of your HA configuration.
2. If you do not have a custom_components directory, you need to create it.
3. In the custom_components directory create a new directory called enode.
4. Copy all the files from the custom_components/enode/ directory in this repository into the enode directory.
5. Restart Home Assistant
6. Add the integration to Home Assistant (see `Configuration`)

### Configuration

A registered [Enode Developer](https://developers.enode.com/register) account is required before proceeding.

#### Create an Enode client

1. Create a new client from the [Enode Developers dashboard](https://developers.enode.com/dashboard).
2. Select sandbox as the client environment if that is the only option. After you create the client you will have to contact their sales team to request it be granted production access.
3. Create API credentials for the newly created client.

#### Add the Enode integration

1. [Add the Enode intregration in Home Assistant](https://my.home-assistant.io/redirect/config_flow_start/?domain=enode)
  1. Goto the Configuration -> Integrations page.
  2. On the bottom right of the page, click on the + Add Integration sign to add an integration.
  3. Search for Enode. (If you don't see it, try refreshing your browser page to reload the cache.)
2. Provide the client credentials (see [Create an Enode client])
3. Optionally, you can change the user ID that is used for linking devices. Defaults to the client ID.
4. Click Submit so add the integration.

## Linking a new device

To link a new device that hasn't been integrated with Enode yet.

1. Navigate to the [Enode integration](https://my.home-assistant.io/redirect/integration/?domain=enode) that has been configured.
2. Select "Link a device" from the menu next to the configured integration.
3. Follow the instructions to select the vendor and supported device to link.