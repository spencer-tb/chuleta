#!/usr/bin/env python3
"""Add a morphology breakdown as the third field of each vocab.json entry.

Verbs → present-tense six forms; nouns → article + plural; -o adjectives →
four forms. Function words and anything uncertain get no breakdown (empty
string) rather than a wrong one.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Fully irregular / stem-changing present-tense forms (yo, tú, él, nosotros,
# vosotros, ellos). Only verbs listed here or perfectly regular get conjugated.
IRREG = {
    "ser": ["soy", "eres", "es", "somos", "sois", "son"],
    "estar": ["estoy", "estás", "está", "estamos", "estáis", "están"],
    "ir": ["voy", "vas", "va", "vamos", "vais", "van"],
    "tener": ["tengo", "tienes", "tiene", "tenemos", "tenéis", "tienen"],
    "hacer": ["hago", "haces", "hace", "hacemos", "hacéis", "hacen"],
    "poder": ["puedo", "puedes", "puede", "podemos", "podéis", "pueden"],
    "querer": ["quiero", "quieres", "quiere", "queremos", "queréis", "quieren"],
    "saber": ["sé", "sabes", "sabe", "sabemos", "sabéis", "saben"],
    "poner": ["pongo", "pones", "pone", "ponemos", "ponéis", "ponen"],
    "venir": ["vengo", "vienes", "viene", "venimos", "venís", "vienen"],
    "decir": ["digo", "dices", "dice", "decimos", "decís", "dicen"],
    "salir": ["salgo", "sales", "sale", "salimos", "salís", "salen"],
    "ver": ["veo", "ves", "ve", "vemos", "veis", "ven"],
    "dar": ["doy", "das", "da", "damos", "dais", "dan"],
    "oír": ["oigo", "oyes", "oye", "oímos", "oís", "oyen"],
    "traer": ["traigo", "traes", "trae", "traemos", "traéis", "traen"],
    "caer": ["caigo", "caes", "cae", "caemos", "caéis", "caen"],
    "conocer": ["conozco", "conoces", "conoce", "conocemos", "conocéis", "conocen"],
    "conducir": ["conduzco", "conduces", "conduce", "conducimos", "conducís", "conducen"],
    "parecer": ["parezco", "pareces", "parece", "parecemos", "parecéis", "parecen"],
    "ofrecer": ["ofrezco", "ofreces", "ofrece", "ofrecemos", "ofrecéis", "ofrecen"],
    "nacer": ["nazco", "naces", "nace", "nacemos", "nacéis", "nacen"],
    "crecer": ["crezco", "creces", "crece", "crecemos", "crecéis", "crecen"],
    "reconocer": ["reconozco", "reconoces", "reconoce", "reconocemos", "reconocéis", "reconocen"],
    "seguir": ["sigo", "sigues", "sigue", "seguimos", "seguís", "siguen"],
    "conseguir": ["consigo", "consigues", "consigue", "conseguimos", "conseguís", "consiguen"],
    "elegir": ["elijo", "eliges", "elige", "elegimos", "elegís", "eligen"],
    "dirigir": ["dirijo", "diriges", "dirige", "dirigimos", "dirigís", "dirigen"],
    "coger": ["cojo", "coges", "coge", "cogemos", "cogéis", "cogen"],
    "recoger": ["recojo", "recoges", "recoge", "recogemos", "recogéis", "recogen"],
    "jugar": ["juego", "juegas", "juega", "jugamos", "jugáis", "juegan"],
    "pensar": ["pienso", "piensas", "piensa", "pensamos", "pensáis", "piensan"],
    "empezar": ["empiezo", "empiezas", "empieza", "empezamos", "empezáis", "empiezan"],
    "comenzar": ["comienzo", "comienzas", "comienza", "comenzamos", "comenzáis", "comienzan"],
    "cerrar": ["cierro", "cierras", "cierra", "cerramos", "cerráis", "cierran"],
    "despertar": ["despierto", "despiertas", "despierta", "despertamos", "despertáis", "despiertan"],
    "sentar": ["siento", "sientas", "sienta", "sentamos", "sentáis", "sientan"],
    "sentir": ["siento", "sientes", "siente", "sentimos", "sentís", "sienten"],
    "mentir": ["miento", "mientes", "miente", "mentimos", "mentís", "mienten"],
    "preferir": ["prefiero", "prefieres", "prefiere", "preferimos", "preferís", "prefieren"],
    "convertir": ["convierto", "conviertes", "convierte", "convertimos", "convertís", "convierten"],
    "entender": ["entiendo", "entiendes", "entiende", "entendemos", "entendéis", "entienden"],
    "perder": ["pierdo", "pierdes", "pierde", "perdemos", "perdéis", "pierden"],
    "encender": ["enciendo", "enciendes", "enciende", "encendemos", "encendéis", "encienden"],
    "volver": ["vuelvo", "vuelves", "vuelve", "volvemos", "volvéis", "vuelven"],
    "encontrar": ["encuentro", "encuentras", "encuentra", "encontramos", "encontráis", "encuentran"],
    "contar": ["cuento", "cuentas", "cuenta", "contamos", "contáis", "cuentan"],
    "recordar": ["recuerdo", "recuerdas", "recuerda", "recordamos", "recordáis", "recuerdan"],
    "acordar": ["acuerdo", "acuerdas", "acuerda", "acordamos", "acordáis", "acuerdan"],
    "costar": ["—", "—", "cuesta", "—", "—", "cuestan"],
    "doler": ["—", "—", "duele", "—", "—", "duelen"],
    "mover": ["muevo", "mueves", "mueve", "movemos", "movéis", "mueven"],
    "mostrar": ["muestro", "muestras", "muestra", "mostramos", "mostráis", "muestran"],
    "probar": ["pruebo", "pruebas", "prueba", "probamos", "probáis", "prueban"],
    "soñar": ["sueño", "sueñas", "sueña", "soñamos", "soñáis", "sueñan"],
    "dormir": ["duermo", "duermes", "duerme", "dormimos", "dormís", "duermen"],
    "morir": ["muero", "mueres", "muere", "morimos", "morís", "mueren"],
    "servir": ["sirvo", "sirves", "sirve", "servimos", "servís", "sirven"],
    "repetir": ["repito", "repites", "repite", "repetimos", "repetís", "repiten"],
    "vestir": ["visto", "vistes", "viste", "vestimos", "vestís", "visten"],
    "reír": ["río", "ríes", "ríe", "reímos", "reís", "ríen"],
    "volar": ["vuelo", "vuelas", "vuela", "volamos", "voláis", "vuelan"],
    "llover": ["—", "—", "llueve", "—", "—", "—"],
    "valer": ["valgo", "vales", "vale", "valemos", "valéis", "valen"],
    "deber": None,  # regular; listed to avoid the -er guess issue below (it's fine)
    "leer": ["leo", "lees", "lee", "leemos", "leéis", "leen"],
    "existir": None,
    "gustar": ["—", "—", "me gusta", "—", "—", "me gustan"],
    "importar": ["—", "—", "importa", "—", "—", "importan"],
    "faltar": ["—", "—", "falta", "—", "—", "faltan"],
    "echar de menos": ["echo de menos", "echas de menos", "echa de menos",
                       "echamos de menos", "echáis de menos", "echan de menos"],
}

FEM_EXCEPTIONS = {"mano", "foto", "moto", "radio"}
MASC_EXCEPTIONS = {"día", "problema", "sistema", "idioma", "mapa", "sofá", "clima", "tema"}
FEM_ENDINGS = ("a", "ión", "dad", "tad", "tud", "umbre")
KNOWN_FEM = {"noche", "tarde", "gente", "calle", "sangre", "leche", "carne",
             "clase", "llave", "fiebre", "frase", "suerte", "muerte", "parte",
             "madre", "sal", "sed", "piel", "flor", "luz", "voz", "paz", "red",
             "ley", "miel", "nariz", "catedral", "señal", "playa"}
KNOWN_MASC = {"coche", "nombre", "hombre", "padre", "restaurante", "puente",
              "diente", "cine", "pie", "café", "té", "amor", "color", "dolor",
              "calor", "señor", "sol", "papel", "hotel", "árbol", "mes", "país",
              "autobús", "corazón", "camión", "jamón", "limón", "pan", "tren",
              "fin", "jardín", "reloj", "lápiz", "pez", "arroz", "mar", "bar",
              "lugar", "azúcar", "aire", "viaje", "traje", "paisaje", "queso",
              "juego", "fuego"}

ADJ = {"grande", "pequeño", "nuevo", "viejo", "bueno", "malo", "primero",
       "último", "mismo", "propio", "único", "cierto", "importante", "joven",
       "mayor", "menor", "mejor", "peor", "alto", "bajo", "largo", "corto",
       "ancho", "fuerte", "débil", "rápido", "lento", "fácil", "difícil",
       "posible", "imposible", "libre", "ocupado", "abierto", "cerrado",
       "lleno", "vacío", "limpio", "sucio", "caro", "barato", "rico", "pobre",
       "feliz", "triste", "contento", "enfermo", "sano", "cansado",
       "despierto", "dormido", "caliente", "frío", "seco", "mojado", "dulce",
       "amargo", "salado", "bonito", "guapo", "feo", "precioso", "perfecto",
       "raro", "normal", "especial", "diferente", "igual", "junto", "solo",
       "seguro", "peligroso", "tranquilo", "nervioso", "serio", "divertido",
       "aburrido", "interesante", "simpático", "amable", "listo", "tonto",
       "loco", "verdadero", "falso", "claro", "oscuro", "blanco", "negro",
       "rojo", "azul", "verde", "amarillo", "gris", "marrón", "rosa",
       "naranja", "general", "próximo", "pasado", "siguiente"}

PRONOUNS = ["yo", "tú", "él", "nosotros", "vosotros", "ellos"]


def conj_regular(v):
    if v.endswith("ar"):
        stem, ends = v[:-2], ["o", "as", "a", "amos", "áis", "an"]
    elif v.endswith("er"):
        stem, ends = v[:-2], ["o", "es", "e", "emos", "éis", "en"]
    elif v.endswith("ir") or v.endswith("ír"):
        stem, ends = v[:-2], ["o", "es", "e", "imos", "ís", "en"]
    else:
        return None
    return [stem + e for e in ends]


def plural(n):
    if n.endswith(("a", "e", "i", "o", "u", "é", "á", "ó")):
        return n + "s"
    if n.endswith("z"):
        return n[:-1] + "ces"
    if n.endswith("ón"):
        return n[:-2] + "ones"
    return n + "es"


def gender(n):
    if n in FEM_EXCEPTIONS or n in KNOWN_FEM:
        return "la"
    if n in MASC_EXCEPTIONS or n in KNOWN_MASC:
        return "el"
    if n.endswith(FEM_ENDINGS):
        return "la"
    if n.endswith(("o", "or", "aje", "án")):
        return "el"
    return None


def breakdown(word, gloss):
    reflexive = word.endswith("se") and gloss.startswith("to ")
    base = word[:-2] if reflexive else word
    if gloss.startswith("to ") and (base.endswith(("ar", "er", "ir", "ír")) or word in IRREG):
        forms = IRREG.get(word) or IRREG.get(base)
        if forms is None or word in IRREG and IRREG[word] is None:
            forms = conj_regular(base)
        if not forms:
            return ""
        return " · ".join(f"{p} {f}" for p, f in zip(PRONOUNS, forms) if f != "—")
    if " " not in word and not gloss.startswith("to ") and word.isalpha():
        if word in ADJ:
            if word.endswith("o"):
                return f"{word} / {word[:-1]}a · {word}s / {word[:-1]}as"
            return f"{word} · {plural(word)} (same for m/f)"
        art = gender(word)
        if art:
            pl_art = "los" if art == "el" else "las"
            return f"{art} {word} · {pl_art} {plural(word)}"
    return ""


def main():
    vocab = json.loads((ROOT / "vocab.json").read_text())
    out = []
    n = 0
    for entry in vocab:
        w, g = entry[0], entry[1]
        b = breakdown(w, g)
        if b:
            n += 1
        out.append([w, g, b])
    (ROOT / "vocab.json").write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(out)} entries, {n} with breakdowns")
    for probe in ("tener", "casa", "pequeño", "que", "doler", "echar de menos"):
        for w, g, b in out:
            if w == probe:
                print(f"  {w}: {b or '(none)'}")


if __name__ == "__main__":
    main()
