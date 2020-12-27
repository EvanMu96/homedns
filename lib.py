import sqlite3
import logging
import os
from typing import Optional, Any, AnyStr, Final
from dnslib import *

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
Log: Final = logging.getLogger(__name__)

TTL: Final[int] = 60 * 5

IN: Final[int] = 1


# query record from sqlite file
def query_db(qname: AnyStr, protocol_type: AnyStr) -> Optional[Any]:
    c = sqlite3.connect("dns_records.db").cursor()
    c.execute("""SELECT IP FROM DNS_A WHERE DOMAIN='{}' """.format(qname))
    return c.fetchone()


# make dns response
def dns_response(data: AnyStr, protocol_type: AnyStr) -> AnyStr:
    # decode a DNS packet
    request = DNSRecord.parse(data)

    Log.info("starting response: %s", request)
    # qr is a bit for distingushing queries(0) and reponses(1)
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    qname = request.q.qname
    qn = str(qname)
    qtype = request.q.qtype
    qt = QTYPE[qtype]

    if qt:
        pass

    if qn.endswith("."):
        query_result = query_db(qn.rstrip("."), protocol_type)
    else:
        query_result = query_db(qn, protocol_type)
    if query_result[0] is not None:
        rdata = A(query_result[0])
        reply.add_answer(
            RR(rname=qname, rtype=getattr(QTYPE, "A"), rclass=IN, ttl=TTL, rdata=rdata)
        )

    Log.info("---- Reply:%s\n", reply)

    return reply.pack()


__all__ = ["dns_response"]
