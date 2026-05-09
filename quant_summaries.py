"""
Resúmenes interpretativos orientativos (plantillas + números reales).
No usan modelo generativo; son guías para el analista sobre lo que muestran los resultados.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from quant_advanced import GroupComparisonResult, likert_matrix_key_to_original_column

from survey_intel import build_column_label_map


def loading_row_choice_labels(columns_ordered: list[str]) -> dict[str, str]:
    """
    Índices de cargas PCA/AFE («clave interna por truncado + sufijo») →
    etiquetas como en el selector («11. [resolver…»).
    """
    k2orig = likert_matrix_key_to_original_column(columns_ordered)
    choice = build_column_label_map(columns_ordered)
    return {k: choice[orig] for k, orig in k2orig.items()}


def _esc(*parts: str) -> str:
    return "".join(parts)


def _trunc(s: str, n: int = 72) -> str:
    t = str(s).replace("\n", " ").strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def _leading_common_fragment(columns: list[str], min_keep: int = 28) -> str:
    vals = [c.replace("\n", " ").strip() for c in columns if str(c).strip()]
    if not vals:
        return ""
    pref = vals[0]
    for other in vals[1:]:
        i = 0
        m = min(len(pref), len(other))
        while i < m and pref[i] == other[i]:
            i += 1
        pref = pref[:i]
        if len(pref) < min_keep:
            break
    pref = pref.strip()
    return pref if len(pref) >= min_keep else _trunc(vals[0], 140)


def _p_txt(p: float) -> str:
    if not (p == p):
        return "no disponible."
    if p < 0.001:
        return "inferior a 0,001 (**muy improbable** bajo hipótesis de independencia o de igualdad de medias)."
    return f"{p:.4f}."


def _cramers_interpret(v: float) -> str:
    if not (v == v):
        return "No se puede estimar **Cramér V** con esta tabla (celdas o dimensiones insuficientes)."
    absv = abs(v)
    mag = (
        "**asociación leve**" if absv < 0.1 else "**asociación pequeña a moderada**" if absv < 0.3 else "**asociación moderada a grande**"
    )
    return f"Cramér V = **{v:.3f}** (reglas orientativas: &lt;0,10 leve, 0,10–0,30 típico, ≥0,30 grande). Interpretación: {mag}."


def _alpha_interpret(alpha: float) -> str:
    if not (alpha == alpha):
        return "El **α** no permite una lectura útil hasta que haya suficientes ítems y variación conjunta."

    bands = "(orientativo: líteratura suele ubicar valores **≥0,70–0,80** como aceptables en investigación aplicada)."
    if alpha >= 0.9:
        return f"Valor **alto ({alpha:.3f})** para consistencia interna {bands}; verificá que los ítems midan una sola dimensión."
    if alpha >= 0.7:
        return f"Valor **aceptable a bueno ({alpha:.3f})** {bands} si la escala es unidimensional y los ítems son conceptualmente cercanos."
    if alpha >= 0.6:
        return f"Valor **aceptable pero mejorable ({alpha:.3f})**. Reconsiderá ítems ambiguos, mezcla 4 vs 5 categorías o subescalas diferenciadas."
    return f"Valor **relativamente bajo ({alpha:.3f})**. El bloque puede no comportarse como una sola escala o incluir preguntas poco relacionadas tras la codificación."


def descriptive_explanatory(desc: dict, ft: pd.DataFrame | None = None, top_categories: int = 4) -> str:
    out: list[str] = []
    n = desc.get("n_no_na") or desc.get("n", 0)
    out.append(_esc(f"Hay **{int(n)}** respuestas no vacías sobre **{int(desc.get('n_categorías', 0))}** categorías distintas. "))
    modo = desc.get("moda_etiqueta") or ""
    out.append(_esc(f"La **moda** (categoría más frecuente) es «{_trunc(modo, 64)}». "))
    if ft is not None and not ft.empty and "frecuencia" in ft.columns:
        cols = ft.columns
        pct_col = "porcentaje" if "porcentaje" in cols else None
        top = ft.head(top_categories)
        bits = []
        for _, row in top.iterrows():
            cat = _trunc(row.get("categoría", row.iloc[0]), 52)
            f = int(row["frecuencia"])
            if pct_col:
                pct = row[pct_col]
                bits.append(f"«{cat}» (**{pct:.1f}%**, n={f})")
            else:
                bits.append(f"«{cat}» (n={f})")
        out.append("\n\n**Dominio de categorías:** " + "; ".join(bits) + ". ")
    if desc.get("media") is not None and desc.get("media") == desc.get("media"):
        out.append(
            _esc(
                f"\n\nEl motor infirió escala ordinal reconocible (**{desc.get('esquema_ordinal_inferido') or 'esquema mixto'}**): "
                f"media **{desc['media']:.2f}**, mediana **{desc['mediana']:.2f}**"
            )
        )
        if desc.get("desv_std") is not None and desc["desv_std"] == desc["desv_std"]:
            out.append(f", desv. típ. **{desc['desv_std']:.2f}**.")
        else:
            out.append(".")
    else:
        out.append(
            "\n\n**No** se reportan mediana/media como escala continua: "
            "tratá el ítem como **categórico nominal u ordinal no homogéneo** en la muestra actual."
        )
    out.append(
        "\n\n*Limitación:* las inferencias estadísticas formales están en otros módulos (χ², comparación de grupos, etc.)."
    )
    return "".join(out)


def chi_square_explanatory(
    *,
    chi2: float,
    gl: int,
    p_valor: float,
    cramers_v: float,
    n: int,
    row_lab: str,
    col_lab: str,
) -> str:
    if not (chi2 == chi2) or gl < 1:
        return (
            "**No** se ejecutó χ² válido (tabla con una sola fila/columna o datos insuficientes). "
            "Probá agrupando categorías poco frecuentes o usando otras variables."
        )
    cram = _cramers_interpret(cramers_v)
    sig = p_valor == p_valor and p_valor < 0.05
    p_clar = (
        "*p*&lt;0,05 suele marcarse como resultados estadísticamente destacables (α habitual 0,05)."
        if sig
        else "*p*≥0,05 suele leerse como ausencia de evidencia clara contra independencia estadística entre filas y columnas."
    )
    assoc = cram
    if sig:
        assoc = (
            "**Hay evidencia compatible con una asociación** entre estas variables categorizadas (al nivel habitual α=0,05).\n\n"
            + cram
            + "\n\n**Ojo interpretativo:** lo estadístico no reemplaza el tamaño efectivo práctico; mirá proporciones por celda para la lectura cualitativa."
        )
    else:
        assoc = (
            "**No hay evidencia clara** contra la independencia entre filas y columnas en esta tabla (α habitual 0,05).\n\n" + cram
        )
    return (
        f"Con **n = {int(n)}** casos válidos ({_trunc(row_lab, 48)} × {_trunc(col_lab, 48)}):\n\n"
        f"- χ² = **{chi2:.3f}**, gl = **{gl}**, p = {_p_txt(p_valor)}\n"
        f"- {p_clar}\n\n"
        f"{assoc}"
    )


def group_comparison_explanatory(res: GroupComparisonResult, y_lab: str, g_lab: str) -> str:
    lines = [
        f"Comparación de **{_trunc(y_lab, 56)}** según **{_trunc(g_lab, 56)}**.",
        f"- Grupos **k = {res.n_groups}**, tamaños: {res.group_sizes}.",
    ]
    if res.message:
        lines.append(f"- Nota: {res.message}")
    if res.n_groups == 2:
        if res.t_p is not None and res.t_p == res.t_p:
            lines.append(
                f"- **t de Welch** p = **{res.t_p:.4f}** — "
                f"{'diferencia de medias ordinal-inferida entre los dos grupos plausible a α=0,05' if res.t_p < 0.05 else 'sin evidencia clara de diferencia de medias entre los dos grupos (α=0,05 orientativo).'}"
            )
        if res.mw_p is not None and res.mw_p == res.mw_p:
            lines.append(
                f"- **Mann–Whitney** p = **{res.mw_p:.4f}** — prueba no paramétrica complementaria sobre rangos; {'coherente con diferencia de distribución' if res.mw_p < 0.05 else 'sin señal clara de cambio de distribución.'}"
            )
    if res.anova_p is not None and res.anova_p == res.anova_p and res.n_groups > 2:
        lines.append(
            f"- **ANOVA** p = **{res.anova_p:.4f}** — "
            f"{'al menos un grupo difiere en media (ver supuestos y post‑hoc si aplica)' if res.anova_p < 0.05 else 'sin evidencia clara de diferencias globales de medias.'}"
        )
    if res.kruskal_p is not None and res.kruskal_p == res.kruskal_p and res.n_groups > 2:
        lines.append(
            f"- **Kruskal–Wallis** p = **{res.kruskal_p:.4f}** — "
            f"{'diferencias de distribución entre grupos plausibles' if res.kruskal_p < 0.05 else 'sin señal clara entre grupos.'}"
        )
    lines.append(
        "\n*Recordatorio:* la codificación ordinal es **inferida** automáticamente; validá trato de categorías e ítems invertidos en el panel superior."
    )
    return "\n".join(lines)


def cronbach_explanatory(alpha: float, n_cases: int, n_items: int, warns: list[str] | None) -> str:
    lines = [
        f"Matriz lista con **{n_cases}** encuestados y **{n_items}** ítems (casos completos, listwise).",
        _alpha_interpret(alpha),
        "\nCombinar ítems de **preguntas con distinta escala** (4 vs 5 puntos) puede inflar/deprimir α; los avisos del panel están para eso.",
    ]
    if warns:
        lines.append("\n\n**Advertencias emitidas:** " + "; ".join(_trunc(w, 140) for w in warns[:4]))
        if len(warns) > 4:
            lines.append(f" (+{len(warns)-4} más).")
    return "".join(lines)


def _top_loading_pairs(
    loadings: pd.DataFrame,
    col: str,
    k: int = 6,
    threshold: float = 0.22,
    row_labels: dict[str, str] | None = None,
) -> list[tuple[str, float]]:
    """Pares (etiqueta legible, carga ordenada por |.|)."""
    if col not in loadings.columns:
        return []
    s = loadings[col].abs().sort_values(ascending=False)
    rows = [(str(idx), float(loadings.loc[idx, col])) for idx in s.index]
    picked: list[tuple[str, float]] = []
    for i, v in rows:
        if abs(v) >= threshold:
            picked.append((i, v))
            if len(picked) >= k:
                break
    if not picked:
        picked = rows[: max(2, min(k, len(rows)))]
    out: list[tuple[str, float]] = []
    for idx, v in picked[:k]:
        lab = _trunc(row_labels.get(idx, idx), 92) if row_labels else _trunc(idx, 56)
        out.append((lab, v))
    return out


def _top_loadings_markdown(
    loadings: pd.DataFrame,
    col: str,
    k: int = 3,
    threshold: float = 0.25,
    row_labels: dict[str, str] | None = None,
) -> str:
    pairs = _top_loading_pairs(loadings, col, k=k, threshold=threshold, row_labels=row_labels)
    if not pairs:
        return "—"
    parts = []
    for lab, v in pairs:
        sign = "+" if v >= 0 else ""
        parts.append(f"«{_trunc(lab, 92)}» ({sign}{v:.2f})")
    return ", ".join(parts)


def pca_explanatory(
    loadings: pd.DataFrame,
    var_ratio: np.ndarray,
    n_respondentes: int,
    method: str = "clásico",
    row_labels: dict[str, str] | None = None,
) -> str:
    vr = np.asarray(var_ratio).ravel()
    if vr.size == 0:
        return "No hay varianza explicada disponible para resumir."
    cum12 = float(vr[:2].sum()) if vr.size >= 2 else float(vr[0])
    cumk = float(vr[: min(6, vr.size)].sum())
    ml = method.lower()
    method_txt = (
        "**correlaciones policóricas aprox.**"
        if "polí" in ml or "polic" in ml or "poly" in ml or "hec" in ml
        else "**datos estandarizados (Pearson / PCA habitual)**"
    )

    pcs = []
    for j in range(min(3, loadings.shape[1])):
        nm = loadings.columns[j]
        pcs.append(
            f"- **{nm}**: carga destacada en {_top_loadings_markdown(loadings, nm, row_labels=row_labels)}."
        )

    note = ""
    if vr[0] >= 0.45:
        note = "\n\nLa primera componente domina bastante parte de la varianza conjunta → revisá redundancia conceptual entre preguntas o un único tema transversal."
    return (
        f"PCA **{method_txt}**, **n** = **{int(n_respondentes)}** encuestados con datos completos en los ítems elegidos.\n\n"
        f"- **PC1** explica ~**{100*vr[0]:.1f}%** de la varianza total;"
        + (f" **PC1+PC2** acumulan ~**{100*cum12:.1f}%**." if vr.size >= 2 else "")
        + f"\n- Los **{min(6, vr.size)}** primeros ejes cubren ~**{100*cumk:.1f}%**.\n\n"
        "**Interpretación práctica:** las cargas indican cómo cada pregunta pesa sobre cada componente "
        "(valores cercanos en magnitud sugieren comportamiento parecido tras estandarización):\n\n"
        + "\n".join(pcs)
        + "\n\n"
        "**Cuidados:** PCA busca ejes ortogonales de varianza, no garantiza factores sociológicos teorizados;"
        + " no equivale solo a ítems correlacionados con el mismo fenómeno sin revisión cualitativa del cuestionario."
        + note
    )


def efa_explanatory(
    loadings: pd.DataFrame,
    eig: tuple[Any, ...] | None,
    n_respondentes: int,
    n_factors_requested: int,
    method_note: str = "Varimax, datos continuos estándar o matriz policórica según opción marcada.",
    row_labels: dict[str, str] | None = None,
) -> str:
    lines = [
        f"AFE exploratorio solicitó **{int(n_factors_requested)}** factores; **n** = **{int(n_respondentes)}**. {method_note}",
        "\nPor factor destacan cargas grandes (entre **≈0,25 y ≈0,40** suele tratarse solo como guía rápida; acá ordenamos las más altas observadas):\n",
    ]
    fac_lines = []
    for j in range(loadings.shape[1]):
        col = loadings.columns[j]
        top = _top_loadings_markdown(loadings, col, k=4, threshold=0.22, row_labels=row_labels)
        fac_lines.append(f"- **{col}**: {top}.")
    lines.append("\n" + "\n".join(fac_lines))

    lines.append("\n\n**Kaiser orientativo:** buscá autovalores de la correlación &gt;1 en muestras grandes; si el segundo cae rápido, quizá menos factores tienen soporte estadístico simple.")
    if eig is not None and eig[0] is not None:
        ev = np.asarray(eig[0]).ravel()
        if ev.size >= 4:
            lines.append(f"\n\nPrimer autovalores: **{ev[0]:.2f}**, **{ev[1]:.2f}**, **{ev[2]:.2f}**, **{ev[3]:.2f}**… ")
            lines.append("\nContrastá ese patrón con el **scree** y con la teoría de tu constructo antes de etiquetar factores.")
    lines.append(
        "\n\n*Limitación:* AFE encuentra combinaciones estadísticas de correlación; nombrarlos («utilidad práctica», etc.) sigue siendo trabajo **conceptual**, no automatizable sin el marco del estudio."
    )
    return "".join(lines)


def _pc1_paragraph_academic(
    loadings: pd.DataFrame,
    row_labels: dict[str, str] | None,
) -> str:
    pc1 = loadings.columns[0] if loadings.shape[1] >= 1 else ""
    if not pc1:
        return ""
    pairs = _top_loading_pairs(loadings, str(pc1), k=6, threshold=0.22, row_labels=row_labels)
    if len(pairs) < 2:
        return ""
    pos = [(a, b) for a, b in pairs if b > 0.05][:4]
    neg = [(a, b) for a, b in pairs if b < -0.05][:3]
    pos_txt = ", ".join(f"**{p[0]}**" for p in pos)
    out = (
        f"Para **interpretar {pc1} en clave sustantiva (exploratorio)**, destacá que tras estandarización las cargas positivas muestran **co‑variación estadística positiva**. "
        f"Las preguntas {pos_txt} **suben a la vez** en la muestra cuando se comparan personas (no implica igual «importancia práctica»: sólo coincide el patrón de respuesta). "
        "En artículos de psicometría o educación mediática esto suele resumirse como un **primer eje instrumental** que resume dispersión correlacional antes de etiquetarlo con etiquetas causales fuertes."
    )
    if neg:
        neg_txt = "; ".join(f"**{a}** (carga {b:+.2f})" for a, b in neg)
        out += f" Ítems con carga marcada negativamente (**{neg_txt}**) mueven el eje **en sentido contrario** frente al bloque anterior: conviene chequear formulación/redacción o si están invertidas en tu protocolo."
    return out


def _efa_factor_paragraph(loadings_efa: pd.DataFrame, row_labels: dict[str, str] | None) -> str:
    bullets: list[str] = []
    for col in loadings_efa.columns:
        prs = _top_loading_pairs(loadings_efa, col, k=4, threshold=0.38, row_labels=row_labels)
        if len(prs) < 2:
            prs = _top_loading_pairs(loadings_efa, col, k=5, threshold=0.26, row_labels=row_labels)
        if len(prs) < 2:
            continue
        labs = "**" + "**, **".join(_trunc(p[0], 74) for p in prs[:4]) + "**"
        vals = "; ".join(f"{p[1]:+.2f}" for p in prs[:4])
        bullets.append(f"- `{col}` sintetiza con mayor fuerza cargas relativas sobre {labs}. Valores cargas (orden mostrado): {vals}. ")
    return "\n".join(bullets)


def academic_exploratory_factor_reading(
    *,
    selected_columns: list[str],
    row_labels_matrix_index: dict[str, str],
    loadings_pca: pd.DataFrame,
    var_ratio: np.ndarray,
    loadings_efa: pd.DataFrame | None,
    eig: tuple[Any, ...] | None,
    n_factors_requested: int,
    n_obs: int,
    pca_engine_description: str,
    efa_engine_description: str,
) -> str:
    """
    Texto tipo informe exploratorio dirigido a lector universitario no experto en factorial.
    `row_labels_matrix_index`: claves igual a índice de cargas PCA/AFE → etiquetas estilo selector.
    """
    if not selected_columns or loadings_pca.empty:
        return ""
    vr = np.asarray(var_ratio).ravel()
    if vr.size == 0:
        return ""

    cmap = build_column_label_map(selected_columns)
    lista_items = "\n".join(f"- {cmap[c]}" for c in selected_columns)
    frag = _leading_common_fragment(selected_columns)
    bbrk = frag.rfind("[")
    frag_show = frag[:bbrk].strip() if bbrk > 40 else frag

    bloque_ctx = (
        f"Este es un **conjunto factorial exploratorio**: **{len(selected_columns)} preguntas** Likert marcadas simultáneamente en el selector. "
    )
    if len(frag_show) >= 42:
        bloque_ctx += (
            "Comparten formulación inicial similar del formulario (reflejo habitual de «matrices» tipo Google Forms), "
            f"por ejemplo cuando todas arrancan: «{_trunc(frag_show, 150)}». "
            "Debajo aparece cómo cada subítem aparece etiquetado en la interfaz:"
        )
    else:
        bloque_ctx += "Las formulaciones pueden ser heterogéneas; listamos los textos diferenciadores que muestra la app:"
    bloque_ctx += f"\n\n{lista_items}\n\nTotal de personas con respuestas **completas** en estos ítems: **{int(n_obs)}**."

    pca_intro = (
        f"\n\n### ¿Qué aporta el PCA ({pca_engine_description})?\n\n"
        f"Las componentes ordenan combinaciones que **maximizan varianza** en datos correlacionados. "
        f"Tu **primera componente** explica aproximadamente **{100 * float(vr[0]):.1f}%** de la dispersión estándar del bloque"
    )
    if vr.size >= 2:
        pca_intro += f"; junto con la segunda suman **{100 * float(vr[0] + vr[1]):.1f}%**"
    pca_intro += "."
    pc1_txt = _pc1_paragraph_academic(loadings_pca, row_labels_matrix_index)
    pca_intro += "\n\n" + pc1_txt if pc1_txt else ""

    if loadings_efa is None:
        tails = (
            "\n\n### Límites formales para publicación\n\n"
            "- Esta lectura sirve como **primer paso técnico**; no equivale todavía a un modelo de ecuaciones estructurales confirmatorio.\n"
            "- Los ítems se tratan como **continua ordinalizada** mediante la rutina previa.\n\n"
            "Si necesitás texto para marco estadístico, citá método explícito (**PCA**) y tamaño muestral antes de extrapolar causalidad."
        )
        return "### Lectura académica exploratoria (referida al mismo bloque seleccionado)\n\n" + bloque_ctx + pca_intro + tails

    kaiser_txt = ""
    if eig is not None and eig[0] is not None:
        ev = np.asarray(eig[0]).ravel()
        if ev.size >= 1:
            kaiser_txt = (
                f"\n\n### ¿Qué sugiere el patrón de autovalores (antes de etiquetar factores sociológicos)?\n\n"
                f"- Primer valor propio habitual del motor factorial: **{ev[0]:.2f}**."
            )
            if ev.size >= 2:
                kaiser_txt += f"\n- Segundo: **{ev[1]:.2f}**."
                if ev.size >= 3:
                    kaiser_txt += f" Tercero: **{ev[2]:.2f}**…"
            above1 = int(np.sum(ev >= 1.0))
            nf = int(n_factors_requested)
            if above1 <= 1 and nf >= 3:
                kaiser_txt += (
                    "\n\nCon la **regla Kaiser** habitual (solo heurística cuando la muestra crece)"
                    ", muchos revisores observan pocas razones estadísticas fuertes para **tres o más dimensiones nuevas**, "
                    f"cuando apenas **uno** autovalor queda típicamente sobre 1. Aquí solicitaste **{nf}** factores: "
                    "podés hacerlo exploratoriamente pero **nombre semánticos** («dimensión A/B») deberían sostenerse con teoría o CFA posterior."
                )
            elif above1 >= nf >= 2:
                kaiser_txt += (
                    f"\n\nAparecen **{above1}** raíces ≥1 ⇒ el número factorial exploratorio plausible podría alinearse mejor con ese conteo estadístico, "
                    f"compatibilizándolo después con **{efa_engine_description}**."
                )
            else:
                kaiser_txt += (
                    "\n\nEl primer autovalor domina ⇒ la mayor parte de correlaciones comparte un denominador estadístico común antes de subdividir ejes posteriores."
                )

    efa_body = (
        f"\n\n### Lectura cualitativa de los factores rotados (**{efa_engine_description}**)\n\n"
        "**Varimax** favorece interpretabilidad porque intenta producir pocas cargas fuertes y muchas cercanas a cero dentro de cada columna factorial, "
        "asumiendo ejes estadísticos **sin correlacionar entre sí** después de rotar."
        "\n\n"
        "**Síntesis por factor (solo con base en tus datos y las etiquetas de las preguntas):**\n\n"
        + _efa_factor_paragraph(loadings_efa, row_labels_matrix_index)
        + (
            "\n\nEn artículos suelen describir estos grupos como **facetas instrumentales distintas dentro del mismo objeto de preguntamiento**. "
            "Es decir: no probaste todavía un modelo bifactorial confirmatorio pero ya podés caracterizar cómo tus encuestados **coactivan correlativamente "
            "las alternativas** listadas tras el encabezado común del formulario."
        )
        + ("\n\n" + kaiser_txt if kaiser_txt else "")
    )

    disclaim = (
        "\n\n### Deberías documentar después en un trabajo académico\n\n"
        "- Especificación **EFA vs CFA** explícita, estimador (factores continuos ordinarios vs modelo de respuesta categorial / WLSMV). \n"
        "- Que esto es una **captura estadística dentro de esta app**, no equivalencia causal de «dimensiones percibidas».\n\n"
        "Si estos ítems miden prácticas con IA declaradas como similares textualmente pero distintos subítems, recordá mencionarlo antes de extrapolar comportamiento real más allá de la declaración autopercibida del cuestionario."
    )

    return (
        "### Lectura académica exploratoria (referida al mismo bloque seleccionado)\n\n"
        + bloque_ctx
        + pca_intro
        + efa_body
        + disclaim
    )


def clustering_explanatory(
    mode: str,
    *,
    k: int | None = None,
    inertia: float | None = None,
    vc: pd.DataFrame | None = None,
    noise_rate: float | None = None,
    n_feats: int = 2,
    n_obs: int = 0,
) -> str:
    if mode == "K-means":
        vc_txt = ""
        if vc is not None and not vc.empty and "n" in vc.columns:
            sizes = vc["n"].astype(int).tolist()
            imbalance = max(sizes) / max(min(sizes), 1)
            vc_txt = f" Tamaños de cluster **{sizes}**. "
            vc_txt += f"Índice bruto mayor/menor = **{imbalance:.1f}x** (**&lt;~3** suele leerse equilibrado en exploración rápida)."
        inert_txt = f" **Inercia** final **{inertia:,.0f}** (sólo comparable si variás k sobre la misma matriz)." if inertia else ""
        return (
            f"Segmentación **K-means** con **k = {int(k)}** sobre **{n_feats} rasgos codificados** y **{int(n_obs)}** filas usadas.{inert_txt}\n\n"
            f"{vc_txt}\n\nInterpretá centroides más altos/más bajos como **promedios de los escalares tras imputación con mediana**; "
            f"nombre de los segmentos (estudiante «heavy user», etc.) es **analítico**."
        )
    if mode == "DBSCAN":
        nr = noise_rate if noise_rate is not None else 0.0
        return (
            f"**DBSCAN** con **≥{int(n_feats)}** rasgos.\n\n"
            f"**{100*nr:.1f}%** de observaciones marcadas como ruido (cluster **‑1**) → valores altos sugieren dispersión grande o necesidad de ajustar **eps**/escala;\n\n"
            f"clusters denso‑conectados sin asumir formas convexas como k‑means."
        )
    return (
        "**Jerárquico:** sólo dendrograma de una **muestra aleatoria** (legibilidad). "
        "**No** extrapoles cortes óptimos al universo completo sin recalcular; usalo para intuir fusión/aglomeraciones."
    )


def predictive_explanatory(accuracy_tbl: pd.DataFrame, modelo_shap: str) -> str:
    if accuracy_tbl.empty:
        return ""
    best = accuracy_tbl.loc[accuracy_tbl["accuracy_val"].idxmax()]
    worst = accuracy_tbl.loc[accuracy_tbl["accuracy_val"].idxmin()]
    return (
        f"En validación codificada por la rutina interna (train/test reproducible),\n\n"
        f"- **Mayor accuracy** vista: **{best['modelo']}** (**{best['accuracy_val']:.3f}**).\n"
        f"- **Menor**: **{worst['modelo']}** (**{worst['accuracy_val']:.3f}**).\n\n"
        f"Gráfico **SHAP** con **{modelo_shap}** resume importancia direccional promedio "
        "(con las limitaciones conocidas sobre dependencia y tamaño muestral).\n\n"
        "**No** sustituye diseño muestral externo ni validación específica de tu protocolo institucional."
    )


def cfa_explanatory_short() -> str:
    return (
        "CFA de **un solo factor**: los coeficientes y métricas (si están) describen cómo ese factor explica correlaciones observadas tras **semopy**.\n\n"
        "Contrastá métricas de ajuste (χ² robusto, CFI/TLI, RMSEA, etc.) con umbrales de tu disciplina;"
        "\nUn factor único suele verse **parsimonioso** pero puede **no bastar** si hay subdimensiones teóricas claras."
    )
