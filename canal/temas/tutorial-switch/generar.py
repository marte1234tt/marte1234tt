"""Genera los guiones de los dos tutoriales de switch (terminal con historial entre escenas)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ROBOT = {"tipo": "posicion", "x": 905, "y": 1335, "escala": 0.4, "desde": -1}

def tutorial(nombre, escenas, portada):
    hist, out = [], []
    for e in escenas:
        efectos = list(e.get("efectos", []))
        if e.get("topo") is not None:
            efectos = [ROBOT, dict({"tipo": "topologia", "desde": 0}, **e["topo"])] + efectos
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
    g = {"tema": nombre, "categoria": "tutorial", "personaje": "profe", "etiqueta": "TUTORIAL · PACKET TRACER",
         "duracion": {"min": 30, "max": 300}, "escenas": out, "encuesta": [], "portada": portada,
         "publicacion": {}, "fuentes": ["Cheat sheet Xarxes locals (MP0225, AEA2)"]}
    json.dump(g, open(os.path.join(D, nombre.split()[0].lower() + ".json"), "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- 1. configuración básica
tutorial("Basica configuración del switch", [
 {"titulo": "CONFIGURAR UN SWITCH", "texto": "Vamos a configurar un switch Cisco desde cero en Packet Tracer. Los cables ya los sabes poner, así que vamos directos a lo importante.",
  "efectos": [{"tipo": "entrada"}, {"tipo": "mirar", "x": "vaiven"}]},
 {"titulo": "NUESTRA RED", "texto": "Esta es la red: un switch en el centro y seis PCs conectados con cable directo. Cuando las luces del cable se ponen verdes, hay enlace. Haz clic en el switch, abre la pestaña CLI y pulsa Enter.",
  "topo": {"puertos": ["Fa0/1", "Fa0/2", "Fa0/3", "Fa0/4", "Fa0/5", "Fa0/6"], "clic": "clic"}},
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
], {"escena": 1, "t": "verdes", "linea1": "CONFIGURACIÓN", "linea2": "BÁSICA DEL SWITCH", "color2": "#FFD23F", "banda": "PACKET TRACER · PASO A PASO", "color_banda": "#3A86FF"})

# ---------------------------------------------------------------- 2. VLANs (3 VLAN)
V = [{"num": 10, "nombre": "VENDES", "color": "#3A86FF"}, {"num": 20, "nombre": "COMPRES", "color": "#FF7F50"}, {"num": 30, "nombre": "DIRECCIO", "color": "#9B5DE5"}]
PUERTOS = ["Fa0/1", "Fa0/2", "Fa0/3", "Fa0/4", "Fa0/5", "Fa0/6"]
TABLA = ["VLAN Name      Status    Ports", "---- --------- --------- -----------------",
         "1    default   active    Fa0/7 ... Fa0/24, Gig0/1",
         "10   Vendes    active    Fa0/1, Fa0/2", "20   Compres   active    Fa0/3, Fa0/4",
         "30   Direccio  active    Fa0/5, Fa0/6"]
tutorial("Vlans configurar 3 VLANs en el switch", [
 {"titulo": "¿QUÉ ES UNA VLAN?", "texto": "Una VLAN divide un switch en varias redes separadas. Los equipos solo se ven con los de su misma VLAN, como si estuvieran en switches distintos.",
  "efectos": [{"tipo": "entrada"}, {"tipo": "mirar", "x": "vaiven"},
              {"tipo": "etiqueta", "texto": "VLAN 10", "pos": [230, 560], "fondo": "#3A86FF", "color": "#FFFFFF", "desde": "divide"},
              {"tipo": "etiqueta", "texto": "VLAN 20", "pos": [540, 470], "fondo": "#FF7F50", "color": "#FFFFFF", "desde": "varias"},
              {"tipo": "etiqueta", "texto": "VLAN 30", "pos": [850, 560], "fondo": "#9B5DE5", "color": "#FFFFFF", "desde": "separadas"},
              {"tipo": "sello", "texto": "NO SE VEN", "color": "#E63946", "pos": [540, 700], "size": 80, "desde": "solo"}]},
 {"titulo": "EL EJERCICIO", "texto": "Este es el ejercicio: seis PCs, dos por departamento. Vendes en la VLAN 10, Compres en la VLAN 20 y Direcció en la VLAN 30. Vendes va en los puertos 1 y 2, Compres en el 3 y el 4, y Direcció en el 5 y el 6.",
  "topo": {"puertos": PUERTOS, "vlans": [dict(V[0], desde="Vendes"), dict(V[1], desde="Compres"), dict(V[2], desde="Direcció")]}},
 {"titulo": "ENTRA A CONFIGURAR", "texto": "En el switch, escribe enable, pon la contraseña, y luego configure terminal.", "aparece": 0.2,
  "lineas": [["s1>", "enable", "enable", ["Password:"]], ["s1#", "configure terminal", "configure"], ["s1(config)#", "", "configure+1.6"]]},
 {"titulo": "CREA LAS 3 VLAN", "texto": "Creamos las tres. Primero vlan 10 y name Vendes. Luego vlan 20 y name Compres. Y por último, vlan 30 y name Direccio. Sal de cada una con exit.",
  "lineas": [["s1(config)#", "vlan 10", "10"], ["s1(config-vlan)#", "name Vendes", "Vendes"], ["s1(config-vlan)#", "exit", "Luego-0.4"],
             ["s1(config)#", "vlan 20", "20"], ["s1(config-vlan)#", "name Compres", "Compres"], ["s1(config-vlan)#", "exit", "último-0.6"],
             ["s1(config)#", "vlan 30", "30"], ["s1(config-vlan)#", "name Direccio", "Direccio"], ["s1(config-vlan)#", "exit", "exit"], ["s1(config)#", "", "exit+1.2"]]},
 {"titulo": "PUERTOS DE VENDES", "texto": "Ahora, puerto por puerto. Entra en interface fa0/1, ponlo en modo acceso, y asígnalo a la VLAN 10. Sal con exit. Repite con el fa0/2: switchport mode access, y switchport access vlan 10.",
  "lineas": [["s1(config)#", "interface fa0/1", "interface"], ["s1(config-if)#", "switchport mode access", "modo"],
             ["s1(config-if)#", "switchport access vlan 10", "asígnalo"], ["s1(config-if)#", "exit", "exit"],
             ["s1(config)#", "interface fa0/2", "Repite+0.4"], ["s1(config-if)#", "switchport mode access", "switchport"],
             ["s1(config-if)#", "switchport access vlan 10", "switchport+2.2"], ["s1(config-if)#", "exit", "switchport+3.6"]]},
 {"titulo": "PUERTOS DE COMPRES", "texto": "Ahora Compres, en la VLAN 20. Primero el fa0/3: interface, modo acceso y VLAN 20. Y después, exactamente igual con el fa0/4.",
  "lineas": [["s1(config)#", "interface fa0/3", 0.9], ["s1(config-if)#", "switchport mode access", 2.15], ["s1(config-if)#", "switchport access vlan 20", 3.4], ["s1(config-if)#", "exit", 4.7], ["s1(config)#", "interface fa0/4", 5.6], ["s1(config-if)#", "switchport mode access", 6.85], ["s1(config-if)#", "switchport access vlan 20", 8.1], ["s1(config-if)#", "exit", 9.399999999999999]]},
 {"titulo": "PUERTOS DE DIRECCIÓ", "texto": "Y por último Direcció, en la VLAN 30. Lo mismo con el fa0/5, y después con el fa0/6. Ya están los seis.",
  "lineas": [["s1(config)#", "interface fa0/5", 0.9], ["s1(config-if)#", "switchport mode access", 2.15], ["s1(config-if)#", "switchport access vlan 30", 3.4], ["s1(config-if)#", "exit", 4.7], ["s1(config)#", "interface fa0/6", 5.6], ["s1(config-if)#", "switchport mode access", 6.85], ["s1(config-if)#", "switchport access vlan 30", 8.1], ["s1(config-if)#", "exit", 9.399999999999999]]},
 {"titulo": "COMPRUEBA", "texto": "Vuelve con end y escribe show vlan brief: verás las tres VLAN, cada una con sus dos puertos.",
  "lineas": [["s1(config)#", "end", "end"], ["s1#", "show vlan brief", "show", TABLA]]},
 {"titulo": "GUARDA", "texto": "Y no te olvides de guardar con copy running-config startup-config.",
  "lineas": [["s1#", "copy running-config startup-config", "copy", ["Building configuration...", "[OK]"]], ["s1#", "", "copy+3"]]},
 {"titulo": "PRUEBA CON PING", "texto": "Ahora la prueba. Pon a cada PC una IP de la misma red. El PC0 hace ping a su compañero de Vendes y responde. Pero si hace ping a uno de Compres, nada: están en VLANs distintas.",
  "topo": {"puertos": PUERTOS, "vlans": [dict(V[0], desde=-1), dict(V[1], desde=-1), dict(V[2], desde=-1)],
           "pings": [{"de": 0, "a": 1, "ok": True, "desde": "compañero"}, {"de": 0, "a": 2, "ok": False, "desde": "Compres"}]}},
], {"escena": 1, "t": "Direcció+1", "linea1": "3 VLANs EN EL", "linea2": "SWITCH CISCO", "color2": "#FFD23F", "banda": "PACKET TRACER · PASO A PASO", "color_banda": "#9B5DE5"})
print("ok")
