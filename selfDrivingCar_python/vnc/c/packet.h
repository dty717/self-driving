#include "common.h"
#include "kex.h"

struct sshkey;
struct sshbuf;
struct session_state;	/* private session data */

// struct ssh {
// 	/* Session state */
// 	struct session_state *state;

// 	/* Key exchange */
// 	struct kex *kex;

// 	/* Cached remote ip address and port*/
// 	char *remote_ipaddr;
// 	int remote_port;

// 	/* Dispatcher table */
// 	dispatch_fn *dispatch[DISPATCH_MAX];
// 	/* number of packets to ignore in the dispatcher */
// 	int dispatch_skip_packets;

// 	/* datafellows */
// 	int compat;

// 	/* Authentication context */
// 	void *authctxt;

// 	/* Host key verification */
// 	char *host;
// 	struct sockaddr *hostaddr;

// 	/* Lists for private and public keys */
// 	TAILQ_HEAD(, key_entry) private_keys;
// 	TAILQ_HEAD(, key_entry) public_keys;

// 	/* APP data */
// 	void *app_data;
// };