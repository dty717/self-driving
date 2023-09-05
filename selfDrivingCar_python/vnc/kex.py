from digest import *
from init import *
from openssl.obj_mac import *
KEX_COOKIE_LEN = 16

KEX_DH1 = "diffie-hellman-group1-sha1"
KEX_DH14 = "diffie-hellman-group14-sha1"
KEX_DHGEX_SHA1 = "diffie-hellman-group-exchange-sha1"
KEX_DHGEX_SHA256 = "diffie-hellman-group-exchange-sha256"
KEX_ECDH_SHA2_NISTP256 = "ecdh-sha2-nistp256"
KEX_ECDH_SHA2_NISTP384 = "ecdh-sha2-nistp384"
KEX_ECDH_SHA2_NISTP521 = "ecdh-sha2-nistp521"
KEX_CURVE25519_SHA256 = "curve25519-sha256@libssh.org"


KEX_DH_GRP1_SHA1 = 0
KEX_DH_GRP14_SHA1 = 1
KEX_DH_GEX_SHA1 = 2
KEX_DH_GEX_SHA256 = 3
KEX_ECDH_SHA2 = 4
KEX_C25519_SHA256 = 5
KEX_MAX = 6


class Kexalg:
    def __init__(self, name, keyType, ec_nid, hash_alg):
        self.name = name
        self.keyType = keyType
        self.ec_nid = ec_nid
        self.hash_alg = hash_alg


if WITH_OPENSSL:
    kexalgs = [
        Kexalg(KEX_DH1, KEX_DH_GRP1_SHA1, 0, SSH_DIGEST_SHA1),
        Kexalg(KEX_DH14, KEX_DH_GRP14_SHA1, 0, SSH_DIGEST_SHA1),
        Kexalg(KEX_DHGEX_SHA1, KEX_DH_GEX_SHA1, 0, SSH_DIGEST_SHA1),
        Kexalg(KEX_DHGEX_SHA256, KEX_DH_GEX_SHA256, 0, SSH_DIGEST_SHA256),
        Kexalg(KEX_ECDH_SHA2_NISTP256, KEX_ECDH_SHA2,
               NID_X9_62_prime256v1, SSH_DIGEST_SHA256),
        Kexalg(KEX_ECDH_SHA2_NISTP384, KEX_ECDH_SHA2, NID_secp384r1,
               SSH_DIGEST_SHA384),
        Kexalg(KEX_ECDH_SHA2_NISTP521, KEX_ECDH_SHA2, NID_secp521r1,
               SSH_DIGEST_SHA512),
        Kexalg(KEX_CURVE25519_SHA256, KEX_C25519_SHA256, 0, SSH_DIGEST_SHA256),
        Kexalg(None, -1, -1, -1),
    ]
else:
    kexalgs = [
        Kexalg(KEX_CURVE25519_SHA256, KEX_C25519_SHA256, 0, SSH_DIGEST_SHA256),
        Kexalg(None, -1, -1, -1),
    ]


def kex_alg_list(sep):
    retStr = ''
    for k in kexalgs.reverse():
        if k.name:
            retStr+=sep
            retStr+=


    return ','.join([k.name for k in kexalgs])


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
