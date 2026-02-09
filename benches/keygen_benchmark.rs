use criterion::{black_box, criterion_group, criterion_main, Criterion};
use dilithium_keygen::{generate_keypair, Parameters};
use rand::thread_rng;

fn benchmark_keygen(c: &mut Criterion) {
    c.bench_function("Dilithium key generation", |b| {
        b.iter(|| {
            let params = black_box(Parameters::default());
            let mut rng = black_box(thread_rng());
            let _ = black_box(generate_keypair(&params, &mut rng));
        })
    });
}

criterion_group!(benches, benchmark_keygen);
criterion_main!(benches);