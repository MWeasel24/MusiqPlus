# backend/data/setup_data.py
from pathlib import Path
import random

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# 1) Catálogo de músicas reais (30 itens)
# ============================================================

def create_itens():
    songs = [
        {
            "item_id": 1,
            "nome": "Blinding Lights",
            "artista": "The Weeknd",
            "genero": "Pop",
            "tempo": "Rápido",
            "instrumentacao": "Sintetizador, Voz",
            "palavra_chave": "pop",
            "humor": "Animado",
            "duracao_segundos": 200,
            "idioma": "Inglês",
            "tags": "pop, rápido, 2020, hit",
            "descricao": "Hit pop moderno com forte influência de synthwave.",
            "youtube_url": "https://youtu.be/fHI8X4OXluQ?si=B_OePl14nhgMTZ2g",
        },
        {
            "item_id": 2,
            "nome": "Shape of You",
            "artista": "Ed Sheeran",
            "genero": "Pop",
            "tempo": "Médio",
            "instrumentacao": "Violão, Voz, Percussão",
            "palavra_chave": "pop",
            "humor": "Animado",
            "duracao_segundos": 234,
            "idioma": "Inglês",
            "tags": "pop, dançante, radio",
            "descricao": "Faixa pop romântica com ritmo envolvente.",
            "youtube_url": "https://youtu.be/_dK2tDK9grQ?si=xag9qkf88tHRIb9o",
        },
        {
            "item_id": 3,
            "nome": "Bohemian Rhapsody",
            "artista": "Queen",
            "genero": "Rock",
            "tempo": "Médio",
            "instrumentacao": "Guitarra, Piano, Voz, Bateria",
            "palavra_chave": "rock",
            "humor": "Dramático",
            "duracao_segundos": 355,
            "idioma": "Inglês",
            "tags": "rock, clássico, anos 70",
            "descricao": "Clássico do rock com estrutura não convencional.",
            "youtube_url": "https://youtu.be/fJ9rUzIMcZQ?si=RhDlMxFmn4j-vvnP",
        },
        {
            "item_id": 4,
            "nome": "Smells Like Teen Spirit",
            "artista": "Nirvana",
            "genero": "Rock",
            "tempo": "Rápido",
            "instrumentacao": "Guitarra, Bateria, Baixo, Voz",
            "palavra_chave": "rock",
            "humor": "Animado",
            "duracao_segundos": 301,
            "idioma": "Inglês",
            "tags": "rock, grunge, anos 90",
            "descricao": "Hino do grunge que marcou os anos 90.",
            "youtube_url": "https://youtu.be/hTWKbfoikeg?si=rcIAv96R4NpuE9iH",
        },
        {
            "item_id": 5,
            "nome": "Take Five",
            "artista": "The Dave Brubeck Quartet",
            "genero": "Jazz",
            "tempo": "Médio",
            "instrumentacao": "Saxofone, Piano, Bateria",
            "palavra_chave": "jazz",
            "humor": "Chill",
            "duracao_segundos": 324,
            "idioma": "Instrumental",
            "tags": "jazz, clássico, instrumental",
            "descricao": "Jazz em compasso 5/4, um dos mais icônicos da história.",
            "youtube_url": "https://youtu.be/-DHuW1h1wHw?si=Am7tJEykcpp92KFH",
        },
        {
            "item_id": 6,
            "nome": "Garota de Ipanema",
            "artista": "Tom Jobim",
            "genero": "MPB",
            "tempo": "Médio",
            "instrumentacao": "Violão, Voz, Piano",
            "palavra_chave": "mpb",
            "humor": "Relaxado",
            "duracao_segundos": 210,
            "idioma": "Português",
            "tags": "mpb, bossa nova, clássico",
            "descricao": "Um dos maiores clássicos da Bossa Nova.",
            "youtube_url": "https://youtu.be/WuenyQ4NCQE?si=eQk77CP-sYzT4ln_",
        },
        {
            "item_id": 7,
            "nome": "Aquarela do Brasil",
            "artista": "Ary Barroso",
            "genero": "MPB",
            "tempo": "Médio",
            "instrumentacao": "Orquestra, Voz",
            "palavra_chave": "mpb",
            "humor": "Animado",
            "duracao_segundos": 260,
            "idioma": "Português",
            "tags": "mpb, samba, clássico",
            "descricao": "Canção brasileira clássica com forte identidade nacional.",
            "youtube_url": "https://youtu.be/r3Zjp1AO9lI?si=ougWDLKnpJK6z0Gr",
        },
        {
            "item_id": 8,
            "nome": "Blue in Green",
            "artista": "Miles Davis",
            "genero": "Jazz",
            "tempo": "Lento",
            "instrumentacao": "Trompete, Piano, Baixo",
            "palavra_chave": "jazz",
            "humor": "Triste",
            "duracao_segundos": 329,
            "idioma": "Instrumental",
            "tags": "jazz, modal, clássico",
            "descricao": "Balada jazz melancólica e introspectiva.",
            "youtube_url": "https://youtu.be/TLDflhhdPCg?si=NZWGcEWl4jNKuute",
        },
        {
            "item_id": 9,
            "nome": "Clair de Lune",
            "artista": "Claude Debussy",
            "genero": "Clássica",
            "tempo": "Lento",
            "instrumentacao": "Piano",
            "palavra_chave": "clássica",
            "humor": "Relaxado",
            "duracao_segundos": 290,
            "idioma": "Instrumental",
            "tags": "clássica, piano, romântico",
            "descricao": "Peça de piano impressionista, suave e contemplativa.",
            "youtube_url": "https://youtu.be/WNcsUNKlAKw?si=gnYqE8PaMopiYUwW",
        },
        {
            "item_id": 10,
            "nome": "Für Elise",
            "artista": "Ludwig van Beethoven",
            "genero": "Clássica",
            "tempo": "Médio",
            "instrumentacao": "Piano",
            "palavra_chave": "clássica",
            "humor": "Nostálgico",
            "duracao_segundos": 195,
            "idioma": "Instrumental",
            "tags": "clássica, piano, estudo",
            "descricao": "Peça de piano extremamente conhecida, muito usada em estudo.",
            "youtube_url": "https://youtu.be/wfF0zHeU3Zs?si=nST9iT5vBi7s7wgw",
        },
        {
            "item_id": 11,
            "nome": "SICKO MODE",
            "artista": "Travis Scott",
            "genero": "Hip Hop",
            "tempo": "Médio",
            "instrumentacao": "Beat, Voz",
            "palavra_chave": "hip hop",
            "humor": "Animado",
            "duracao_segundos": 312,
            "idioma": "Inglês",
            "tags": "hip hop, trap, moderno",
            "descricao": "Track de hip hop/trap com mudanças de beat marcantes.",
            "youtube_url": "https://youtu.be/6ONRf7h3Mdk?si=IhFfv9TX4RpMD-9E",
        },
        {
            "item_id": 12,
            "nome": "God's Plan",
            "artista": "Drake",
            "genero": "Hip Hop",
            "tempo": "Médio",
            "instrumentacao": "Beat, Voz",
            "palavra_chave": "hip hop",
            "humor": "Chill",
            "duracao_segundos": 210,
            "idioma": "Inglês",
            "tags": "hip hop, chill, radio",
            "descricao": "Faixa de hip hop com clima mais tranquilo e melódico.",
            "youtube_url": "https://youtu.be/xpVfcZ0ZcFM?si=eZtR2ARVnWo9C2yC",
        },
        {
            "item_id": 13,
            "nome": "One More Time",
            "artista": "Daft Punk",
            "genero": "Eletrônica",
            "tempo": "Rápido",
            "instrumentacao": "Sintetizador, Voz",
            "palavra_chave": "eletrônica",
            "humor": "Animado",
            "duracao_segundos": 320,
            "idioma": "Inglês",
            "tags": "eletrônica, house, clássico",
            "descricao": "Clássico da música eletrônica para festas.",
            "youtube_url": "https://youtu.be/FGBhQbmPwH8?si=bPjT_BZKZ_wy-IaQ",
        },
        {
            "item_id": 14,
            "nome": "Strobe",
            "artista": "deadmau5",
            "genero": "Eletrônica",
            "tempo": "Médio",
            "instrumentacao": "Sintetizador",
            "palavra_chave": "eletrônica",
            "humor": "Focado",
            "duracao_segundos": 630,
            "idioma": "Instrumental",
            "tags": "eletrônica, progressivo, longa",
            "descricao": "Faixa longa e progressiva, muito usada para foco.",
            "youtube_url": "https://youtu.be/tKi9Z-f6qX4?si=3NzeYiRJEOQi4QD6",
        },
        {
            "item_id": 15,
            "nome": "Lose Yourself",
            "artista": "Eminem",
            "genero": "Hip Hop",
            "tempo": "Médio",
            "instrumentacao": "Beat, Voz",
            "palavra_chave": "hip hop",
            "humor": "Focado",
            "duracao_segundos": 326,
            "idioma": "Inglês",
            "tags": "hip hop, trilha sonora, motivacional",
            "descricao": "Faixa intensa e motivacional de Eminem.",
            "youtube_url": "https://youtu.be/xFYQQPAOz7Y?si=OSGw35PjBTduHtkP",
        },
        {
            "item_id": 16,
            "nome": "Astronomia",
            "artista": "Vicetone & Tony Igy",
            "genero": "Eletrônica",
            "tempo": "Rápido",
            "instrumentacao": "Sintetizador",
            "palavra_chave": "eletrônica",
            "humor": "Animado",
            "duracao_segundos": 222,
            "idioma": "Instrumental",
            "tags": "eletrônica, meme, dançante",
            "descricao": "Música eletrônica que ficou famosa em memes de internet.",
            "youtube_url": "https://youtu.be/E-UidYgpn2A?si=03mEI6FuLDJf_T1C",
        },
        {
            "item_id": 17,
            "nome": "Numb",
            "artista": "Linkin Park",
            "genero": "Rock",
            "tempo": "Médio",
            "instrumentacao": "Guitarra, Bateria, Synth",
            "palavra_chave": "rock",
            "humor": "Triste",
            "duracao_segundos": 185,
            "idioma": "Inglês",
            "tags": "rock, nu metal, anos 2000",
            "descricao": "Faixa melancólica e intensa da banda Linkin Park.",
            "youtube_url": "https://youtu.be/kXYiU_JCYtU?si=QJysU8JPj1d9BUbT",
        },
        {
            "item_id": 18,
            "nome": "Perfect",
            "artista": "Ed Sheeran",
            "genero": "Pop",
            "tempo": "Lento",
            "instrumentacao": "Violão, Voz",
            "palavra_chave": "pop",
            "humor": "Romântico",
            "duracao_segundos": 263,
            "idioma": "Inglês",
            "tags": "pop, balada, romântico",
            "descricao": "Balada romântica muito popular em casamentos.",
            "youtube_url": "https://youtu.be/2Vv-BfVoq4g?si=cpNK40Nj7AoPPFd0",
        },
        {
            "item_id": 19,
            "nome": "Creep",
            "artista": "Radiohead",
            "genero": "Rock",
            "tempo": "Médio",
            "instrumentacao": "Guitarra, Bateria, Voz",
            "palavra_chave": "rock",
            "humor": "Triste",
            "duracao_segundos": 238,
            "idioma": "Inglês",
            "tags": "rock, alternativo, anos 90",
            "descricao": "Rock alternativo com clima melancólico e introspectivo.",
            "youtube_url": "https://youtu.be/XFkzRNyygfk?si=G_wPxYQ6mZ_y67gW",
        },
        {
            "item_id": 20,
            "nome": "All of Me",
            "artista": "John Legend",
            "genero": "Pop",
            "tempo": "Lento",
            "instrumentacao": "Piano, Voz",
            "palavra_chave": "pop",
            "humor": "Romântico",
            "duracao_segundos": 269,
            "idioma": "Inglês",
            "tags": "pop, balada, piano",
            "descricao": "Balada romântica com piano marcante.",
            "youtube_url": "https://youtu.be/450p7goxZqg?si=h-hmOmNbxoQA1Hb9",
        },
        {
            "item_id": 21,
            "nome": "Ocean Eyes",
            "artista": "Billie Eilish",
            "genero": "Indie",
            "tempo": "Lento",
            "instrumentacao": "Synth, Voz",
            "palavra_chave": "indie",
            "humor": "Triste",
            "duracao_segundos": 215,
            "idioma": "Inglês",
            "tags": "indie, pop alternativo, chill",
            "descricao": "Faixa suave e melancólica de Billie Eilish.",
            "youtube_url": "https://youtu.be/viimfQi_pUw?si=QsZEJqsqnOHG30Xk",
        },
        {
            "item_id": 22,
            "nome": "Sweater Weather",
            "artista": "The Neighbourhood",
            "genero": "Indie",
            "tempo": "Médio",
            "instrumentacao": "Guitarra, Voz, Synth",
            "palavra_chave": "indie",
            "humor": "Chill",
            "duracao_segundos": 240,
            "idioma": "Inglês",
            "tags": "indie, alternativo, chill",
            "descricao": "Hit indie com clima chill e romântico.",
            "youtube_url": "https://youtu.be/GCdwKhTtNNw?si=kO7blql2r3ixQide",
        },
        {
            "item_id": 23,
            "nome": "Technicolor",
            "artista": "Kudasai",
            "genero": "Lo-fi",
            "tempo": "Lento",
            "instrumentacao": "Synth, Bateria, Baixo",
            "palavra_chave": "lo-fi",
            "humor": "Chill",
            "duracao_segundos": 190,
            "idioma": "Instrumental",
            "tags": "lo-fi, estudo, relax",
            "descricao": "Faixa lo-fi muito usada para relaxar e estudar.",
            "youtube_url": "https://youtu.be/oAGWFop_Hx8?si=K3EudvLJUwpyUwUo",
        },
        {
            "item_id": 24,
            "nome": "Snowfall",
            "artista": "idealism",
            "genero": "Lo-fi",
            "tempo": "Lento",
            "instrumentacao": "Piano, Beat",
            "palavra_chave": "lo-fi",
            "humor": "Chill",
            "duracao_segundos": 195,
            "idioma": "Instrumental",
            "tags": "lo-fi, piano, relax",
            "descricao": "Faixa lo-fi calma com piano e clima de inverno.",
            "youtube_url": "https://youtu.be/B1ElJGOfUuc?si=pw3iPoQzsQY3VWwr",
        },
        {
            "item_id": 25,
            "nome": "Dreams",
            "artista": "Joakim Karud",
            "genero": "Lo-fi",
            "tempo": "Médio",
            "instrumentacao": "Beat, Synth",
            "palavra_chave": "lo-fi",
            "humor": "Chill",
            "duracao_segundos": 210,
            "idioma": "Instrumental",
            "tags": "lo-fi, vlog, chill",
            "descricao": "Música instrumental muito usada em vlogs.",
            "youtube_url": "https://youtu.be/p56gqDhUYbU?si=WQZG0ZvcxBKzioIV",
        },
        {
            "item_id": 26,
            "nome": "Sunset Lover",
            "artista": "Petit Biscuit",
            "genero": "Synthwave",
            "tempo": "Médio",
            "instrumentacao": "Synth, Voz",
            "palavra_chave": "synthwave",
            "humor": "Relaxado",
            "duracao_segundos": 195,
            "idioma": "Instrumental",
            "tags": "synthwave, chill, eletrônica",
            "descricao": "Faixa eletrônica com forte clima de pôr do sol.",
            "youtube_url": "https://youtu.be/4fQeaM62mOY?si=o3yP1MRZysdehVFQ",
        },
        {
            "item_id": 27,
            "nome": "Nightcall",
            "artista": "Kavinsky",
            "genero": "Synthwave",
            "tempo": "Lento",
            "instrumentacao": "Synth, Voz",
            "palavra_chave": "synthwave",
            "humor": "Sombrio",
            "duracao_segundos": 257,
            "idioma": "Inglês",
            "tags": "synthwave, dark, filme",
            "descricao": "Synthwave com clima mais sombrio, famosa por trilha sonora.",
            "youtube_url": "https://youtu.be/MV_3Dpw-BRY?si=b_sMwgCP-qXDPafs",
        },
        {
            "item_id": 28,
            "nome": "See You Again",
            "artista": "Wiz Khalifa ft. Charlie Puth",
            "genero": "Pop",
            "tempo": "Médio",
            "instrumentacao": "Piano, Voz, Beat",
            "palavra_chave": "pop",
            "humor": "Triste",
            "duracao_segundos": 229,
            "idioma": "Inglês",
            "tags": "pop, trilha sonora, emotivo",
            "descricao": "Balada emotiva famosa em trilha de filme.",
            "youtube_url": "https://youtu.be/RgKAFK5djSk?si=LLNms6GlhWJkPUyt",
        },
        {
            "item_id": 29,
            "nome": "Mas Que Nada",
            "artista": "Jorge Ben Jor",
            "genero": "MPB",
            "tempo": "Rápido",
            "instrumentacao": "Violão, Percussão, Voz",
            "palavra_chave": "mpb",
            "humor": "Animado",
            "duracao_segundos": 160,
            "idioma": "Português",
            "tags": "mpb, samba, clássico",
            "descricao": "Clássico brasileiro cheio de energia.",
            "youtube_url": "https://youtu.be/hg0XftC43Zo?si=eJo6PMiemv6G5EY_",
        },
        {
            "item_id": 30,
            "nome": "Weightless",
            "artista": "Marconi Union",
            "genero": "Eletrônica",
            "tempo": "Lento",
            "instrumentacao": "Synth, Texturas",
            "palavra_chave": "eletrônica",
            "humor": "Relaxado",
            "duracao_segundos": 505,
            "idioma": "Instrumental",
            "tags": "ambient, relax, estudo",
            "descricao": "Faixa ambiente considerada relaxante para estudo e sono.",
            "youtube_url": "https://youtu.be/UfcAVejslrU?si=9CJOeLaJTXbJ1dFI",
        },
    ]

    df = pd.DataFrame(songs)
    df.to_csv(BASE_DIR / "itens.csv", index=False)
    print("itens.csv criado com 30 músicas reais.")


# ============================================================
# 2) Gabarito – avaliacoes.csv (10 usuários, TODOS avaliam TODAS as músicas)
# ============================================================

def create_avaliacoes():
    """
    Gabarito do sistema: 10 usuários (ids 1–10) avaliando TODAS as músicas.
    Cada par (usuario_id, item_id) terá uma linha em avaliacoes.csv.
    """
    random.seed(42)
    np.random.seed(42)

    itens = pd.read_csv(BASE_DIR / "itens.csv")
    user_ids = list(range(1, 11))  # 10 usuários de gabarito

    # Preferência por gênero desses 10 usuários (gabarito)
    user_prefs = {
        1: ["Lo-fi", "Indie", "MPB"],
        2: ["Rock", "Hip Hop", "Trap"],
        3: ["Pop", "Eletrônica"],
        4: ["Jazz", "Clássica"],
        5: ["Trap", "Hip Hop"],
        6: ["Synthwave", "Eletrônica", "Lo-fi"],
        7: ["MPB", "Jazz"],
        8: ["Indie", "Rock"],
        9: ["Pop", "Lo-fi"],
        10: ["Jazz", "MPB", "Clássica"],
    }

    rows = []
    for u in user_ids:
        prefs = user_prefs.get(u, [])
        for _, item in itens.iterrows():
            item_id = int(item["item_id"])
            genero = str(item["genero"])
            # TODO: todo usuário avalia todas as músicas
            if genero in prefs:
                p_like = 0.85
            else:
                p_like = 0.35
            gostou = 1 if random.random() < p_like else 0
            rows.append(
                {
                    "usuario_id": u,
                    "item_id": item_id,
                    "gostou": gostou,
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(BASE_DIR / "avaliacoes.csv", index=False)
    print("avaliacoes.csv (gabarito) criado com 10 usuários avaliando todas as músicas.")


# ============================================================
# 3) Usuarios simulados
# ============================================================

def create_usuarios():
    """
    Cria apenas a estrutura de usuarios.csv, sem nenhum usuário.
    Todos os usuários serão criados manualmente pelo sistema.
    """
    df = pd.DataFrame(columns=["usuario_id", "nome", "item_id", "gostou", "origem"])
    df.to_csv(BASE_DIR / "usuarios.csv", index=False)
    print("usuarios.csv criado vazio; usuários serão cadastrados pelo sistema.")


# ============================================================
# Execução principal
# ============================================================

if __name__ == "__main__":
    create_itens()
    create_avaliacoes()
    create_usuarios()
    print("itens.csv, avaliacoes.csv e usuarios.csv criados em", BASE_DIR)
