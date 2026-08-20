import { generateKeyPairSync } from 'crypto';

// Generates a fresh, ephemeral RSA keypair for the test run so
// TokenIssuerService/JwtStrategy can sign/verify RS256 tokens without any
// real key material ever touching the repository.
const { privateKey, publicKey } = generateKeyPairSync('rsa', {
  modulusLength: 2048,
  privateKeyEncoding: { type: 'pkcs1', format: 'pem' },
  publicKeyEncoding: { type: 'spki', format: 'pem' },
});

process.env.JWT_PRIVATE_KEY = privateKey;
process.env.JWT_PUBLIC_KEY = publicKey;
process.env.MFA_CHALLENGE_SECRET = 'test-mfa-challenge-secret';
