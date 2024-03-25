# v412-ctl
Linux v412-ctl integration for HA, depends on using a custom API Flask app, which should likely be set as a system service on the device running the cameras and API and should be placed underneath a deployment infrastructure such as gunicorn (which is what I am using on my production instance)


TODO:  
An actual how-to for installing the integration since it is not HACS linked (and may not ever be tbh)
code comments
how to actually deploy the API in a system service using gunicorn, or just using python for testing since the Flask app call is slightly different

... prob more shit tbh
