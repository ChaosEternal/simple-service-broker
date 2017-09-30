curl -v -H "X-Broker-Api-Version: 2.3" http://$USER:$PASS@$URI/v2/service_instances/$SII -X PUT -H "Content-Type: application/json" -d '
{"service_id":"$SI",
 "plan_id":"$PI"}
'
