import sys, matplotlib.pyplot as plt, networkx as nx
from matplotlib.patches import FancyArrowPatch

states = {"q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8"}
alphabet = {"a", "b", "c", "d"}

delta = {
    ("q0", "a"): "q1",
    ("q0", "b"): "q2",
    ("q0", "c"): "q3",
    ("q1", "a"): "q1",
    ("q1", "b"): "q3",
    ("q1", "c"): "q1",
    ("q1", "d"): "q4",
    ("q2", "a"): "q2",
    ("q2", "c"): "q2",
    ("q2", "d"): "q4",
    ("q3", "a"): "q3",
    ("q3", "d"): "q4",
    ("q4", "a"): "q7",
    ("q4", "b"): "q5",
    ("q5", "b"): "q6",
    ("q5", "c"): "q8",
    ("q6", "a"): "q7"
}

q0 = "q0"
F = {"q7", "q8"}

def run(s):
    q, steps = q0, [q0]
    for i, ch in enumerate(s):
        if (q, ch) not in delta: 
            raise ValueError(f"Sin transición desde {q} con '{ch}' en pos {i}")
        q = delta[(q, ch)]
        steps.append(q)
    return steps, q in F

G = nx.MultiDiGraph()
G.add_nodes_from(states)
for (q, a), p in delta.items(): 
    G.add_edge(q, p, key=a, label=a)

pos = nx.shell_layout(G)

def _mid(p1, p2, o=0.10):
    (x1, y1), (x2, y2) = p1, p2
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    nx_, ny_ = -dy, dx
    L = (nx_**2 + ny_**2)**0.5 or 1
    return mx + o * nx_ / L, my + o * ny_ / L

def draw_step(current, idx, sym=None):
    plt.clf()
    nodes = list(G.nodes())
    
    labels_map = {
        "q0": "q0:Espera", "q1": "q1:1$", "q2": "q2:2$", "q3": "q3:5$",
        "q4": "q4:Identif", "q5": "q5:Selecc", "q6": "q6:Dispen", 
        "q7": "q7:Cambio", "q8": "q8:Agotado"
    }
    
    nx.draw_networkx_nodes(G, pos, nodelist=nodes, 
                           node_size=[1500 if n == current else 1000 for n in nodes],
                           linewidths=[3 if n in F else 1 for n in nodes], 
                           edgecolors="black", node_color="lightgreen" if current in F else "lightblue")
    
    nx.draw_networkx_labels(G, pos, labels=labels_map, font_size=8, font_weight="bold")
    
    seen = {}
    for u, v, k, d in G.edges(keys=True, data=True):
        if u == v:
            x, y = pos[u]
            plt.gca().add_patch(FancyArrowPatch((x, y), (x + 1e-4, y + 1e-4), 
                                                connectionstyle="arc3,rad=0.45", 
                                                arrowstyle='-|>', mutation_scale=15))
            plt.text(x, y + 0.15, d['label'], fontsize=12, color="red", ha='center')
            continue
        
        i = seen.get((u, v), 0)
        seen[(u, v)] = i + 1
        rad = 0.25 if i % 2 == 0 else -0.25
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], connectionstyle=f"arc3,rad={rad}", 
                               arrows=True, arrowstyle='-|>', arrowsize=15)
        
        lx, ly = _mid(pos[u], pos[v], 0.12 if i % 2 == 0 else -0.12)
        plt.text(lx, ly, d['label'], fontsize=11, color="blue", ha='center', va='center', 
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
                 
    plt.axis('off')
    plt.title(f"Paso {idx}: {labels_map[current]}" + (f" | Entrada actual: '{sym}'" if sym else ""), fontsize=12)
    plt.pause(1.2)

if __name__ == '__main__':
    s = sys.argv[1] if len(sys.argv) > 1 else input("Introduce cadena de eventos (ej: abdba, cdbc): ").strip()
    try:
        steps, ok = run(s)
        print("✔ CADENA ACEPTADA" if ok else "✘ CADENA RECHAZADA (No terminó en estado final)", f"-> Estado final: {steps[-1]}")
        plt.ion()
        draw_step(steps[0], 0)
        for i, ch in enumerate(s, 1): 
            draw_step(steps[i], i, ch)
        plt.ioff()
        plt.show()
    except Exception as e:
        print("✘ RECHAZA:", e)