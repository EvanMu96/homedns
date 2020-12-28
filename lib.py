import sqlite3
import logging
import os
from typing import Optional, Any, AnyStr, Final, List
from dnslib import A, AAAA, CNAME, RR, DNSRecord, QTYPE, DNSHeader

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
def query_db(qname: str, qtype: str) -> Optional[List[Any]]:
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
def dns_response(data: AnyStr, protocol_type: AnyStr) -> AnyStr:
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

    if query_result is not None:
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

    Log.info("---- Reply:%s\n", reply)

    return reply.pack()


__all__ = ["dns_response"]
