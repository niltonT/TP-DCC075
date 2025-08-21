# Experimento: Quebrando um RSA didático com Shor (via Qiskit se disponível)
# -----------------------------------------------------------
# Este código é educacional: usa N pequeno (p.ex. 15) para demonstrar o fluxo completo.

import math
from random import randint

# -----------------------------
# 1) Monta um RSA didático
# -----------------------------
p, q = 3, 5              # pequenos, apenas para demonstração
N = p * q                # 15
phi = (p - 1) * (q - 1)  # 8
e = 3                    # gcd(e, phi) = 1
m = 7                    # mensagem de teste (1 < m < N e m coprimo a N de preferência)

# Cifra
c = pow(m, e, N)

print(f"[RSA didático] p={p}, q={q}, N={N}, phi(N)={phi}, e={e}")
print(f"Mensagem: {m} Cifrada: {c}\n")

# ------------------------------------------------------
# 2) Tenta fatorar N com Shor (rota quântica via Qiskit)
# ------------------------------------------------------
found_factors = None

def try_qiskit_shor_factor(N):
    """
    Tenta fatorar N usando Qiskit Shor se disponível no ambiente.
    Retorna lista de fatores [[p, q], ...] ou None.
    """
    try:
        # Tenta primeiro a API moderna
        from qiskit_algorithms import Shor
        from qiskit.primitives import Sampler
        # Um Sampler padrão (local). Se Aer estiver disponível, Qiskit o usará.
        sampler = Sampler()
        shor = Shor(sampler=sampler)
        res = shor.factor(N)
        # Alguns retornos trazem res.factors como lista de listas
        if hasattr(res, "factors") and res.factors:
            return res.factors
        return None
    except Exception as err1:
        # Tenta uma rota alternativa (versões antigas podem ter paths diferentes)
        try:
            from qiskit.algorithms import Shor  # fallback histórico
            from qiskit.primitives import Sampler
            sampler = Sampler()
            shor = Shor(sampler=sampler)
            res = shor.factor(N)
            if hasattr(res, "factors") and res.factors:
                return res.factors
            return None
        except Exception as err2:
            # Sem Qiskit ou sem Shor disponível
            return None

factors = try_qiskit_shor_factor(N)
if factors:
    # Escolhe o primeiro par válido não trivial
    for pair in factors:
        a, b = pair
        if a > 1 and b > 1 and a*b == N:
            found_factors = (a, b)
            break

if found_factors:
    print(f"[Shor/Qiskit] Sucesso! Fatores obtidos: p={found_factors[0]}, q={found_factors[1]}")
else:
    print("[Shor/Qiskit] Não foi possível rodar Shor (ambiente sem Qiskit/algoritmos ou falhou em N pequeno).")
    print("-> Seguindo com fallback didático (não quântico) apenas para concluir o exemplo.\n")
    # ------------------------------------------------------------------------
    # 2b) Fallback DIDÁTICO (não-quântico): busca fatores por tentativa
    #     Importante: isto NÃO é Shor; é apenas para fechar o ciclo do exemplo.
    # ------------------------------------------------------------------------
    def trivial_factor(N):
        for x in range(2, int(math.sqrt(N)) + 1):
            if N % x == 0:
                return x, N // x
        return None

    found_factors = trivial_factor(N)
    if found_factors:
        print(f"Fatores: p={found_factors[0]}, q={found_factors[1]}")
    else:
        raise RuntimeError("Não foi possível fatorar N nem com fallback.")

# -----------------------------------------------
# 3) Reconstrói a chave privada e decifra a msg
# -----------------------------------------------
p_rec, q_rec = found_factors
phi_rec = (p_rec - 1) * (q_rec - 1)

# Inverso modular de e mod phi
def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x, y = egcd(b, a % b)
    return (g, y, x - (a // b) * y)

def modinv(a, n):
    g, x, _ = egcd(a, n)
    if g != 1:
        raise ValueError("inverso modular não existe")
    return x % n

d_rec = modinv(e, phi_rec)
m_rec = pow(c, d_rec, N)

print(f"Mensagem recuperada: {m_rec}")
print("\nVerificação:", "SUCESSO" if m_rec == m else "FALHOU")
