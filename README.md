# Dilithium Key Generation Library

This is a high-quality Rust implementation of the Dilithium post-quantum digital signature algorithm's key generation process. Dilithium is based on the hardness of lattice problems and is designed to be secure against quantum computer attacks.

## Features

- Secure Dilithium key pair generation
- Proper handling of polynomial arithmetic in Z_q[X]/(X^n + 1)
- Centered Binomial Distribution (CBD) sampling for secret generation
- Memory-safe implementation with zeroization of sensitive data
- Comprehensive test suite
- Performance benchmarks

## Security Considerations

- All sensitive data is properly zeroized after use using the `zeroize` crate
- Polynomial operations are implemented with care to avoid timing side-channels
- Random number generation uses cryptographically secure sources
- Proper modular arithmetic to prevent overflows

## Usage

Add this to your `Cargo.toml`:

```toml
[dependencies]
dilithium-keygen = { path = "./" }
rand = "0.8"
```

Example:

```rust
use dilithium_keygen::{generate_keypair, Parameters};
use rand::thread_rng;

fn main() {
    let params = Parameters::default();  // Uses Dilithium3 parameters
    let mut rng = thread_rng();
    
    let (public_key, secret_key) = generate_keypair(&params, &mut rng)
        .expect("Key generation failed");
    
    println!("Generated Dilithium keypair successfully!");
    println!("Public key has {} polynomials", public_key.t1.len());
    println!("Secret key has {} secret polynomials", secret_key.s1.len());
}
```

## Implementation Details

This implementation follows the Dilithium specification closely:

- **Modulus (q)**: 8380417 (2^23 - 2^13 + 1)
- **Polynomial degree (n)**: 256
- **Matrix dimensions**: k × l (default 4 × 4 for Dilithium3)
- **CBD parameter (η)**: 2
- **Hash function**: SHAKE-256 (via SHA3-512)

The key generation process involves:
1. Generating a random seed `ρ` for the public matrix A
2. Sampling secret polynomials `s1` and `s2` with small coefficients using CBD
3. Computing `t = A·s1 - s2`
4. Decomposing `t` into high-order bits (`t1`) and low-order bits (`t0`)
5. Creating public key `(t1, ρ)` and secret key `(s1, s2, t0, ρ, TR, key)`

## Performance

Run benchmarks with:

```bash
cargo bench
```

Run tests with:

```bash
cargo test
```

## References

- [Dilithium Specification](https://pq-crystals.org/dilithium/specs/Dilithium-Round3-Updated20210125.pdf)
- [CRYSTALS-Dilithium Submission to NIST PQC Standardization Project](https://csrc.nist.gov/projects/post-quantum-cryptography/round-3-submissions)
- [Lattice-based cryptography fundamentals](https://link.springer.com/book/10.1007/978-3-319-95273-3)

## License

This project is licensed under the MIT license.