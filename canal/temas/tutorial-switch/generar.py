"""Genera los guiones de los dos tutoriales de switch (terminal con historial entre escenas)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ROBOT = {"tipo": "posicion", "x": 905, "y": 1335, "escala": 0.4, "desde": -1}

def tutorial(nombre, escenas, portada):
    hist, out = [], []
    for e in escenas:
        efectos = list(e.get("efectos", []))
        if e.get("lineas") is not None:
            nuevas = [dict(zip(("prompt", "cmd", "desde", "salida"), l + ([] if len(l) > 3 else [[]]))) for l in e["lineas"]]
            for l in nuevas:
                if not l["salida"]: del l["salida"]
            if nuevas and "aparece" in e: nuevas[0]["aparece"] = e["aparece"]
            viejas = [dict(l, desde=-10, aparece=-10) for l in hist if l["cmd"] or l is hist[-1]][-10:]
            if viejas and nuevas and not viejas[-1]["cmd"]: viejas = viejas[:-1]  # el prompt vacío lo sustituye la línea nueva
            efectos = [ROBOT, {"tipo": "terminal", "desde": 0, "y1": 1110, "titulo": "s1 · CLI  (Packet Tracer)", "lineas": viejas + nuevas}] + efectos
            hist += nuevas
        out.append({"titulo": e["titulo"], "texto": e["texto"], "efectos": efectos})
    g = {"tema": nombre, "categoria": "tutorial", "personaje": "robot", "etiqueta": "TUTORIAL · PACKET TRACER",
         "duracion": {"min": 30, "max": 300}, "escenas": out, "encuesta": [], "portada": portada,
         "publicacion": {}, "fuentes": ["Cheat sheet Xarxes locals (MP0225, AEA2)"]}
    json.dump(g, open(os.path.join(D, nombre.split()[0].lower() + ".json"), "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- 1. configuración básica
tutorial("Basica configuración del switch", [
 {"titulo": "CONFIGURAR UN SWITCH", "texto": "Vamos a configurar un switch Cisco desde cero en Packet Tracer. Los cables ya los sabes poner, así que vamos directos a la terminal. Haz clic en el switch, abre la pestaña CLI y pulsa Enter.",
  "efectos": [{"tipo": "entrada"}, {"tipo": "mirar", "x": "vaiven"},
              {"tipo": "etiqueta", "texto": "PESTAÑA «CLI»", "pos": [540, 520], "fondo": "#FFD23F", "desde": "CLI"},
              {"tipo": "etiqueta", "texto": "PULSA ENTER ⏎", "pos": [540, 640], "desde": "Enter"}]},
 {"titulo": "USUARIO → PRIVILEGIADO", "texto": "Verás Switch y el símbolo mayor que: es el modo usuario, el más limitado. Escribe enable y el símbolo cambia a almohadilla. Ya estás en modo privilegiado.", "aparece": 0.2,
  "lineas": [["Switch>", "enable", "enable"], ["Switch#", "", "almohadilla"]]},
 {"titulo": "CONFIGURACIÓN GLOBAL", "texto": "Ahora escribe configure terminal, o en corto, conf t. Entras en la configuración global: fíjate en el paréntesis config del prompt.",
  "lineas": [["Switch#", "configure terminal", "configure"], ["Switch(config)#", "", "global"]]},
 {"titulo": "PONLE NOMBRE", "texto": "Lo primero, el nombre: hostname s1. Mira el prompt: ya no pone Switch, ahora pone s1.",
  "lineas": [["Switch(config)#", "hostname s1", "hostname"], ["s1(config)#", "", "Mira"]]},
 {"titulo": "CONTRASEÑA DE CONSOLA", "texto": "Protegemos la consola. Escribe line console 0. Luego password y la contraseña, por ejemplo Clau consola 1. Y muy importante, login: sin login, la contraseña no se pide. Sal con exit.",
  "lineas": [["s1(config)#", "line console 0", "line"], ["s1(config-line)#", "password Clau_consola1", "password"],
             ["s1(config-line)#", "login", "login"], ["s1(config-line)#", "exit", "exit"], ["s1(config)#", "", "exit+1.4"]]},
 {"titulo": "MENSAJE DE AVISO", "texto": "Ahora, un aviso para quien se conecte: banner motd, y el texto entre almohadillas.",
  "lineas": [["s1(config)#", "banner motd #Accés només per a personal autoritzat#", "banner"], ["s1(config)#", "", "almohadillas+0.6"]]},
 {"titulo": "CIFRAR CONTRASEÑAS", "texto": "Con service password-encryption, las contraseñas que estaban a la vista se guardan cifradas. Y con enable secret, más la clave, proteges el modo privilegiado.",
  "lineas": [["s1(config)#", "service password-encryption", "service"], ["s1(config)#", "enable secret Clau_admin1", "enable"], ["s1(config)#", "", "proteges"]]},
 {"titulo": "¡GUARDA!", "texto": "Ya casi está. Escribe end para volver al modo privilegiado, y después copy running-config startup-config para guardar. Si no guardas, al reiniciar se pierde todo.",
  "lineas": [["s1(config)#", "end", "end"], ["s1#", "copy running-config startup-config", "copy", ["Destination filename [startup-config]? ⏎", "Building configuration...", "[OK]"]], ["s1#", "", "reiniciar"]]},
 {"titulo": "COMPRUEBA", "texto": "Para comprobarlo todo, escribe show running-config. ¡Y listo! Switch configurado. En el siguiente vídeo, las VLAN.",
  "lineas": [["s1#", "show running-config", "show", ["hostname s1", "enable secret 5 $1$mERr$9cTjUIEqNGurQiFU.ZeCi1", "banner motd ^CAccés només per a personal autoritzat^C", "line con 0", " password 7 0822455D0A16", " login"]]],
  "efectos": [{"tipo": "sello", "texto": "¡LISTO!", "color": "#27C93F", "pos": [360, 1250], "size": 90, "desde": "listo"}]},
], {"escena": 0, "t": "terminal", "linea1": "CONFIGURACIÓN", "linea2": "BÁSICA DEL SWITCH", "color2": "#FFD23F", "banda": "PACKET TRACER · PASO A PASO", "color_banda": "#3A86FF"})

# ---------------------------------------------------------------- 2. VLANs
TABLA = ["VLAN Name      Status    Ports", "---- --------- --------- ------------------",
         "1    default   active    Fa0/6, Fa0/7, Fa0/8 ...", "10   Vendes    active    Fa0/1, Fa0/2, Fa0/3,", "                         Fa0/4, Fa0/5"]
tutorial("Vlans configurar VLANs en el switch", [
 {"titulo": "¿QUÉ ES UNA VLAN?", "texto": "Una VLAN divide un switch en varias redes separadas. Los equipos solo se ven con los de su misma VLAN, como si estuvieran en switches distintos. Vamos a crear la VLAN 10, Vendes.",
  "efectos": [{"tipo": "entrada"}, {"tipo": "mirar", "x": "vaiven"},
              {"tipo": "etiqueta", "texto": "VLAN 10 · VENDES", "pos": [260, 560], "fondo": "#3A86FF", "color": "#FFFFFF", "desde": "divide"},
              {"tipo": "etiqueta", "texto": "VLAN 20 · COMPRES", "pos": [820, 560], "fondo": "#FF7F50", "color": "#FFFFFF", "desde": "separadas"},
              {"tipo": "sello", "texto": "NO SE VEN", "color": "#E63946", "pos": [540, 700], "size": 80, "desde": "solo"}]},
 {"titulo": "ENTRA A CONFIGURAR", "texto": "Partimos del switch del vídeo anterior. Escribe enable, pon la contraseña, y luego configure terminal.", "aparece": 0.2,
  "lineas": [["s1>", "enable", "enable", ["Password:"]], ["s1#", "configure terminal", "configure"], ["s1(config)#", "", "configure+1.6"]]},
 {"titulo": "CREA LA VLAN", "texto": "Escribe vlan 10. Si no existe, se crea y entras en su modo. Ponle nombre con name Vendes, y sal con exit.",
  "lineas": [["s1(config)#", "vlan 10", "vlan"], ["s1(config-vlan)#", "name Vendes", "name"], ["s1(config-vlan)#", "exit", "exit"], ["s1(config)#", "", "exit+1.2"]]},
 {"titulo": "ASIGNA EL PUERTO", "texto": "Ahora el puerto donde está el PC: interface fa0/1. Lo ponemos en modo acceso, para un solo equipo, con switchport mode access. Y lo metemos en la VLAN con switchport access vlan 10.",
  "lineas": [["s1(config)#", "interface fa0/1", "interface"], ["s1(config-if)#", "switchport mode access", "switchport"], ["s1(config-if)#", "switchport access vlan 10", "metemos+1.0"]]},
 {"titulo": "VARIOS PUERTOS A LA VEZ", "texto": "Truco: con interface range configuras varios puertos de golpe. Por ejemplo, del fa0/2 al fa0/5, y repites los dos switchport.",
  "lineas": [["s1(config-if)#", "exit", "Truco"], ["s1(config)#", "interface range fa0/2 - 5", "interface"], ["s1(config-if-range)#", "switchport mode access", "repites"], ["s1(config-if-range)#", "switchport access vlan 10", "repites+1.7"]]},
 {"titulo": "COMPRUEBA", "texto": "Vuelve con end y escribe show vlan brief. Es el comando más útil: verás la VLAN 10, Vendes, con todos sus puertos.",
  "lineas": [["s1(config-if-range)#", "end", "end"], ["s1#", "show vlan brief", "show", TABLA]]},
 {"titulo": "GUARDA Y PRUEBA", "texto": "Guarda con copy running-config startup-config. Y la prueba de fuego: los PCs de la misma VLAN se hacen ping; los de VLANs distintas, no.",
  "lineas": [["s1#", "copy running-config startup-config", "copy", ["Building configuration...", "[OK]"]]],
  "efectos": [{"tipo": "sello", "texto": "MISMA VLAN: PING ✓", "color": "#27C93F", "pos": [390, 1210], "size": 50, "rot": -6, "desde": "misma"},
              {"tipo": "sello", "texto": "DISTINTA: PING ✗", "color": "#E63946", "pos": [390, 1340], "size": 50, "rot": 4, "desde": "distintas"}]},
], {"escena": 0, "t": "separadas", "linea1": "VLANs EN EL", "linea2": "SWITCH CISCO", "color2": "#FFD23F", "banda": "PACKET TRACER · PASO A PASO", "color_banda": "#9B5DE5"})
print("ok")
