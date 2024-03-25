# v412-ctl
Linux v412-ctl integration for HA, depends on using a custom API Flask app, which should likely be set as a system service on the device running the cameras and API and should be placed underneath a deployment infrastructure such as gunicorn (which is what I am using on my production instance)
