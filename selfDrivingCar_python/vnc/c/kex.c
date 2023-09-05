#include <stdio.h>
#include "kex.h"
#include "digest.h"
#include "openssl/obj_mac.h"


/* prototype */
static int kex_choose_conf(struct ssh *);
static int kex_input_newkeys(int, u_int32_t, struct ssh *);

static const char *proposal_names[PROPOSAL_MAX] = {
	"KEX algorithms",
	"host key algorithms",
	"ciphers ctos",
	"ciphers stoc",
	"MACs ctos",
	"MACs stoc",
	"compression ctos",
	"compression stoc",
	"languages ctos",
	"languages stoc",
};

struct kexalg {
	char *name;
	u_int type;
	int ec_nid;
	int hash_alg;
};
static const struct kexalg kexalgs[] = {
#ifdef WITH_OPENSSL
	{ KEX_DH1, KEX_DH_GRP1_SHA1, 0, SSH_DIGEST_SHA1 },
	{ KEX_DH14, KEX_DH_GRP14_SHA1, 0, SSH_DIGEST_SHA1 },
	{ KEX_DHGEX_SHA1, KEX_DH_GEX_SHA1, 0, SSH_DIGEST_SHA1 },
	{ KEX_DHGEX_SHA256, KEX_DH_GEX_SHA256, 0, SSH_DIGEST_SHA256 },
	{ KEX_ECDH_SHA2_NISTP256, KEX_ECDH_SHA2,
	    NID_X9_62_prime256v1, SSH_DIGEST_SHA256 },
	{ KEX_ECDH_SHA2_NISTP384, KEX_ECDH_SHA2, NID_secp384r1,
	    SSH_DIGEST_SHA384 },
	{ KEX_ECDH_SHA2_NISTP521, KEX_ECDH_SHA2, NID_secp521r1,
	    SSH_DIGEST_SHA512 },
#endif
	{ KEX_CURVE25519_SHA256, KEX_C25519_SHA256, 0, SSH_DIGEST_SHA256 },
	{ NULL, -1, -1, -1},
};

char *
kex_alg_list(char sep)
{
	char *ret = NULL, *tmp;
	size_t nlen, rlen = 0;
	const struct kexalg *k;

	for (k = kexalgs; k->name != NULL; k++) {
		if (ret != NULL)
			ret[rlen++] = sep;
		nlen = strlen(k->name);
		if ((tmp = realloc(ret, rlen + nlen + 2)) == NULL) {
			free(ret);
			return NULL;
		}
		ret = tmp;
		memcpy(ret + rlen, k->name, nlen + 1);
		rlen += nlen;
	}
	return ret;
}

static const struct kexalg *
kex_alg_by_name(const char *name)
{
	const struct kexalg *k;

	for (k = kexalgs; k->name != NULL; k++) {
		if (strcmp(k->name, name) == 0)
			return k;
	}
	return NULL;
}

int main()
{
	kex_alg_by_name("ecdh-sha2-nistp521");
    printf(kex_alg_list('\n'));
    printf("\n");
    return 0;
}
