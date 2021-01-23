## Intro
![flake8](https://github.com/EvanMu96/dns_test/workflows/Lint/badge.svg)  
A toy DNS server suppport local record and query forwarding.  
Now it supports a few query types in local database.
- A
- AAAA
- CNAME  
- NS
- MX
  
And it support normal plain-text DNS to DoT/DoH forwarding. You can use it as a DoT/DoH proxy.

## To do
- [x] DoT
- [ ] DoH
- [ ] Optimization

## Usage
Please sure that you have installed sqlite3, for Ubuntu users
```bash
sudo apt-get install sqlite3
```
then,
```bash
# install dependencies
pip install -r requirements.txt
# initialize database
mkdir data && sqlite3 data/dns_records.db < scripts/schema.sql
```
now you can insert your own entries by sqlite3
```bash
sqlite3 data/dns_records.db < "INSERT INTO RECORDS ( DOMAIN, RECORD_TYPE, VALUE)
VALUES ( 'test.com', 1, '1.1.1.1');"
```
edit config instance in `main.py`, for example
```Python 
config = Config(
    roots=[
        ("192.168.102.81", None),
        ("114.114.114.114", None),
    ],
    db_path="data/dns_records.db",
    # when encrypted_roots in set, only encrpted roots take effect not unencrpted roots.
    # encrypted_roots=[("1.1.1.1", "cloudflare-dns.com", None)], 
    client_denylist=[
        ("192.168.56.103", "*"),
        ("192.168.56.102", "A"),
    ],
)
```
save and start DNS server, the default port is 8053
```bash
python main.py --port=<port>
```

## Learn More About DNS
[CLOUDFLARE DNS](https://www.cloudflare.com/zh-cn/learning/dns/dns-records/)  
[RFC 1035](https://tools.ietf.org/html/rfc1035)  
[CLOUDFLARE DoT/DoH](https://developers.google.com/speed/public-dns/docs/doh)  
[Google DNS DoH](https://developers.google.com/speed/public-dns/docs/doh)  