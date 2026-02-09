//! # Dilithium Key Generation Implementation
//!
//! This crate provides a secure implementation of the Dilithium post-quantum
//! digital signature algorithm's key generation process. Dilithium is based on
//! the hardness of lattice problems and is designed to be secure against
//! quantum computer attacks.

use rand::Rng;
use sha3::{Sha3_512, Digest};
use std::ops::{Add, Sub, Mul};
use zeroize::Zeroize;

/// Represents a polynomial in the ring R_q = Z_q[X]/(X^n + 1)
#[derive(Debug, Clone)]
pub struct Polynomial {
    coefficients: Vec<u32>,
    modulus: u32,
}

impl Zeroize for Polynomial {
    fn zeroize(&mut self) {
        self.coefficients.zeroize();
    }
}

impl Polynomial {
    /// Create a new polynomial with given degree and modulus
    pub fn new(size: usize, modulus: u32) -> Self {
        Self {
            coefficients: vec![0; size],
            modulus,
        }
    }

    /// Sample a polynomial with coefficients from a centered binomial distribution
    pub fn sample_cbd(sigma: u32, n: usize, rng: &mut impl Rng) -> Self {
        let mut poly = Polynomial::new(n, 8380417); // Dilithium modulus
        for i in 0..n {
            poly.coefficients[i] = Self::sample_single_cbd(sigma, rng);
        }
        poly
    }

    /// Sample a single coefficient using centered binomial distribution
    fn sample_single_cbd(sigma: u32, rng: &mut impl Rng) -> u32 {
        let mut t = 0i32;
        for _ in 0..sigma {
            let b1 = rng.gen::<u8>() & 1;
            let b2 = (rng.gen::<u8>() >> 1) & 1;
            t += (b1 as i32) - (b2 as i32);
        }
        ((t + 4190208) as u32) % 8380417 // Add offset to ensure positive value
    }

    /// Reduce all coefficients modulo q
    pub fn reduce(&mut self) {
        for coeff in &mut self.coefficients {
            *coeff %= self.modulus;
        }
    }

    /// Number of coefficients in the polynomial
    pub fn len(&self) -> usize {
        self.coefficients.len()
    }

    /// Check if polynomial is empty
    pub fn is_empty(&self) -> bool {
        self.coefficients.is_empty()
    }
}

impl Add for Polynomial {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        let mut result = self.clone();
        result += other;
        result
    }
}

impl<'a> Add<&'a Polynomial> for Polynomial {
    type Output = Self;

    fn add(mut self, other: &'a Polynomial) -> Self {
        self += other;
        self
    }
}

impl Add<&Polynomial> for &Polynomial {
    type Output = Polynomial;

    fn add(self, other: &Polynomial) -> Polynomial {
        let mut result = self.clone();
        result += other;
        result
    }
}

impl Add<&Polynomial> for &mut Polynomial {
    type Output = ();

    fn add(&mut self, other: &Polynomial) {
        for i in 0..self.coefficients.len() {
            self.coefficients[i] = (self.coefficients[i] + other.coefficients[i]) % self.modulus;
        }
    }
}

impl Add<&Polynomial> for Polynomial {
    type Output = ();

    fn add(&mut self, other: &Polynomial) {
        for i in 0..self.coefficients.len() {
            self.coefficients[i] = (self.coefficients[i] + other.coefficients[i]) % self.modulus;
        }
    }
}

impl Sub for Polynomial {
    type Output = Self;

    fn sub(self, other: Self) -> Self {
        let mut result = self.clone();
        result -= other;
        result
    }
}

impl<'a> Sub<&'a Polynomial> for Polynomial {
    type Output = Self;

    fn sub(mut self, other: &'a Polynomial) -> Self {
        self -= other;
        self
    }
}

impl Sub<&Polynomial> for &Polynomial {
    type Output = Polynomial;

    fn sub(self, other: &Polynomial) -> Polynomial {
        let mut result = self.clone();
        result -= other;
        result
    }
}

impl Sub<&Polynomial> for &mut Polynomial {
    type Output = ();

    fn sub(&mut self, other: &Polynomial) {
        for i in 0..self.coefficients.len() {
            // Handle negative result by adding modulus
            let diff = self.coefficients[i] as i64 - other.coefficients[i] as i64;
            self.coefficients[i] = ((diff + self.modulus as i64) % self.modulus as i64) as u32;
        }
    }
}

impl Sub<&Polynomial> for Polynomial {
    type Output = ();

    fn sub(&mut self, other: &Polynomial) {
        for i in 0..self.coefficients.len() {
            // Handle negative result by adding modulus
            let diff = self.coefficients[i] as i64 - other.coefficients[i] as i64;
            self.coefficients[i] = ((diff + self.modulus as i64) % self.modulus as i64) as u32;
        }
    }
}

impl Mul for Polynomial {
    type Output = Self;

    fn mul(self, other: Self) -> Self {
        let mut result = self.clone();
        result *= other;
        result
    }
}

impl<'a> Mul<&'a Polynomial> for Polynomial {
    type Output = Self;

    fn mul(mut self, other: &'a Polynomial) -> Self {
        self *= other;
        self
    }
}

impl Mul<&Polynomial> for &Polynomial {
    type Output = Polynomial;

    fn mul(self, other: &Polynomial) -> Polynomial {
        let mut result = self.clone();
        result *= other;
        result
    }
}

impl Mul<&Polynomial> for &mut Polynomial {
    type Output = ();

    fn mul(&mut self, other: &Polynomial) {
        // Perform NTT-based multiplication if implemented, otherwise use schoolbook method
        // Here we implement schoolbook multiplication for simplicity
        let n = self.coefficients.len();
        let mut result_coeffs = vec![0u32; n];
        
        for i in 0..n {
            for j in 0..n {
                let k = (i + j) % n;
                // Handle potential overflow by using u64 for intermediate calculation
                let product = (self.coefficients[i] as u64) * (other.coefficients[j] as u64);
                result_coeffs[k] = (result_coeffs[k] as u64 + product) as u32 % self.modulus;
            }
        }
        
        self.coefficients = result_coeffs;
    }
}

impl Mul<&Polynomial> for Polynomial {
    type Output = ();

    fn mul(&mut self, other: &Polynomial) {
        // Perform NTT-based multiplication if implemented, otherwise use schoolbook method
        // Here we implement schoolbook multiplication for simplicity
        let n = self.coefficients.len();
        let mut result_coeffs = vec![0u32; n];
        
        for i in 0..n {
            for j in 0..n {
                let k = (i + j) % n;
                // Handle potential overflow by using u64 for intermediate calculation
                let product = (self.coefficients[i] as u64) * (other.coefficients[j] as u64);
                result_coeffs[k] = (result_coeffs[k] as u64 + product) as u32 % self.modulus;
            }
        }
        
        self.coefficients = result_coeffs;
    }
}

/// Represents the public key in Dilithium
#[derive(Debug, Clone)]
pub struct PublicKey {
    t1: Vec<Polynomial>,
    rho: [u8; 32],  // Seed for generating A
}

impl Zeroize for PublicKey {
    fn zeroize(&mut self) {
        for poly in &mut self.t1 {
            poly.zeroize();
        }
        self.rho.zeroize();
    }
}

/// Represents the secret key in Dilithium
#[derive(Debug)]
pub struct SecretKey {
    s1: Vec<Polynomial>,
    s2: Vec<Polynomial>,
    t0: Vec<Polynomial>,  // Low-order bits of (A*s1+s2)
    rho: [u8; 32],       // Seed for generating A
    tr: [u8; 64],        // Hash of (rho, t1)
    key: [u8; 32],       // Randomness used for signing
}

impl Zeroize for SecretKey {
    fn zeroize(&mut self) {
        for poly in &mut self.s1 {
            poly.zeroize();
        }
        for poly in &mut self.s2 {
            poly.zeroize();
        }
        for poly in &mut self.t0 {
            poly.zeroize();
        }
        self.rho.zeroize();
        self.tr.zeroize();
        self.key.zeroize();
    }
}

/// Dilithium parameters structure
#[derive(Debug, Clone)]
pub struct Parameters {
    pub n: usize,         // Polynomial degree
    pub k: usize,         // Number of polynomials in public key
    pub l: usize,         // Number of polynomials in secret key
    pub q: u32,           // Modulus
    pub eta: u32,         // CBD parameter for secrets
    pub tau: u32,         // Number of non-zero entries in c
}

/// Default parameters for Dilithium3 variant
impl Default for Parameters {
    fn default() -> Self {
        Self {
            n: 256,      // Polynomial degree
            k: 4,        // Number of polynomials in public key
            l: 4,        // Number of polynomials in secret key
            q: 8380417,  // Modulus
            eta: 2,      // CBD parameter
            tau: 39,     // Number of non-zero entries in c
        }
    }
}

/// Generate a pair of Dilithium keys
pub fn generate_keypair(
    params: &Parameters,
    rng: &mut impl Rng,
) -> Result<(PublicKey, SecretKey), &'static str> {
    // Generate random seed rho for matrix A
    let mut rho = [0u8; 32];
    rng.fill(&mut rho);

    // Generate random seed for the randomization vector w
    let mut r_seed = [0u8; 32];
    rng.fill(&mut r_seed);

    // Expand seed to generate matrix A
    let a_matrix = expand_a(&rho, params.k, params.l, params.n, params.q);

    // Generate secret vectors s1 and s2 with small coefficients
    let mut s1 = Vec::with_capacity(params.l);
    let mut s2 = Vec::with_capacity(params.k);

    for _ in 0..params.l {
        s1.push(Polynomial::sample_cbd(params.eta, params.n, rng));
    }

    for _ in 0..params.k {
        s2.push(Polynomial::sample_cbd(params.eta, params.n, rng));
    }

    // Compute A*s1 - s2 to get t
    let mut t = Vec::with_capacity(params.k);
    for i in 0..params.k {
        let mut ti = Polynomial::new(params.n, params.q);
        for j in 0..params.l {
            let mut product = a_matrix[i][j].clone();
            product *= &s1[j];
            ti += &product;
        }
        ti -= &s2[i];
        ti.reduce(); // Reduce coefficients modulo q
        t.push(ti);
    }

    // Create public key components
    let mut t1 = Vec::with_capacity(params.k);
    let mut t0 = Vec::with_capacity(params.k);

    for ti in t {
        let mut t1_poly = ti.clone();
        let mut t0_poly = ti;  // Work with a copy

        // Shift right by 13 bits to get high-order bits (for t1)
        for coeff in &mut t1_poly.coefficients {
            *coeff >>= 13;
        }

        // Keep low 13 bits (for t0)
        for coeff in &mut t0_poly.coefficients {
            *coeff &= ((1 << 13) - 1);  // Mask to keep only 13 low bits
        }

        t1.push(t1_poly);
        t0.push(t0_poly);
    }

    // Generate randomness for signing
    let mut key = [0u8; 32];
    rng.fill(&mut key);

    // Create TR (hash of rho and t1)
    let mut hash_input = Vec::new();
    hash_input.extend_from_slice(&rho);
    for poly in &t1 {
        for coeff in &poly.coefficients {
            hash_input.extend_from_slice(&coeff.to_le_bytes());
        }
    }

    let mut hasher = Sha3_512::new();
    hasher.update(&hash_input);
    let tr_full = hasher.finalize();
    let mut tr = [0u8; 64];
    tr.copy_from_slice(&tr_full);

    let public_key = PublicKey { t1, rho };
    let secret_key = SecretKey { s1, s2, t0, rho, tr, key };

    Ok((public_key, secret_key))
}

/// Expand the seed rho to generate the matrix A
fn expand_a(
    rho: &[u8; 32],
    k: usize,
    l: usize,
    n: usize,
    q: u32,
) -> Vec<Vec<Polynomial>> {
    let mut matrix = Vec::with_capacity(k);
    
    for i in 0..k {
        let mut row = Vec::with_capacity(l);
        for j in 0..l {
            // Create PRF input: [i, j, rho]
            let mut input = Vec::with_capacity(34);  // 1 byte for i + 1 byte for j + 32 bytes for rho
            input.push(i as u8);
            input.push(j as u8);
            input.extend_from_slice(rho);
            
            // Apply PRF to generate polynomial
            let mut hasher = Sha3_512::new();
            hasher.update(&input);
            let digest = hasher.finalize();
            
            // Convert digest to polynomial coefficients
            let mut poly = Polynomial::new(n, q);
            for (idx, chunk) in digest.chunks(4).take(n).enumerate() {
                let mut bytes = [0u8; 4];
                bytes[..chunk.len()].copy_from_slice(chunk);
                poly.coefficients[idx] = u32::from_le_bytes(bytes) % q;
            }
            
            row.push(poly);
        }
        matrix.push(row);
    }
    
    matrix
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::thread_rng;

    #[test]
    fn test_polynomial_operations() {
        let params = Parameters::default();
        let mut rng = thread_rng();
        
        // Test polynomial creation
        let mut poly1 = Polynomial::new(params.n, params.q);
        for i in 0..params.n {
            poly1.coefficients[i] = (i % params.q as usize) as u32;
        }
        
        let mut poly2 = Polynomial::new(params.n, params.q);
        for i in 0..params.n {
            poly2.coefficients[i] = ((i + 1) % params.q as usize) as u32;
        }
        
        // Test addition
        let sum = &poly1 + &poly2;
        assert_eq!(sum.coefficients[0], (poly1.coefficients[0] + poly2.coefficients[0]) % params.q);
        
        // Test subtraction
        let diff = &poly1 - &poly2;
        let expected_diff = (params.q - 1) % params.q;  // Since 0 - 1 mod q = q-1
        assert_eq!(diff.coefficients[0], expected_diff);
        
        // Test sampling
        let sampled = Polynomial::sample_cbd(params.eta, params.n, &mut rng);
        assert_eq!(sampled.len(), params.n);
    }

    #[test]
    fn test_key_generation() {
        let params = Parameters::default();
        let mut rng = thread_rng();
        
        let (pk, sk) = generate_keypair(&params, &mut rng).expect("Key generation failed");
        
        // Verify key sizes
        assert_eq!(pk.t1.len(), params.k);
        assert_eq!(sk.s1.len(), params.l);
        assert_eq!(sk.s2.len(), params.k);
        assert_eq!(sk.t0.len(), params.k);
        
        // Verify key properties
        assert_eq!(pk.rho.len(), 32);
        assert_eq!(sk.rho.len(), 32);
        assert_eq!(sk.tr.len(), 64);
        assert_eq!(sk.key.len(), 32);
    }
}