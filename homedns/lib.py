import logging
import os
import sqlite3
from collections import namedtuple
from typing import Any, AnyStr, Final, List, Optional, Tuple

from dnslib import QTYPE, RR, DNSHeader, DNSRecord

from .constants import IN, RESP_BLK, RESP_FWD, RESP_OK
from .utils import RecordFactory

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger: Final = logging.getLogger(__name__)

# definition of query results from sqlite3
QueryItem = namedtuple("QueryItem", ["value", "TTL"])

# query record from sqlite file
def query_db(qname: str, qtype: str, db_path: str) -> List[Any]:
    logger.debug("querying from databases")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    query_tuple = (int(getattr(QTYPE, qtype)), qname)

    c.execute(
        """SELECT VALUE, TTL FROM RECORDS WHERE RECORD_TYPE=? AND DOMAIN=?;""",
        query_tuple,
    )
    ret = c.fetchall()
    conn.close()
    logger.debug(ret)
    return ret


def dns_response(
    data: AnyStr, db_path: str, protocol_type: AnyStr, deny_types: List
) -> Tuple[int, Optional[AnyStr]]:
    # decode a DNS packet
    request = DNSRecord.parse(data)
    qname = request.q.qname
    qn = str(qname)
    qtype = QTYPE[request.q.qtype]

    # query type is in denied types
    if (qtype in deny_types) or ("*" in deny_types):
        logger.warning("query has blocked.")
        return (RESP_BLK, None)

    # qr is a bit for distingushing queries(0) and reponses(1)
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    if qn.endswith("."):
        query_result = query_db(qn.rstrip("."), qtype, db_path)
    else:
        query_result = query_db(qn, qtype, db_path)

    # hit
    if len(query_result) != 0:
        for _item in map(QueryItem._make, query_result):
            rdata = RecordFactory(qtype, _item.value, logger)
            reply.add_answer(
                RR(
                    rname=qname,
                    rtype=getattr(QTYPE, qtype),
                    rclass=IN,
                    ttl=_item.TTL,
                    rdata=rdata,
                )
            )
    # need forward
    else:
        return (RESP_FWD, None)
    logger.debug("Reply: %s\n", reply)

    return (RESP_OK, reply.pack())


__all__ = ["dns_response"]
