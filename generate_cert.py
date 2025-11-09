"""
Generate self-signed SSL certificate for local HTTPS development
Run this script once to create cert.pem and key.pem files
"""

from OpenSSL import crypto
import os

def generate_self_signed_cert(cert_file="cert.pem", key_file="key.pem"):
    """Generate a self-signed certificate"""

    # Create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # Create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "US"
    cert.get_subject().ST = "State"
    cert.get_subject().L = "City"
    cert.get_subject().O = "AI Fitness Trainer"
    cert.get_subject().OU = "Development"
    cert.get_subject().CN = "AI Trainer"

    # Add Subject Alternative Names for local IPs
    cert.add_extensions([
        crypto.X509Extension(
            b"subjectAltName",
            False,
            b"DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:10.42.108.58"
        ),
    ])

    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for 1 year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')

    # Save certificate
    with open(cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    # Save private key
    with open(key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

    print(f"✓ Certificate created: {cert_file}")
    print(f"✓ Private key created: {key_file}")
    print("\nNext steps:")
    print("1. Run: python app_https.py")
    print("2. Access: https://10.42.108.58:5000")
    print("3. Click 'Advanced' and 'Proceed' when browser warns about certificate")

if __name__ == "__main__":
    generate_self_signed_cert()
