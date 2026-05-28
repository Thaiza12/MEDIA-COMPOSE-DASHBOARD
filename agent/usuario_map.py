# usuario_map.py
# Fonte única de verdade para códigos de editor → nome completo.
# Importado pelo monitor.py e por qualquer outro módulo que precise.
#
# Convenção do nome de pasta:
#   <NOME DO PROJETO> - <CÓDIGO>
#   ex: "ANIVERSARIO RECIFE - LUC" → Lucas Cardoso Alecrim | projeto: ANIVERSARIO RECIFE
#
# Para adicionar um editor novo:
#   1. Descubra o código usado na pasta (token após " - ", maiúsculo)
#   2. Adicione uma linha aqui: "CODIGO": "Nome Completo"
#   3. Salve — o monitor.py já vai usar automaticamente

USUARIO_MAP: dict[str, str] = {

    # ── Editores ativos (extraídos da escala) ──────────────────────────────────
    "DEI":        "Deiga",
    "DEIGA":      "Deiga",

    "ALE":        "Alexandre Cavalcanti",
    "ALEX":       "Alexandre Cavalcanti",
    "ALEXANDRE":  "Alexandre Cavalcanti",

    "NAD":        "Nadja Cabral",
    "NADJA":      "Nadja Cabral",

    "HEN":        "Henrique Soares",
    "HENRIQUE":   "Henrique Soares",
    "HENF":       "Henrique Ferreira",

    "LIN":        "Linda Nsilva",
    "LINDA":      "Linda Nsilva",

    "EDU":        "Eduardo Carneiro Roque",
    "EDUARDO":    "Eduardo Carneiro Roque",

    "ERL":        "Erlania Silva",
    "ERLANIA":    "Erlania Silva",

    "OTO":        "Oto Duarte",

    "GAB":        "Gabrielli Lima",
    "GABI":       "Gabi Melo",
    "GABRIELLI":  "Gabrielli Lima",

    "CAR":        "Carla Silva",
    "CARLA":      "Carla Silva",

    "THA":        "Thayana Silva",
    "THAYANA":    "Thayana Silva",

    "BOS":        "Bosco",
    "BOSCO":      "Bosco",

    "NAF":        "Naftali Emidio",
    "NAFTALI":    "Naftali Emidio",

    "WEL":        "Wellingtania Widian Silva Marinho",
    "WELL":       "Wellingtania Widian Silva Marinho",

    "JES":        "Jessica Vale",
    "JESSICA":    "Jessica Vale",

    "CAM":        "Camila Macedo",
    "CAMILA":     "Camila Macedo",

    # ── Mantidos da versão anterior ───────────────────────────────────────────
    "LUC":        "Lucas Cardoso Alecrim",
    "LUCAS":      "Lucas Cardoso Alecrim",

    "SAM":        "Samuel Santos",
    "SAMUEL":     "Samuel Santos",

    "JOA":        "João Oliveira",
    "ANA":        "Ana Paula Ferreira",
}


def resolver_usuario(codigo: str) -> str:
    return USUARIO_MAP.get(codigo.upper().strip(), codigo)