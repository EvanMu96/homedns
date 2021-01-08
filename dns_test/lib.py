import logging
import os
import sqlite3
from typing import Any, AnyStr, Final, List, Optional, Tuple

from dnslib import AAAA, CNAME, QTYPE, RR, A, DNSHeader, DNSRecord, NS, MX

from .config import db_path

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
Log: Final = logging.getLogger(__name__)

IN: Final[int] = 1

RESP_OK, RESP_FWD, RESP_BLK = 0, 1, 2

# imporvement
def RecordFactory(qtype: str, data: str) -> Any:
    if qtype == "A":
        return A(data)
    elif qtype == "CNAME":
        return CNAME(data)
    elif qtype == "AAAA":
        return AAAA(data)
    elif qtype == "NS":
        return NS(data)
    elif qtype == "MX":
        pref, entry = data.split()
        print(pref, entry)
        return MX(preference=int(pref), label=entry)
    else:
        Log.error("not implemented query type")


# query record from sqlite file
def query_db(qname: str, qtype: str) -> List[Any]:
    Log.debug("querying from databases")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    query_tuple = (int(getattr(QTYPE, qtype)), qname)

    c.execute(
        """SELECT VALUE, TTL FROM RECORDS WHERE RECORD_TYPE=? AND DOMAIN=?;""",
        query_tuple,
    )
    ret = c.fetchall()
    conn.close()
    Log.debug(ret)
    return ret


# 0: query sucess
# 1: need forwarding
# 2: blocked
# make dns response
def dns_response(
    data: AnyStr, protocol_type: AnyStr, deny_types: List
) -> Tuple[int, Optional[AnyStr]]:
    # decode a DNS packet
    request = DNSRecord.parse(data)
    qname = request.q.qname
    qn = str(qname)
    qtype = QTYPE[request.q.qtype]

    # query type is in denied types
    if (qtype in deny_types) or ("*" in deny_types):
        Log.warning("query has blocked.")
        return (RESP_BLK, None)

    # qr is a bit for distingushing queries(0) and reponses(1)
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    if qn.endswith("."):
        query_result = query_db(qn.rstrip("."), qtype)
    else:
        query_result = query_db(qn, qtype)

    # hit
    if len(query_result) != 0:
        for value, TTL in query_result:
            rdata = RecordFactory(qtype, value)
            reply.add_answer(
                RR(
                    rname=qname,
                    rtype=getattr(QTYPE, qtype),
                    rclass=IN,
                    ttl=TTL,
                    rdata=rdata,
                    
                )
            )
    # need forward
    else:
        return (RESP_FWD, None)
    Log.debug("Reply:%s\n", reply)

    return (RESP_OK, reply.pack())


__all__ = ["dns_response"]
