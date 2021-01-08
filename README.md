## Intro
![flake8](https://github.com/EvanMu96/dns_test/workflows/Lint/badge.svg)  
A toy DNS server suppport local record and query forwarding.  
Now it supports a few query types in local database.
- A
- AAAA
- CNAME  
- NS
- MX
  
And it can forward arbitrary queries to root servers.

## Install
```Python
pip install -r requirements.txt
```

## Learn More About DNS
[CLODFLARE DNS](https://www.cloudflare.com/zh-cn/learning/dns/dns-records/)