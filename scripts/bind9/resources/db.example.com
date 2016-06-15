; example.com
\$ORIGIN example.com.
\$TTL 1h
@ IN SOA ns admin\@example.com. ( $(date +%Y%m%d%H) 1d 2h 1w 30s )
@ NS ns
ns A $(hostname -I)
