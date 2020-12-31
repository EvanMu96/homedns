import logging
import os
import sqlite3
from typing import Any, AnyStr, Final, List, Optional

from dnslib import AAAA, CNAME, QTYPE, RR, A, DNSHeader, DNSRecord

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
Log: Final = logging.getLogger(__name__)


IN: Final[int] = 1

# imporvement
def RecordFactory(qtype: str) -> Any:
    if qtype == "A":
        return A
    elif qtype == "CNAME":
        return CNAME
    elif qtype == "AAAA":
        return AAAA
    else:
        Log.error("not implemented query type")


# query record from sqlite file
def query_db(qname: str, qtype: str) -> List[Any]:
    conn = sqlite3.connect("dns_records.db")
    c = conn.cursor()
    query_tuple = (int(getattr(QTYPE, qtype)), qname)

    c.execute(
        """SELECT VALUE, TTL FROM RECORDS WHERE RECORD_TYPE=? AND DOMAIN=?;""",
        query_tuple,
    )
    ret = c.fetchall()
    conn.close()
    return ret


# make dns response
def dns_response(data: AnyStr, protocol_type: AnyStr) -> Optional[Any]:
    # decode a DNS packet
    request = DNSRecord.parse(data)

    Log.info("starting response: %s", request)
    # qr is a bit for distingushing queries(0) and reponses(1)
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    qname = request.q.qname
    qn = str(qname)
    qtype = QTYPE[request.q.qtype]

    if qn.endswith("."):
        query_result = query_db(qn.rstrip("."), qtype)
    else:
        query_result = query_db(qn, qtype)

    # hit
    if len(query_result) != 0:
        for value, TTL in query_result:
            rdata = RecordFactory(qtype)(value)
            reply.add_answer(
                RR(
                    rname=qname,
                    rtype=getattr(QTYPE, qtype),
                    rclass=IN,
                    ttl=TTL,
                    rdata=rdata,
                )
            )
    # fail
    else:
        return None
    Log.info("---- Reply:%s\n", reply)

    return reply.pack()


__all__ = ["dns_response"]
