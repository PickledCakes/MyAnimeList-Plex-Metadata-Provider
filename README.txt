MAL Plex Custom Metadata Provider v1.5
======================================

EASIEST INSTALL
---------------
1. Extract this folder.
2. Run INSTALL_AND_START.bat.
3. Approve the administrator prompt.
4. Add this provider URL to Plex:

   http://127.0.0.1:4567/tv

The installer starts the provider and creates a Windows Scheduled Task named:

   MAL Plex Metadata Provider

It starts automatically whenever Windows boots, before any user signs in.

SETTINGS
--------
Run EDIT_SETTINGS.bat, edit settings.json, save, then restart using:

   STOP_PROVIDER_TASK.bat
   START_PROVIDER_TASK.bat

The _help section in settings.json lists all accepted values and is ignored by
the provider.

USEFUL FILES
------------
INSTALL_AND_START.bat   One-click install, startup registration, and launch
REGISTER_STARTUP.bat    Register or repair automatic startup
UNREGISTER_STARTUP.bat  Remove automatic startup
START_PROVIDER_TASK.bat Start the background provider
STOP_PROVIDER_TASK.bat  Stop the background provider
VIEW_LOG.bat            Open logs\provider.log
RUN_PROVIDER.bat        Interactive troubleshooting run
TEST_PROVIDER.bat       Basic connectivity test
BUILD_EXE.bat           Build a standalone EXE for release maintainers

See README.md for complete GitHub and release instructions.
