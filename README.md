# Home Assistant Integration - Ombi

This project is a custom integration for Home Assistant which adds sensors displaying information from an Ombi instance.

The following is available.

# Installation

1. Add a directory named *custom_components* to your Home Assistant root directory if you do not already have one.
2. Create a directory named *ombi* inside the custom_components directory.
3. Download the latest release from this repo and add the files to the directory you created.
4. Done! See examples under *Usage*.

# Usage

## Configuration variables


**api_key** (required)  
API key from ombi found under Settings/Ombi on your Ombi page.

**host**  
The host Ombi is running on.

**port**  
The port Ombi is running on.

**ssl**   
Whether to or not to use ssl.

**urlbase**   
The base URL Ombi is running under.

**monitored_conditions**  
Conditions to monitor (defaults to all).

- movies
- tv
- pending
- recentlyaddedmovies
- recentlyaddedtv


## Examples
```yaml
sensor:
  - platform: ombi
    api_key: 46p2tsioswcdoifbstgu6kr6xuq4n4fa
    host: 192.168.1.120
    port: 3579
    ssl: false
```

```yaml
sensor:
  - platform: ombi
    api_key: 46p2tsioswcdoifbstgu6kr6xuq4n4fa
    host: myserver.com
    port: 443
    ssl: true
    urlbase: ombi/
    monitored_conditions:
      - movies
      - pending
      - recentlyaddedtv
```

# Links

* Ombi: https://ombi.io/
* Home Assistant: https://www.home-assistant.io/

# License

This project is licensed under the MIT License - see the LICENSE.txt file for details.
