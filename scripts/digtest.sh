#! /usr/bin/env bash
dig @127.0.0.1 -p 8053 test.com
dig @127.0.0.1 -p 8053 test.com +tcp
dig @127.0.0.1 -p 8053 google.com
dig @127.0.0.1 -p 8053 google.com +tcp
dig @127.0.0.1 -p 8053 test.com NS
dig @127.0.0.1 -p 8053 google.com MX
dig @127.0.0.1 -p 8053 testipv6.com AAAA
dig @127.0.0.1 -p 8053 testcname.com CNAME