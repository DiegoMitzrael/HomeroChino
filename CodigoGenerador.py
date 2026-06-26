import sys, matplotlib.pyplot as plt, networkx as nx
from matplotlib.patches import FancyArrowPatch

# === 1. DEFINICIÓN DEL DFA (Basado exactamente en tu libreta) ===
states = {"q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8"}
alphabet = {"a", "b", "c"}

delta = {
    ("q0", "a"): "q1",
    ("q0", "b"): "q2",
    ("q0", "c"): "q3",
    ("q1", "a"): "q4",
    ("q2", "a"): "q2",
    ("q2", "b"): "q4",
    ("q3", "a"): "q3",
    ("q3", "b"): "q4",
    ("q4", "a"): "q5",
    ("q4", "b"): "q1",
    ("q4", "c"): "q2", 
    ("q5", "a"): "q6", 
    ("5", "b"): "q7", 
    ("q5", "c"): "q8", 
}

q0 = "q0"
# Estados finales (Cajas de terminación o entrega)
F = {"q6", "q7", "q8"}

# === 2. SIMULACIÓN ===
def run(s):
    q, steps = q0, [q0]
    for i, ch in enumerate(s):
        if (q, ch) not in delta: 
            raise ValueError(f"Sin transición desde {q} con '{ch}' en pos {i}")
        q = delta[(q, ch)]
        steps.append(q)
    return steps, q in F

# === 3. GRAFO Y DISEÑO DE COORDENADAS (Réplica de tu hoja) ===
G = nx.MultiDiGraph()
G.add_nodes_from(states)
for (q, a), p in delta.items(): 
    G.add_edge(q, p, key=a, label=a)

# Posiciones manuales (X, Y) para calcar la distribución de tu libreta
pos = {
    "q0": (0.0, 2.0),   # EN ESPERA DE CLIENTE (Izquierda)
    "q1": (2.5, 4.0),   # 1$ CREDIT (Arriba)
    "q2": (2.5, 2.2),   # 2$ (Centro-Izquierda)
    "q3": (2.5, 0.2),   # 5$ (Abajo-Izquierda)
    "q4": (5.5, 4.0),   # IDENTIFICA PRODUCTO (Centro-Arriba)
    "q5": (5.5, 2.0),   # SELECCIÓN EN PROCESO (Centro)
    "q7": (8.5, 4.0),   # ENTREGA VUELTO CAMBIO (Arriba Derecha)
    "q6": (5.5, -0.2),  # DISPENSA PRODUCTO (Abajo Centro)
    "q8": (8.5, 0.2),   # AGOTADO (Abajo Derecha)
}

# Mapeo de texto exacto de tus cajas para los nodos
labels_map = {
    "q0": "EN ESPERA\nDE CLIENTE",
    "q1": "1$ CREDIT",
    "q2": "2$",
    "q3": "5$",
    "q4": "IDENTIFICA\nPRODUCTO",
    "q5": "SELECCIÓN\nEN PROCESO",
    "q6": "DISPENSA\nPRODUCTO",
    "q7": "ENTREGA VUELTO\nCAMBIO",
    "q8": "AGOTADO"
}

# === 4. DIBUJO DINÁMICO POR PASOS ===
def _mid(p1, p2, o=0.12):
    (x1, y1), (x2, y2) = p1, p2
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    nx_, ny_ = -dy, dx
    L = (nx_**2 + ny_**2)**0.5 or 1
    return mx + o * nx_ / L, my + o * ny_ / L

def draw_step(current, idx, sym=None):
    plt.clf()
    nodes = list(G.nodes())
    
    # Dibujar Cajas/Nodos estilo tus diagramas
    nx.draw_networkx_nodes(G, pos, nodelist=nodes, 
                           node_size=[2800 if n == current else 2200 for n in nodes],
                           node_shape="s", # Nodos rectangulares como tus cajas
                           linewidths=[3 if n in F else 1 for n in nodes], 
                           edgecolors="black", 
                           node_color=["#FFD700" if n == current else "#F5F5F5" for n in nodes])
    
    nx.draw_networkx_labels(G, pos, labels=labels_map, font_size=7, font_weight="bold")
    
    seen = {}
    for u, v, k, d in G.edges(keys=True, data=True):
        # Bucles sobre sí mismo (como en 2$ y 5$)
        if u == v:
            x, y = pos[u]
            plt.gca().add_patch(FancyArrowPatch((x - 0.2, y + 0.2), (x + 0.2, y + 0.2), 
                                                connectionstyle="arc3,rad=-2.5", 
                                                arrowstyle='-|>', mutation_scale=15, color="blue"))
            plt.text(x, y + 0.45, d['label'], fontsize=12, color="blue", weight="bold", ha='center')
            continue
            
        # Flechas curvas para rutas de ida y vuelta sin encimarse
        i = seen.get((u, v), 0)
        seen[(u, v)] = i + 1
        rad = 0.15 if i % 2 == 0 else -0.15
        
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], connectionstyle=f"arc3,rad={rad}", 
                               arrows=True, arrowstyle='-|>', arrowsize=18, edge_color="gray")
        
        lx, ly = _mid(pos[u], pos[v], 0.12 if i % 2 == 0 else -0.12)
        plt.text(lx, ly, d['label'], fontsize=12, color="red", weight="bold", ha='center', va='center',
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))
                 
    plt.axis('off')
    plt.title(f"PASO {idx}: {labels_map[current].replace('\n', ' ')}" + (f" | Evento actual: '{sym}'" if sym else ""), fontsize=12, weight="bold")
    plt.pause(1.5)

# === 5. EJECUCIÓN ===
if __name__ == '__main__':
    print("--- SIMULADOR DE MÁQUINA EXPENDEDORA ---")
    s = sys.argv[1] if len(sys.argv) > 1 else input("Ingresa secuencia de eventos (ej. 'aa', 'bba', 'ca'): ").strip()
    try:
        steps, ok = run(s)
        print("\n[RESULTADO] ACEPTA -> Ruta de flujo válida." if ok else "\n[RESULTADO] RECHAZA -> Flujo incompleto.")
        plt.ion()
        draw_step(steps[0], 0)
        for i, ch in enumerate(s, 1): 
            draw_step(steps[i], i, ch)
        plt.ioff()
        plt.show()
    except Exception as e:
        print("\n[ERROR/RECHAZA]:", e)