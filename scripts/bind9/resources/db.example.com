; example.com
$ORIGIN example.com.
$TTL 1h
@ IN SOA ns admin@example.com. ( ${DATE} 1d 2h 1w 30s )
@ NS ns
ns A ${ADDRESS}
