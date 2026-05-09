"""
Análisis cuantitativo avanzado para datos de encuesta (ordenales, correlaciones inferenciales, etc.).
"""
from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats


def column_key_short(name: str, max_len: int = 64) -> str:
    return str(name).replace("\n", " ").strip()[:max_len]


def invert_ordinal_series(s: pd.Series) -> pd.Series:
    """
    Inverso dentro del rango observado por ítem: x' = mín + máx − x.
    Pensado para ítems Likert formulados en sentido contrario al resto del bloque.
    """
    out = s.astype(float).copy()
    m = out.notna()
    if not m.any():
        return out
    lo = float(out.loc[m].min())
    hi = float(out.loc[m].max())
    if hi <= lo:
        return out
    out.loc[m] = lo + hi - out.loc[m]
    return out


# --- Codificación ordinal (español, formularios Google típicos) ---

LIKERT_SCORE = {
    "totalmente en desacuerdo": 1,
    "en desacuerdo": 2,
    "ni de acuerdo ni en desacuerdo": 3,
    "ni de acuerdo ni desacuerdo": 3,
    "de acuerdo": 4,
    "totalmente de acuerdo": 5,
    "completamente de acuerdo": 5,
}

FREQ_SCORE = {
    "nunca": 1,
    "rara vez": 2,
    "a veces": 3,
    "frecuentemente": 4,
    "siempre": 5,
}


def normalize_text(x: Any) -> str:
    if pd.isna(x):
        return ""
    import re

    s = str(x).strip().lower()
    return re.sub(r"\s+", " ", s)


def series_to_likert_numeric(s: pd.Series) -> pd.Series:
    mapped = s.map(lambda v: LIKERT_SCORE.get(normalize_text(v)) if normalize_text(v) else np.nan)
    return pd.to_numeric(mapped, errors="coerce")


def series_to_freq_numeric(s: pd.Series) -> pd.Series:
    mapped = s.map(lambda v: FREQ_SCORE.get(normalize_text(v)) if normalize_text(v) else np.nan)
    return pd.to_numeric(mapped, errors="coerce")


def detect_best_ordinal(series: pd.Series, min_cover: float = 0.55) -> tuple[pd.Series, str]:
    """
    Intenta Likert → frecuencia. Retorna Serie numérica y etiqueta del esquema, o valores vacíos si no aplica.
    """
    lk = series_to_likert_numeric(series)
    fr = series_to_freq_numeric(series)
    lk_ok = lk.notna().mean()
    fr_ok = fr.notna().mean()
    if lk_ok >= min_cover and lk_ok >= fr_ok:
        return lk, "Likert"
    if fr_ok >= min_cover:
        return fr, "frecuencia"
    # intento menor umbral sólo Likert/Freq en competencia con ambos bajos
    if lk_ok >= 0.35 and lk_ok >= fr_ok:
        return lk, "Likert (parcial)"
    if fr_ok >= 0.35:
        return fr, "frecuencia (parcial)"
    return pd.Series([np.nan] * len(series), index=series.index), "no ordinal"


def descriptive_one_column(series: pd.Series, inverted: bool = False) -> dict[str, Any]:
    raw = series.dropna()
    vc = raw.astype(str).value_counts()
    total = vc.sum()
    pct = vc / total * 100 if total else vc * 0
    mode = vc.index[0] if len(vc) else ""
    coded, scheme = detect_best_ordinal(series)
    if inverted:
        coded = invert_ordinal_series(coded)
    valid_codes = coded.dropna()

    stats_block: dict[str, Any | None]
    if len(valid_codes) >= max(30, len(raw) * 0.3):
        stats_block = {
            "esquema_ordinal_inferido": scheme,
            "n_codificados": int(valid_codes.shape[0]),
            "media": float(valid_codes.mean()),
            "mediana": float(valid_codes.median()),
            "desv_std": float(valid_codes.std(ddof=1)) if len(valid_codes) > 1 else np.nan,
            "mínimo": float(valid_codes.min()),
            "máximo": float(valid_codes.max()),
        }
    else:
        stats_block = {
            "esquema_ordinal_inferido": None,
            "n_codificados": int(len(valid_codes)),
            "media": None,
            "mediana": None,
            "desv_std": None,
            "mínimo": None,
            "máximo": None,
        }

    return {
        "n": int(len(series)),
        "n_no_na": int(len(raw)),
        "n_categorías": int(raw.astype(str).nunique()),
        "moda_etiqueta": str(mode),
        **stats_block,
        "valor_counts": vc,
        "porcentajes": pct,
    }


def crosstab_chi_square(df: pd.DataFrame, row: str, col: str) -> dict[str, Any]:
    sub = df[[row, col]].dropna()
    tab = pd.crosstab(sub[row], sub[col])
    if tab.shape[0] < 2 or tab.shape[1] < 2:
        chi2, p, dof, expected = np.nan, np.nan, 0, None
        v = np.nan
    else:
        chi2, p, dof, expected = scipy_stats.chi2_contingency(tab)
        v = cramers_v_from_table(tab.values)
    return {
        "tabla": tab,
        "chi2": float(chi2) if chi2 == chi2 else np.nan,
        "gl": int(dof),
        "p_valor": float(p) if p == p else np.nan,
        "cramers_v": float(v) if v == v else np.nan,
        "n": len(sub),
    }


def cramers_v_from_table(table: np.ndarray) -> float:
    chi2 = scipy_stats.chi2_contingency(table)[0]
    n = np.sum(table)
    r, k = table.shape
    if n <= 0 or min(r, k) < 2:
        return float("nan")
    return np.sqrt(max(0, chi2) / (n * (min(r, k) - 1)))


def cronbach_alpha(matrix: pd.DataFrame) -> float:
    df = matrix.dropna(how="any")
    k = df.shape[1]
    if k < 2 or len(df) < 3:
        return float("nan")
    variances = df.var(axis=0, ddof=1).replace(0, np.nan).dropna().sum()
    row_sum = df.sum(axis=1)
    total_var = row_sum.var(ddof=1)
    if total_var == 0 or np.isnan(total_var):
        return float("nan")
    return float((k / (k - 1)) * (1 - variances / total_var))


@dataclass
class GroupComparisonResult:
    n_groups: int
    group_sizes: dict[str, int]
    anova_F: float | None
    anova_p: float | None
    kruskal_H: float | None
    kruskal_p: float | None
    t_stat: float | None
    t_p: float | None
    mw_U: float | None
    mw_p: float | None
    message: str | None


def compare_numeric_across_groups(
    y_numeric: pd.Series,
    groups: pd.Series,
) -> GroupComparisonResult:
    df = pd.DataFrame({"y": y_numeric, "g": groups}).dropna()
    df["g"] = df["g"].astype(str)
    uniq = sorted(df["g"].unique())

    sizes = {str(k): int(v) for k, v in df["g"].value_counts().items()}

    if len(uniq) < 2 or len(df) < 10:
        return GroupComparisonResult(
            len(uniq),
            sizes,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "Se necesitan al menos 2 grupos y suficientes casos válidos.",
        )

    subsets = [df.loc[df["g"] == g, "y"].values for g in uniq]

    if len(uniq) == 2:
        a, b = subsets[0], subsets[1]
        if len(a) < 3 or len(b) < 3:
            return GroupComparisonResult(
                len(uniq),
                sizes,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                "Cada grupo requiere al menos 3 observaciones válidas.",
            )
        tt = scipy_stats.ttest_ind(a, b, equal_var=False)
        mw = scipy_stats.mannwhitneyu(a, b, alternative="two-sided")

        ao = scipy_stats.f_oneway(*subsets)
        kw = scipy_stats.kruskal(*subsets)

        return GroupComparisonResult(
            2,
            sizes,
            float(ao.statistic),
            float(ao.pvalue),
            float(kw.statistic),
            float(kw.pvalue),
            float(tt.statistic),
            float(tt.pvalue),
            float(mw.statistic),
            float(mw.pvalue),
            "t‑Student (Welch) compara sólo grupos cuando k=2; ANOVA/K‑W igualmente muestras referencia.",
        )

    ao = scipy_stats.f_oneway(*subsets)
    kw = scipy_stats.kruskal(*subsets)
    return GroupComparisonResult(
        len(uniq),
        sizes,
        float(ao.statistic),
        float(ao.pvalue),
        float(kw.statistic),
        float(kw.pvalue),
        None,
        None,
        None,
        None,
        "ANOVA y Kruskal‑Wallis (k grupos ≥ 3). Para k=2, preferí pestaña con dos niveles sólo.",
    )


def coerce_binary_target(series: pd.Series, positive_keywords: tuple[str, ...]) -> pd.Series:
    """Construye binaria rudimentaria: contiene cualquier keyword -> 1."""

    def _lbl(x):
        sx = normalize_text(x)
        if sx in {"", "nan"}:
            return np.nan
        return int(any(k in sx for k in positive_keywords))

    out = series.map(_lbl).astype(float)
    return out


def prepare_feature_matrix(
    df: pd.DataFrame,
    cols: list[str],
    max_dummy: int = 22,
    inverted_cols: set[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, str]]:
    """
    Produce matriz numérica: ordenales automáticas; baja cardinalidad con dummies.
    """
    inverted_cols = inverted_cols or set()
    explanations: dict[str, str] = {}
    mats: list[pd.DataFrame] = []
    for c in cols:
        s = df[c]
        coded, scheme = detect_best_ordinal(s, min_cover=0.42)
        if coded.notna().mean() >= 0.42:
            if c in inverted_cols:
                coded = invert_ordinal_series(coded)
            mats.append(pd.DataFrame({f"{c}__ord": coded}))
            explanations[c] = f"Ordinal inferido ({scheme})"
            continue
        u = s.dropna().astype(str).nunique()
        if u <= max_dummy:
            d = pd.get_dummies(s.astype(str), prefix=c.replace("\n", " ")[:48], dummy_na=False)
            mats.append(d)
            explanations[c] = f"Categórica one‑hot ({u} niveles)"
        else:
            explanations[c] = f"Omitida (alta cardinalidad: {u} niveles; reducila o ordinalizá)."
    if not mats:
        return pd.DataFrame(), explanations
    X = pd.concat(mats, axis=1)
    return X, explanations


def fit_predictive_suite(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.25,
    random_state: int = 42,
) -> tuple[dict[str, Any], np.ndarray]:
    """Entrena clasificadores (binario o multicase). Devuelve métricas y matriz concatenada."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import LabelEncoder
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier

    Xt = X.astype(float).copy()
    Xt = Xt.fillna(Xt.median(numeric_only=True))
    Xt = Xt.replace([np.inf, -np.inf], np.nan).fillna(0)
    y_clean = y.loc[X.index]
    mask = y_clean.notna()
    Xt = Xt.loc[mask].astype(float)
    yv = y_clean.loc[mask]
    enc = LabelEncoder()
    y_enc = enc.fit_transform(yv.astype(str))

    if len(np.unique(y_enc)) < 2:
        raise ValueError("La variable objetivo tiene una sola clase tras limpiar valores.")

    strat = y_enc if len(np.unique(y_enc)) >= 2 else None
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            Xt,
            y_enc,
            test_size=test_size,
            random_state=random_state,
            stratify=strat,
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            Xt,
            y_enc,
            test_size=test_size,
            random_state=random_state,
            stratify=None,
        )

    results: dict[str, Any] = {}

    clf_lr = Pipeline(
        [
            ("clf", LogisticRegression(max_iter=2000, random_state=random_state)),
        ]
    )
    clf_lr.fit(X_train, y_train)
    y_pred = clf_lr.predict(X_test)
    results["Regresión logística"] = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "model": clf_lr,
        "features": Xt.columns.to_list(),
        "encoder": enc,
        "X_test": X_test,
        "y_test": y_test,
    }
    dt = DecisionTreeClassifier(max_depth=6, random_state=random_state, min_samples_leaf=5)
    dt.fit(X_train, y_train)
    y_pd = dt.predict(X_test)
    results["Árbol de decisión"] = {
        "accuracy": float(accuracy_score(y_test, y_pd)),
        "model": dt,
        "features": Xt.columns.to_list(),
        "encoder": enc,
        "X_test": X_test,
        "y_test": y_test,
    }

    rf = RandomForestClassifier(
        n_estimators=240,
        max_depth=14,
        min_samples_leaf=3,
        random_state=random_state,
        class_weight="balanced_subsample",
    )
    rf.fit(X_train, y_train)
    y_pr = rf.predict(X_test)
    results["Random Forest"] = {
        "accuracy": float(accuracy_score(y_test, y_pr)),
        "model": rf,
        "features": Xt.columns.to_list(),
        "encoder": enc,
        "X_test": X_test,
        "y_test": y_test,
    }

    try:
        from xgboost import XGBClassifier

        kwargs = dict(
            n_estimators=200,
            learning_rate=0.08,
            max_depth=5,
            random_state=random_state,
            verbosity=0,
            eval_metric="mlogloss" if len(np.unique(y_enc)) > 2 else "logloss",
        )
        if len(np.unique(y_enc)) <= 100:
            xgb_model = XGBClassifier(**kwargs)
            xgb_model.fit(X_train, y_train)
            y_px = xgb_model.predict(X_test)
            results["XGBoost"] = {
                "accuracy": float(accuracy_score(y_test, y_px)),
                "model": xgb_model,
                "features": Xt.columns.to_list(),
                "encoder": enc,
                "X_test": X_test,
                "y_test": y_test,
            }
    except ImportError:
        pass

    return results, Xt.values


def shap_summary_figure(model: Any, X_sample: pd.DataFrame, multiclass_class: int | None = None):
    import matplotlib.pyplot as plt
    import shap

    plt.ioff()

    if hasattr(model, "named_steps"):
        clf = model.named_steps.get("clf", model.steps[-1][1])
    else:
        clf = model

    if "RandomForestClassifier" == clf.__class__.__name__ or "XGB" in clf.__class__.__name__ or "DecisionTree" == clf.__class__.__name__:
        expl = shap.TreeExplainer(clf)
        vals = expl.shap_values(X_sample)
        fig = plt.figure(figsize=(9, 5))
        if isinstance(vals, list):
            ix = multiclass_class or 0
            shap.summary_plot(vals[ix], X_sample, plot_type="bar", max_display=min(24, X_sample.shape[1]), show=False)
        else:
            shap.summary_plot(vals, X_sample, plot_type="bar", max_display=min(24, X_sample.shape[1]), show=False)
        plt.tight_layout()
        return fig

    bg = X_sample.iloc[: max(60, len(X_sample) // 5)]
    expl = shap.LinearExplainer(clf, bg)
    shap_vals = expl.shap_values(X_sample)
    fig = plt.figure(figsize=(9, 5))
    if isinstance(shap_vals, list):
        ix = multiclass_class or 0
        shap.summary_plot(shap_vals[ix], X_sample, plot_type="bar", max_display=min(24, X_sample.shape[1]), show=False)
    else:
        shap.summary_plot(shap_vals, X_sample, plot_type="bar", max_display=min(24, X_sample.shape[1]), show=False)
    plt.tight_layout()
    return fig


def run_pca_with_loadings(X: pd.DataFrame, n_components: int):
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    Xc = StandardScaler().fit_transform(X.fillna(X.mean()))
    pc = PCA(n_components=n_components, random_state=42)
    Z = pc.fit_transform(Xc)
    loadings = pd.DataFrame(
        pc.components_.T,
        index=X.columns,
        columns=[f"PC{i + 1}" for i in range(pc.n_components_)],
    )
    var = pc.explained_variance_ratio_
    return Z, loadings, var


def polychoric_correlation_matrix(dat: pd.DataFrame, nearest: bool = True) -> pd.DataFrame:
    """
    Correlaciones policóricas pareadas (ordinal vs ordinal).
    Pasamos ndarray + índices de columna porque `hetcor(DataFrame)` de semopy transpone mal los nombres.
    """
    from semopy.polycorr import hetcor

    clean = dat.dropna(how="any").astype(float)
    n, p = clean.shape
    if n < max(35, p + 8):
        raise ValueError(
            "Pocas observaciones para correlaciones policóricas estables "
            "(sugerimos al menos más filas que columnas + margen)."
        )
    vals = np.ascontiguousarray(clean.values, dtype=float)
    p = vals.shape[1]
    colnames = clean.columns.to_list()
    ords_full = set(range(p))
    cor_out = hetcor(vals, ords=ords_full, nearest=nearest)
    if isinstance(cor_out, pd.DataFrame):
        cor_out = cor_out.astype(float).copy()
        cor_out.columns = colnames[: cor_out.shape[1]]
        cor_out.index = colnames[: cor_out.shape[0]]
        return cor_out
    arr = np.asarray(cor_out, dtype=float)
    return pd.DataFrame(arr, index=colnames, columns=colnames)


def pca_loadings_from_correlation_matrix(
    corr_df: pd.DataFrame, n_components: int
) -> tuple[pd.DataFrame, np.ndarray]:
    """
    PCA vía eigendecomposition de la matriz de correlación (cargas = autovectores * sqrt(autovalor)).
    """
    R = np.asarray(corr_df.values, dtype=float)
    eigvals, eigvecs = np.linalg.eigh(R)
    eigvals = np.asarray(np.real_if_close(eigvals, tol=400), dtype=float)
    eigvecs = eigvecs.real
    ix = np.argsort(eigvals)[::-1]
    eigvals = eigvals[ix]
    eigvecs = eigvecs[:, ix]
    tot = eigvals.clip(min=1e-15).sum()
    nc = max(1, min(int(n_components), R.shape[0]))
    vals = eigvals[:nc]
    vecs = eigvecs[:, :nc]
    loadings_mat = vecs * np.sqrt(np.maximum(vals, 0.0))
    loadings = pd.DataFrame(
        loadings_mat,
        index=corr_df.index,
        columns=[f"PC{i + 1}" for i in range(nc)],
    )
    variance_ratio = vals / tot
    return loadings, variance_ratio


def run_efa_from_correlation_matrix(
    corr_df: pd.DataFrame, n_factors: int, rotation: str = "varimax"
) -> tuple[pd.DataFrame, Any]:
    from factor_analyzer import FactorAnalyzer

    p = corr_df.shape[0]
    nf = max(2, min(int(n_factors), p - 1))
    Rvals = corr_df.values.astype(float)
    try:
        fa = FactorAnalyzer(n_factors=nf, rotation=rotation, method="minres", is_corr_matrix=True)
        fa.fit(Rvals)
    except Exception:
        fa = FactorAnalyzer(n_factors=nf, rotation=rotation, method="principal", is_corr_matrix=True)
        fa.fit(Rvals)
    loadings = pd.DataFrame(
        fa.loadings_,
        index=corr_df.columns,
        columns=[f"F{i + 1}" for i in range(nf)],
    )
    eig = getattr(fa, "get_eigenvalues", lambda: (None, None))()
    return loadings, eig


def run_efa(df: pd.DataFrame, n_factors: int, rotation: str = "varimax"):
    from factor_analyzer import FactorAnalyzer
    from sklearn.preprocessing import StandardScaler

    Xm = df.dropna(axis=0, how="any")
    if len(Xm) < max(n_factors + 50, df.shape[1] + 60):
        raise ValueError("Pocos casos completos para AFE estable.")
    zs = pd.DataFrame(StandardScaler().fit_transform(Xm.fillna(Xm.mean())), columns=Xm.columns, index=Xm.index)
    fa = FactorAnalyzer(n_factors=n_factors, rotation=rotation, method="principal")
    fa.fit(zs)
    loadings = pd.DataFrame(
        fa.loadings_,
        index=zs.columns,
        columns=[f"F{i + 1}" for i in range(n_factors)],
    )
    eig = getattr(fa, "get_eigenvalues", lambda: (None, None))()
    return loadings, eig, zs


def kmeans_profiles(Xs: pd.DataFrame, k: int, random_state: int = 42):
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    sc = StandardScaler()
    Zw = pd.DataFrame(sc.fit_transform(Xs.fillna(Xs.mean())), index=Xs.index, columns=Xs.columns)
    km = KMeans(n_clusters=k, n_init="auto", random_state=random_state)
    lbl = pd.Series(km.fit_predict(Zw), index=Xs.index, name="cluster")
    centers = pd.DataFrame(sc.inverse_transform(km.cluster_centers_), columns=Xs.columns)
    return lbl, centers, km.inertia_, Zw


def dbscan_profiles(Xs: pd.DataFrame, eps: float, min_samples: int):
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler

    sc = StandardScaler()
    Zw = sc.fit_transform(Xs.fillna(Xs.mean()))
    db = DBSCAN(eps=float(eps), min_samples=int(min_samples))
    lbl = pd.Series(db.fit_predict(Zw), index=Xs.index, name="cluster")
    noise_rate = float((lbl == -1).mean())
    return lbl, noise_rate, Zw


def hierarchical_linkage_plot(Xs: pd.DataFrame):
    """Dendrograma (submuestra ≤ 80 filas recomendadas)."""
    import matplotlib.pyplot as plt
    from scipy.cluster.hierarchy import dendrogram, linkage
    from sklearn.preprocessing import StandardScaler

    plt.ioff()
    Zs = pd.DataFrame(
        StandardScaler().fit_transform(Xs.fillna(Xs.mean())),
        index=Xs.index,
        columns=Xs.columns,
    )
    lk = linkage(Zs.values, method="ward")
    fig, ax = plt.subplots(figsize=(10, 4))
    dendrogram(lk, ax=ax)
    plt.tight_layout()
    return fig


def optional_sem_estimate(
    df: pd.DataFrame,
    latent_name: str,
    items: list[str],
    inverted_cols: set[str] | None = None,
) -> tuple[Any | None, pd.DataFrame, str | None]:
    """CFA de un factor (semopy): `Latente =~ i1+i2+i3`."""
    try:
        from semopy import Model
    except ImportError:
        return None, pd.DataFrame(), "Instalá semopy (`pip install semopy`) para CFA básico en Python."

    inverted_cols = inverted_cols or set()
    work = pd.DataFrame(index=df.index)
    colnames: dict[str, str] = {}
    for j, raw in enumerate(items):
        key = f"i{j + 1}"
        colnames[key] = raw[:120].replace("\n", " ")
        s = df[raw].copy()
        coded, _ = detect_best_ordinal(s, min_cover=0.30)
        if coded.notna().mean() < 0.30:
            work[key] = pd.factorize(s.astype(str))[0].astype(float)
        else:
            work[key] = coded
        if raw in inverted_cols:
            work[key] = invert_ordinal_series(work[key])
    work = work.astype(float).dropna()
    latent = "".join(ch for ch in latent_name.strip() if ch.isalnum() or ch == "_")
    if not latent or latent[0].isdigit():
        latent = "Latente"

    rhs = "+".join(colnames.keys())
    spec = f"{latent} =~ {rhs}"
    model = Model(spec)
    try:
        model.fit(work)
        return model, work.rename(columns=colnames), None
    except Exception as exc:
        return None, work.rename(columns=colnames), str(exc)


def filter_dataframe_comparison(
    df: pd.DataFrame,
    strata_col: str | None,
    strata_values,
    date_col: str | None,
    date_from,
    date_to,
) -> pd.DataFrame:
    """Submuestras para análisis comparativo (cohortes / filtros)."""
    out = df.copy()
    if strata_col and strata_values:
        out = out[out[strata_col].astype(str).isin(list(strata_values))]
    if date_col and date_col in out.columns and (date_from or date_to):
        ts = pd.to_datetime(out[date_col], errors="coerce")
        mask = ts.notna()
        if date_from:
            mask &= ts >= pd.Timestamp(date_from)
        if date_to:
            mask &= ts <= pd.Timestamp(date_to)
        out = out.loc[mask.fillna(False)]
    return out


def likert_numeric_matrix(
    df: pd.DataFrame,
    cols: list[str],
    inverted_cols: set[str] | None = None,
) -> pd.DataFrame:
    inverted_cols = inverted_cols or set()
    pieces: dict[str, pd.Series] = {}
    for c in cols:
        code, scheme = detect_best_ordinal(df[c], min_cover=0.28)
        if scheme.startswith("no"):
            num_try = pd.to_numeric(df[c], errors="coerce")
            if num_try.dropna().between(1, 7).mean() >= 0.85:
                code = num_try
            else:
                code = series_to_likert_numeric(df[c])
        if c in inverted_cols:
            code = invert_ordinal_series(code)
        pieces[column_key_short(c)] = code
    return pd.DataFrame(pieces)


def sanitize_lavaan_variable_names(columns: list[str]) -> list[str]:
    used = set()
    names_out: list[str] = []
    for i, raw in enumerate(columns):
        slug = re.sub(r"\W+", "_", column_key_short(str(raw), 96), flags=re.UNICODE).strip("_")
        slug = slug or f"v{i + 1}"
        if slug and slug[0].isdigit():
            slug = f"v_{slug}"
        cand = slug
        suf = 0
        while cand in used:
            suf += 1
            cand = f"{slug}_{suf}"
        used.add(cand)
        names_out.append(cand)
    return names_out


def relabel_corr_for_export(corr_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    lavaan_cols = sanitize_lavaan_variable_names([str(c) for c in corr_df.columns])
    rel = corr_df.astype(float).copy()
    rel.index = lavaan_cols
    rel.columns = lavaan_cols
    return rel, lavaan_cols


def lavaan_export_snippet(latent_name: str, var_names: list[str], sample_nobs: int) -> str:
    latent = "".join(ch for ch in latent_name.strip() if ch.isalnum() or ch == "_").strip("_") or "F1"
    if latent and latent[0].isdigit():
        latent = f"_{latent}"
    meas = " + ".join(var_names[:50])
    return textwrap.dedent(
        f"""
        library(lavaan)
        S <- as.matrix(read.csv("cor_poly.csv", row.names = 1, check.names = FALSE))

        model <- '
          {latent} =~ {meas}
        '
        fit <- cfa(model, sample.cov = S, sample.nobs = {int(sample_nobs)}, std.lv = TRUE)
        summary(fit, fit.measures = TRUE, standardized = TRUE)

        ## Si tratás ítems como ordenados categóricos, mejor flujo ordered= + WLSE / WLSMV.
        ## Consultá tu protocolo estadístico y guías de lavaan antes de cerrar inferencias finales.
        """
    ).strip()
