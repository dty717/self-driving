#include "packet.h"
#include "kex.h"

#define PACKET_MAX_SIZE (256 * 1024)

struct packet_state {
	u_int32_t seqnr;
	u_int32_t packets;
	u_int64_t blocks;
	u_int64_t bytes;
};
