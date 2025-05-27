# Enode

Home Assistant integration for [Enode](https://enode.com), a service that provides integrations with 80+ OEMS and 1000+ energy devices.

Note: Device support is limited to vehicles only. Please request support for other devices if interested.

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
The account initially is limited to only be able to create sandbox clients. You will have to contact Enode's
sales team to request they grant you the ability to create production clients.

Note: This may take several days and you may not receive a notification once it has been fulfilled. It may
be best to check daily whether you are able to create production clients.

#### Create an Enode client

1. Create a new client from the [Enode Developers dashboard](https://developers.enode.com/dashboard).
2. Select production as the client environment. If you cannot then see note above.
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

## Enabling webhooks

Webhooks allow Enode's API to send updates to the Enode integration providing quicker feedback and updates instead of relying on
periodic updates. This integration allows enabling, disabling, as well as testing webhooks to ensure the connectivity is working.

Webhooks can be enabled and disabled at any time and does not affect the integration.

To be able to use webhooks your Home Assistant installing must fufill the following criteria:

* Be externally accessible
  1. Is configured with [an external URL](https://my.home-assistant.io/redirect/network/).
  2. Is SSL
  3. Is accessible by Enode's servers. If you need to whitelist their IP addresses see [Enode's information](https://developers.enode.com/docs/webhooks#ip-addresses).
* Have a Home Assistant cloud subscription (unverified)

### To enable webhooks

1. Navigate to the [Enode integration](https://my.home-assistant.io/redirect/integration/?domain=enode) that has been configured.
2. Select "Manage Webhook" from the menu next to the configured integration.
3. Select "Enable Webhook" from the menu options.

### To test webhooks

1. Navigate to the [Enode integration](https://my.home-assistant.io/redirect/integration/?domain=enode) that has been configured.
2. Select "Manage Webhook" from the menu next to the configured integration.
3. Select "Test Webhook" from the menu options.

### To disable webhooks

1. Navigate to the [Enode integration](https://my.home-assistant.io/redirect/integration/?domain=enode) that has been configured.
2. Select "Manage Webhook" from the menu next to the configured integration.
3. Select "Disable Webhook" from the menu options.

# TODO

* [ ] Verify cloud support for webhooks
* [ ] Add support for vehicle smart charging
